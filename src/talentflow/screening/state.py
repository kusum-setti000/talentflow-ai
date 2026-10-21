from typing import TypedDict
from talentflow.domain.models import JobAnalysis, DocumentAnalysis, CandidateAssessment


class ScreeningState(TypedDict, total=False):
    job_text: str
    resume_text: str
    job_analysis: JobAnalysis
    document_analysis: DocumentAnalysis
    assessment: CandidateAssessment
