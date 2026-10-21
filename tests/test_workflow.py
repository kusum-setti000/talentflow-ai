from talentflow.domain.models import JobAnalysis, DocumentAnalysis, CandidateAssessment
from talentflow.screening.graph import build_screening_workflow


class JobStub:
    def analyze(self, text):
        return JobAnalysis(status="valid", title="Engineer", summary="Engineering role", required_skills=["Python"], reason="Clear")


class DocumentStub:
    def __init__(self, status):
        self.status = status
    def classify(self, text):
        return DocumentAnalysis(status=self.status, document_type="resume" if self.status == "valid_resume" else "business card", summary="test", reason="test")


class AssessorStub:
    def __init__(self):
        self.calls = 0
    def assess(self, job, resume):
        self.calls += 1
        return CandidateAssessment(status="completed", match_score=30, experience_alignment="limited", assessment_reasoning="test")


def test_invalid_document_never_reaches_assessor():
    assessor = AssessorStub()
    graph = build_screening_workflow(JobStub(), DocumentStub("not_resume"), assessor)
    result = graph.invoke({"job_text": "Engineer", "resume_text": "Business card"})
    assert "assessment" not in result
    assert assessor.calls == 0


def test_valid_resume_is_assessed():
    assessor = AssessorStub()
    graph = build_screening_workflow(JobStub(), DocumentStub("valid_resume"), assessor)
    result = graph.invoke({"job_text": "Engineer", "resume_text": "Python projects"})
    assert result["assessment"].match_score == 30
    assert assessor.calls == 1
