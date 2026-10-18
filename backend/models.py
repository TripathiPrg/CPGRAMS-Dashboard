"""
SQLAlchemy Models for CPGRAMS Personal Workbench
AI & Emerging Technologies Division, MeitY
"""

from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Boolean, Float, ForeignKey
)
from sqlalchemy.orm import relationship
from backend.database import Base

class Grievance(Base):
    __tablename__ = "grievances"

    id = Column(Integer, primary_key=True, index=True)
    registration_no = Column(String(100), unique=True, index=True, nullable=False)
    subject = Column(String(500), nullable=False)
    date_received = Column(Date, default=date.today, nullable=False)
    applicant_name = Column(String(200), nullable=True)
    applicant_masked = Column(String(200), nullable=True)
    applicant_contact = Column(String(200), nullable=True)
    
    category = Column(String(200), default="AI & Emerging Technologies", nullable=False)
    concerned_ministry = Column(String(250), default="Ministry of Electronics and Information Technology", nullable=False)
    concerned_division = Column(String(200), default="AI & Emerging Technologies Division", nullable=False)
    
    grievance_text = Column(Text, nullable=False)
    requested_relief = Column(Text, nullable=True)
    
    # Status: 'New', 'Under Examination', 'Awaiting Inputs', 'Draft Prepared', 'Approved for Disposal', 'Disposed'
    status = Column(String(50), default="New", index=True, nullable=False)
    recommended_action = Column(String(200), nullable=True)
    priority = Column(String(50), default="Normal", nullable=False)  # 'Urgent', 'High', 'Normal', 'Low'
    target_disposal_date = Column(Date, nullable=True)

    # 9-Stage Operational Workflow State:
    # 'Retrieved', 'Analysis complete', 'Draft generated', 'Awaiting review',
    # 'Approved for submission', 'Submission in progress', 'Official submission confirmed',
    # 'Submission failed', 'Status requires verification'
    workflow_state = Column(String(50), default="Retrieved", index=True, nullable=False)

    # Portal Submission & Verification Audit Fields
    # Strict rule: Never marked 'Disposed' or 'Official submission confirmed' without verified portal response
    portal_action_timestamp = Column(DateTime, nullable=True)
    portal_confirmation_id = Column(String(100), nullable=True)
    verification_status = Column(String(50), default="unverified", nullable=False)  # 'unverified', 'verified_by_portal', 'verification_failed', 'status_requires_verification'
    portal_reply_recorded = Column(Text, nullable=True)
    disposal_category = Column(String(100), nullable=True)
    disposal_remarks = Column(Text, nullable=True)
    
    # Audit & Provenance
    is_sample = Column(Boolean, default=False, nullable=False)  # Clearly labels synthetic test data
    source_type = Column(String(50), default="portal_assisted", nullable=False)  # 'portal_assisted', 'manual_upload', 'synthetic_test', 'excel_import'
    source_filename = Column(String(250), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    analyses = relationship("GrievanceAnalysis", back_populates="grievance", cascade="all, delete-orphan")
    drafts = relationship("ReplyDraft", back_populates="grievance", cascade="all, delete-orphan")
    correspondence = relationship("Correspondence", back_populates="grievance", cascade="all, delete-orphan")


class HistoricalPrecedent(Base):
    __tablename__ = "historical_precedents"

    id = Column(Integer, primary_key=True, index=True)
    registration_no = Column(String(100), unique=True, index=True, nullable=False)
    subject = Column(String(500), nullable=False)
    category = Column(String(200), nullable=False)
    grievance_summary = Column(Text, nullable=True)
    full_grievance_text = Column(Text, nullable=False)
    final_reply = Column(Text, nullable=False)
    disposal_date = Column(Date, nullable=False)
    disposal_type = Column(String(100), default="Closed with reply", nullable=False)
    
    department = Column(String(250), default="Ministry of Electronics and Information Technology", nullable=False)
    division = Column(String(200), default="AI & Emerging Technologies Division", nullable=False)
    policy_reference = Column(String(300), nullable=True)
    
    # Precedent validity tag
    # 1. 'confirmed_issued', 2. 'marked_approved', 3. 'draft_response', 4. 'status_unverified'
    status_tag = Column(String(50), default="confirmed_issued", nullable=False)
    
    # Officer Assessment for Reuse: 'useful_precedent', 'outdated', 'incorrect', 'restricted'
    reuse_recommendation = Column(String(50), default="useful_precedent", nullable=False)
    officer_notes = Column(Text, nullable=True)
    provenance = Column(String(250), default="Official CPGRAMS Export", nullable=False)
    is_sample = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class GrievanceAnalysis(Base):
    __tablename__ = "grievance_analyses"

    id = Column(Integer, primary_key=True, index=True)
    grievance_id = Column(Integer, ForeignKey("grievances.id"), nullable=False)
    
    summary = Column(Text, nullable=False)
    main_allegations = Column(Text, nullable=True)
    exact_relief_requested = Column(Text, nullable=True)
    relevant_facts_dates = Column(Text, nullable=True)
    policy_jurisdiction_issues = Column(Text, nullable=True)
    
    # Submission type: Grievance, Suggestion, Proposal, Representation, RTI Query, Outside Scope
    submission_type = Column(String(100), default="Grievance", nullable=False)
    concerned_entity = Column(String(250), nullable=True)
    recommended_next_action = Column(Text, nullable=False)
    
    confidence_level = Column(String(20), default="High", nullable=False)  # High, Medium, Low
    confidence_score = Column(Float, default=0.85, nullable=False)
    missing_info_verification = Column(Text, nullable=True)
    
    requires_senior_review = Column(Boolean, default=False, nullable=False)
    senior_review_reason = Column(Text, nullable=True)
    
    is_manually_corrected = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    grievance = relationship("Grievance", back_populates="analyses")


class ReplyDraft(Base):
    __tablename__ = "reply_drafts"

    id = Column(Integer, primary_key=True, index=True)
    grievance_id = Column(Integer, ForeignKey("grievances.id"), nullable=False)
    version_number = Column(Integer, default=1, nullable=False)
    
    # Draft types: 'standard_disposal', 'out_of_scope', 'transfer_referral', 'call_for_inputs', 'policy_explanation', 'representation_acknowledgement'
    draft_type = Column(String(100), default="standard_disposal", nullable=False)
    template_used = Column(String(200), nullable=True)
    selected_precedents = Column(Text, nullable=True)  # JSON string of precedent IDs
    
    original_draft_text = Column(Text, nullable=False)
    current_draft_text = Column(Text, nullable=False)
    
    # Approval status: 'draft', 'under_review', 'approved', 'issued_on_portal'
    approval_status = Column(String(50), default="draft", nullable=False)
    approved_by = Column(String(150), nullable=True)
    approval_timestamp = Column(DateTime, nullable=True)
    compliance_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    grievance = relationship("Grievance", back_populates="drafts")


class Correspondence(Base):
    __tablename__ = "correspondences"

    id = Column(Integer, primary_key=True, index=True)
    grievance_id = Column(Integer, ForeignKey("grievances.id"), nullable=True)
    reference_no = Column(String(100), index=True, nullable=False)
    recipient_office = Column(String(250), nullable=False)
    date_sent = Column(Date, default=date.today, nullable=False)
    subject = Column(String(500), nullable=False)
    target_due_date = Column(Date, nullable=False)
    
    # Status: 'Sent', 'Reminder Sent', 'Response Received', 'Overdue', 'Integrated'
    status = Column(String(50), default="Sent", index=True, nullable=False)
    follow_up_history = Column(Text, nullable=True)  # JSON log of reminders
    date_received = Column(Date, nullable=True)
    response_summary = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    grievance = relationship("Grievance", back_populates="correspondence")


class RoutingRule(Base):
    __tablename__ = "routing_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(200), nullable=False)
    keyword_triggers = Column(Text, nullable=False)  # Comma-separated keywords
    match_category = Column(String(150), nullable=True)
    target_ministry = Column(String(250), default="Ministry of Electronics and Information Technology", nullable=False)
    target_division = Column(String(200), nullable=False)
    recommended_action = Column(String(200), nullable=False)
    explanation = Column(Text, nullable=False)
    priority_order = Column(Integer, default=10, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ResponseTemplate(Base):
    __tablename__ = "response_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_code = Column(String(100), unique=True, nullable=False)
    title = Column(String(250), nullable=False)
    template_type = Column(String(100), nullable=False)
    concerned_division = Column(String(200), default="AI & Emerging Technologies Division", nullable=False)
    template_body = Column(Text, nullable=False)
    placeholders = Column(String(300), nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    event_type = Column(String(100), nullable=False)  # 'RECORD_IMPORT', 'RECORD_MODIFIED', 'DRAFT_GENERATED', etc.
    entity_type = Column(String(50), nullable=False)   # 'Grievance', 'Draft', 'Precedent', 'System'
    entity_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=False)
    actor = Column(String(150), default="Authorized Officer (MeitY AI & ET)", nullable=False)
