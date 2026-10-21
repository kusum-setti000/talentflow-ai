"""Public contracts. UI and workflows depend on these types, not provider payloads."""
from enum import StrEnum
from typing import Literal
from pydantic import BaseModel, Field, model_validator, computed_field


class SourceKind(StrEnum):
    URL = "url"
    TEXT = "text"
    FILE = "file"


class ContentInput(BaseModel):
    kind: SourceKind
    text: str | None = None
    url: str | None = None
    filename: str | None = None
    file_bytes: bytes | None = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def check_source(self):
        if self.kind == SourceKind.TEXT and not (self.text or "").strip():
            raise ValueError("Paste non-empty text.")
        if self.kind == SourceKind.URL and not (self.url or "").strip():
            raise ValueError("Enter a job posting URL.")
        if self.kind == SourceKind.FILE and (not self.filename or not self.file_bytes):
            raise ValueError("Upload a PDF or DOCX file.")
        return self


class ScreeningRequest(BaseModel):
    job: ContentInput
    candidate: ContentInput


class ResolvedContent(BaseModel):
    text: str
    source: SourceKind
    label: str


class JobAnalysis(BaseModel):
    status: Literal["valid", "needs_review", "invalid"]
    title: str | None = None
    company: str | None = None
    summary: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    reason: str


class DocumentAnalysis(BaseModel):
    status: Literal["valid_resume", "insufficient_evidence", "not_resume", "needs_review"]
    document_type: str
    summary: str
    evidence_categories: list[str] = Field(default_factory=list)
    reason: str


class EvidenceMatch(BaseModel):
    requirement: str
    resume_evidence: str | None = None
    status: Literal["supported", "not_found", "partial"]


class CandidateAssessment(BaseModel):
    status: Literal["completed", "needs_review"]
    match_score: int | None = Field(default=None, ge=0, le=100)
    matching_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    candidate_strengths: list[str] = Field(default_factory=list)
    potential_gaps: list[str] = Field(default_factory=list)
    recruiter_questions: list[str] = Field(default_factory=list)
    experience_alignment: str
    assessment_reasoning: str
    evidence: list[EvidenceMatch] = Field(default_factory=list)

    @model_validator(mode="after")
    def score_matches_status(self):
        if (self.status == "completed") != (self.match_score is not None):
            raise ValueError("Completed assessments require a score; review assessments must not have one.")
        return self


class ScreeningResult(BaseModel):
    status: Literal["completed", "invalid_job", "invalid_document", "needs_review", "failed"]
    message: str
    job: JobAnalysis | None = None
    document: DocumentAnalysis | None = None
    assessment: CandidateAssessment | None = None

    @model_validator(mode="after")
    def check_outcome(self):
        if self.status == "completed" and (self.assessment is None or self.assessment.status != "completed"):
            raise ValueError("Completed screening requires a completed assessment.")
        if self.status != "completed" and self.assessment is not None and self.assessment.match_score is not None:
            raise ValueError("Unfinished screening cannot expose a score.")
        return self

    @computed_field
    @property
    def review_category(self) -> str:
        if self.status != "completed" or self.assessment is None:
            return "Needs Human Review"

        score = self.assessment.match_score
        if score is None or self.job is None:
            return "Needs Human Review"

        from talentflow.candidates.scoring import (
            EvidenceMappingError,
            has_unverified_required_criteria,
        )

        try:
            if has_unverified_required_criteria(self.job, self.assessment):
                return "Needs Human Review"
        except EvidenceMappingError:
            return "Needs Human Review"

        if score >= 85:
            return "Strong Match"
        if score >= 70:
            return "Potential Match"
        if score >= 50:
            return "Needs Human Review"
        return "Weak Match"

