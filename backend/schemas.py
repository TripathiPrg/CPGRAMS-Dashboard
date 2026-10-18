"""
Pydantic Schemas for Request Validation and Response Serialization
"""

from datetime import datetime, date
from typing import List, Optional, Any
from pydantic import BaseModel, Field

# Grievance Schemas
class GrievanceBase(BaseModel):
    registration_no: str
    subject: str
    date_received: date
    applicant_name: Optional[str] = None
    applicant_contact: Optional[str] = None
    category: str = "AI & Emerging Technologies"
    concerned_ministry: str = "Ministry of Electronics and Information Technology"
    concerned_division: str = "AI & Emerging Technologies Division"
    grievance_text: str
    requested_relief: Optional[str] = None
    status: str = "New"
    recommended_action: Optional[str] = None
    priority: str = "Normal"
    target_disposal_date: Optional[date] = None
    is_sample: bool = False
    source_type: str = "portal_assisted"

class GrievanceCreate(GrievanceBase):
    pass

class GrievanceUpdate(BaseModel):
    subject: Optional[str] = None
    applicant_name: Optional[str] = None
    applicant_contact: Optional[str] = None
    category: Optional[str] = None
    concerned_division: Optional[str] = None
    grievance_text: Optional[str] = None
    requested_relief: Optional[str] = None
    status: Optional[str] = None
    recommended_action: Optional[str] = None
    priority: Optional[str] = None
    target_disposal_date: Optional[date] = None

class GrievanceResponse(GrievanceBase):
    id: int
    applicant_masked: Optional[str] = None
    source_filename: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Precedent Schemas
class PrecedentBase(BaseModel):
    registration_no: str
    subject: str
    category: str
    grievance_summary: Optional[str] = None
    full_grievance_text: str
    final_reply: str
    disposal_date: date
    disposal_type: str = "Closed with reply"
    department: str = "Ministry of Electronics and Information Technology"
    division: str = "AI & Emerging Technologies Division"
    policy_reference: Optional[str] = None
    status_tag: str = "confirmed_issued"
    reuse_recommendation: str = "useful_precedent"
    officer_notes: Optional[str] = None
    provenance: str = "Official CPGRAMS Export"
    is_sample: bool = False

class PrecedentCreate(PrecedentBase):
    pass

class PrecedentResponse(PrecedentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PrecedentSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    reuse_recommendation: Optional[str] = None
    min_similarity: float = 0.15
    limit: int = 5

class PrecedentMatchResult(BaseModel):
    precedent: PrecedentResponse
    similarity_score: float
    match_percentage: int
    relevance_explanation: str
    key_differences: List[str]
    is_recommended: bool

# Analysis Schemas
class GrievanceAnalysisResponse(BaseModel):
    id: int
    grievance_id: int
    summary: str
    main_allegations: Optional[str] = None
    exact_relief_requested: Optional[str] = None
    relevant_facts_dates: Optional[str] = None
    policy_jurisdiction_issues: Optional[str] = None
    submission_type: str
    concerned_entity: Optional[str] = None
    recommended_next_action: str
    confidence_level: str
    confidence_score: float
    missing_info_verification: Optional[str] = None
    requires_senior_review: bool
    senior_review_reason: Optional[str] = None
    is_manually_corrected: bool
    created_at: datetime

    class Config:
        from_attributes = True

class GrievanceAnalysisUpdate(BaseModel):
    summary: Optional[str] = None
    main_allegations: Optional[str] = None
    exact_relief_requested: Optional[str] = None
    relevant_facts_dates: Optional[str] = None
    policy_jurisdiction_issues: Optional[str] = None
    submission_type: Optional[str] = None
    concerned_entity: Optional[str] = None
    recommended_next_action: Optional[str] = None
    confidence_level: Optional[str] = None
    requires_senior_review: Optional[bool] = None
    senior_review_reason: Optional[str] = None

# Reply Draft Schemas
class ReplyDraftBase(BaseModel):
    draft_type: str = "standard_disposal"
    template_used: Optional[str] = None
    selected_precedents: Optional[str] = None
    current_draft_text: str
    approval_status: str = "draft"
    approved_by: Optional[str] = None
    compliance_notes: Optional[str] = None

class ReplyDraftCreate(ReplyDraftBase):
    grievance_id: int
    original_draft_text: str

class ReplyDraftUpdate(BaseModel):
    current_draft_text: str
    approval_status: Optional[str] = None
    approved_by: Optional[str] = None
    compliance_notes: Optional[str] = None

class ReplyDraftResponse(ReplyDraftBase):
    id: int
    grievance_id: int
    version_number: int
    original_draft_text: str
    approval_timestamp: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Correspondence Schemas
class CorrespondenceBase(BaseModel):
    reference_no: str
    recipient_office: str
    date_sent: date = Field(default_factory=date.today)
    subject: str
    target_due_date: date
    status: str = "Sent"
    notes: Optional[str] = None

class CorrespondenceCreate(CorrespondenceBase):
    grievance_id: Optional[int] = None

class CorrespondenceUpdate(BaseModel):
    recipient_office: Optional[str] = None
    subject: Optional[str] = None
    target_due_date: Optional[date] = None
    status: Optional[str] = None
    date_received: Optional[date] = None
    response_summary: Optional[str] = None
    notes: Optional[str] = None

class CorrespondenceResponse(CorrespondenceBase):
    id: int
    grievance_id: Optional[int] = None
    follow_up_history: Optional[str] = None
    date_received: Optional[date] = None
    response_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Routing Rule Schemas
class RoutingRuleBase(BaseModel):
    rule_name: str
    keyword_triggers: str
    match_category: Optional[str] = None
    target_ministry: str = "Ministry of Electronics and Information Technology"
    target_division: str
    recommended_action: str
    explanation: str
    priority_order: int = 10
    is_active: bool = True

class RoutingRuleCreate(RoutingRuleBase):
    pass

class RoutingRuleResponse(RoutingRuleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Template Schemas
class ResponseTemplateBase(BaseModel):
    template_code: str
    title: str
    template_type: str
    concerned_division: str = "AI & Emerging Technologies Division"
    template_body: str
    placeholders: Optional[str] = None
    is_default: bool = False

class ResponseTemplateCreate(ResponseTemplateBase):
    pass

class ResponseTemplateResponse(ResponseTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Audit Log Schema
class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime
    event_type: str
    entity_type: str
    entity_id: Optional[str] = None
    details: str
    actor: str

    class Config:
        from_attributes = True

# Dashboard Stats Schema
class DashboardStats(BaseModel):
    total_grievances: int
    new_grievances: int
    pending_grievances: int
    disposed_grievances: int
    awaiting_inputs: int
    drafts_awaiting_review: int
    approaching_deadlines: int
    urgent_attention: int
    sample_records_count: int
    real_records_count: int
    last_sync_time: Optional[str] = None
    recent_activities: List[AuditLogResponse]
