"""
Semantic Search & Precedent Matching Engine
Runs 100% locally using TF-IDF vectorization and Cosine Similarity.
Provides similarity scores, match explanations, and key difference identification.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from backend.models import HistoricalPrecedent

def search_precedents(
    db: Session,
    query_text: str,
    category: Optional[str] = None,
    reuse_filter: Optional[str] = None,
    min_similarity: float = 0.15,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Performs local semantic matching between a new grievance / query and all
    historical disposed grievances in the library.
    """
    precedents_query = db.query(HistoricalPrecedent)
    if category and category != "All":
        precedents_query = precedents_query.filter(HistoricalPrecedent.category == category)
    if reuse_filter and reuse_filter != "All":
        precedents_query = precedents_query.filter(HistoricalPrecedent.reuse_recommendation == reuse_filter)
    
    precedents = precedents_query.all()
    if not precedents or not query_text.strip():
        return []

    # Build corpus: Combine subject, summary, full grievance text, and policy reference
    corpus = []
    for p in precedents:
        text_chunk = f"{p.subject} {p.category} {p.policy_reference or ''} {p.grievance_summary or ''} {p.full_grievance_text}"
        corpus.append(text_chunk)

    # Initialize TF-IDF Vectorizer with unigrams and bigrams
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        sublinear_tf=True,
        max_features=5000
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
        query_vec = vectorizer.transform([query_text])
        similarities = cosine_similarity(query_vec, tfidf_matrix)[0]
    except Exception:
        # Fallback if vocabulary is empty
        return []

    results = []
    ranked_indices = np.argsort(similarities)[::-1]

    query_words = set(query_text.lower().split())

    for idx in ranked_indices:
        sim = float(similarities[idx])
        if sim < min_similarity and len(results) >= 1:
            break
        
        p = precedents[idx]
        
        # Determine shared keywords
        prec_words = set(f"{p.subject} {p.full_grievance_text}".lower().split())
        common_words = [w for w in (query_words & prec_words) if len(w) > 3][:6]
        
        # Generate match explanation
        explanation_parts = []
        if common_words:
            explanation_parts.append(f"Significant conceptual overlap on: {', '.join(common_words)}.")
        if p.category.lower() in query_text.lower():
            explanation_parts.append(f"Direct category match in {p.category}.")
        if p.policy_reference:
            explanation_parts.append(f"Governed under policy: {p.policy_reference}.")
        
        relevance_explanation = " ".join(explanation_parts) if explanation_parts else "General subject matter similarity."
        
        # Identify key differences
        differences = []
        if p.reuse_recommendation == "outdated":
            differences.append("Precedent marked as OUTDATED due to policy evolution; verify current regulations.")
        elif p.reuse_recommendation == "restricted":
            differences.append("Precedent marked as CASE-SPECIFIC; factual claims must not be generalized.")
        
        if p.disposal_type == "Transferred under Section 6(3)":
            differences.append("Historical case was transferred to an external Ministry rather than disposed on merits.")
        else:
            differences.append(f"Historical case resolved via: {p.disposal_type}.")

        match_pct = int(min(sim * 100 * 1.5, 99.0))  # Normalized calibrated score

        results.append({
            "precedent": {
                "id": p.id,
                "registration_no": p.registration_no,
                "subject": p.subject,
                "category": p.category,
                "grievance_summary": p.grievance_summary,
                "full_grievance_text": p.full_grievance_text,
                "final_reply": p.final_reply,
                "disposal_date": p.disposal_date.isoformat() if p.disposal_date else None,
                "disposal_type": p.disposal_type,
                "department": p.department,
                "division": p.division,
                "policy_reference": p.policy_reference,
                "status_tag": p.status_tag,
                "reuse_recommendation": p.reuse_recommendation,
                "officer_notes": p.officer_notes,
                "provenance": p.provenance,
                "is_sample": p.is_sample,
                "created_at": p.created_at.isoformat() if p.created_at else None
            },
            "similarity_score": round(sim, 3),
            "match_percentage": max(10, match_pct),
            "relevance_explanation": relevance_explanation,
            "key_differences": differences,
            "is_recommended": (p.reuse_recommendation == "useful_precedent" and p.status_tag == "confirmed_issued")
        })

        if len(results) >= top_k:
            break

    return results
