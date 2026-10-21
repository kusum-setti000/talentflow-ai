import pytest

from talentflow.candidates.scoring import (
    EvidenceMappingError,
    calculate_match_score,
    has_unverified_required_criteria,
)
from talentflow.domain.models import (
    CandidateAssessment,
    EvidenceMatch,
    JobAnalysis,
)


def make_job():
    return JobAnalysis(
        status="valid",
        title="Data Engineer",
        summary="Test role",
        required_skills=["5+ years experience", "SQL"],
        reason="Valid",
    )


def make_assessment(evidence):
    return CandidateAssessment(
        status="completed",
        match_score=50,
        experience_alignment="test",
        assessment_reasoning="test",
        evidence=evidence,
    )


def test_partial_mandatory_requirement_needs_review():
    job = make_job()
    assessment = make_assessment([
        EvidenceMatch(requirement="5+ years experience", status="partial"),
        EvidenceMatch(requirement="SQL", status="supported"),
    ])

    assert calculate_match_score(job, assessment) == 75
    assert has_unverified_required_criteria(job, assessment)


def test_all_supported_does_not_need_review():
    job = make_job()
    assessment = make_assessment([
        EvidenceMatch(requirement="5+ years experience", status="supported"),
        EvidenceMatch(requirement="SQL", status="supported"),
    ])

    assert calculate_match_score(job, assessment) == 100
    assert not has_unverified_required_criteria(job, assessment)


def test_missing_evidence_mapping_fails_safely():
    job = make_job()
    assessment = make_assessment([
        EvidenceMatch(requirement="SQL", status="supported"),
    ])

    with pytest.raises(EvidenceMappingError):
        calculate_match_score(job, assessment)


def test_paraphrased_evidence_mapping_fails_safely():
    job = make_job()
    assessment = make_assessment([
        EvidenceMatch(requirement="Five years of experience", status="partial"),
        EvidenceMatch(requirement="SQL", status="supported"),
    ])

    with pytest.raises(EvidenceMappingError):
        calculate_match_score(job, assessment)


def test_duplicate_evidence_fails_safely():
    job = make_job()
    assessment = make_assessment([
        EvidenceMatch(requirement="SQL", status="supported"),
        EvidenceMatch(requirement="SQL", status="supported"),
    ])

    with pytest.raises(EvidenceMappingError):
        calculate_match_score(job, assessment)
