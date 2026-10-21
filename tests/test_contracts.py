import pytest
from pydantic import ValidationError
from talentflow.domain.models import CandidateAssessment, ScreeningResult


def test_completed_requires_assessment():
    with pytest.raises(ValidationError):
        ScreeningResult(status="completed", message="done")


def test_review_must_not_have_score():
    with pytest.raises(ValidationError):
        CandidateAssessment(status="needs_review", match_score=90, experience_alignment="unknown", assessment_reasoning="unclear")


def test_completed_score_can_be_zero():
    result = CandidateAssessment(status="completed", match_score=0, experience_alignment="no evidence", assessment_reasoning="unmatched")
    assert result.match_score == 0
