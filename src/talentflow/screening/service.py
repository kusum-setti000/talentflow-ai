"""The only screening entry point called by the UI."""
import logging
from talentflow.domain.errors import InputError, SourceUnavailable
from talentflow.domain.models import ScreeningRequest, ScreeningResult

logger = logging.getLogger(__name__)


class ScreeningService:
    def __init__(self, content_service, workflow):
        self.content_service = content_service
        self.workflow = workflow

    def screen(self, request: ScreeningRequest) -> ScreeningResult:
        try:
            job = self.content_service.resolve(request.job, allow_url=True)
        except SourceUnavailable:
            return ScreeningResult(status="invalid_job", message="Unable to access this job posting. Enter a direct job link or paste the complete job description and title.")
        except InputError as exc:
            return ScreeningResult(status="invalid_job", message=str(exc))
        try:
            candidate = self.content_service.resolve(request.candidate, allow_url=False)
        except InputError as exc:
            return ScreeningResult(status="invalid_document", message=str(exc))
        try:
            state = self.workflow.invoke({"job_text": job.text, "resume_text": candidate.text})
        except Exception:
            logger.exception("Screening workflow failed; raw document content is not logged")
            return ScreeningResult(status="failed", message="Analysis could not be completed. Please retry later.")
        job_analysis = state["job_analysis"]
        document_analysis = state["document_analysis"]
        if job_analysis.status != "valid":
            return ScreeningResult(status="invalid_job" if job_analysis.status == "invalid" else "needs_review",
                                   message="No clear job role or complete requirements found. Provide a direct job URL or paste the JD and title.",
                                   job=job_analysis, document=document_analysis)
        if document_analysis.status != "valid_resume":
            return ScreeningResult(status="invalid_document" if document_analysis.status != "needs_review" else "needs_review",
                                   message=document_analysis.reason, job=job_analysis, document=document_analysis)
        assessment = state.get("assessment")
        if assessment is None or assessment.status != "completed":
            return ScreeningResult(status="needs_review", message="Requirements are ambiguous; human review is required.",
                                   job=job_analysis, document=document_analysis, assessment=assessment)
        return ScreeningResult(status="completed", message="Screening completed. Review the evidence before making decisions.",
                               job=job_analysis, document=document_analysis, assessment=assessment)
