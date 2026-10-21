from talentflow.candidates.scoring import calculate_match_score
from talentflow.domain.models import (
    JobAnalysis,
    CandidateAssessment,
    EvidenceMatch,
)


def make_job(requirements):
    return JobAnalysis(
        status="valid",
        title="Test Engineer",
        summary="Test role",
        required_skills=requirements,
        reason="Valid",
    )


def make_assessment(evidence):
    return CandidateAssessment(
        status="completed",
        match_score=99,
        experience_alignment="test",
        assessment_reasoning="test",
        evidence=evidence,
    )


def test_all_supported_scores_100():
    job = make_job(["Python", "SQL"])
    assessment = make_assessment([
        EvidenceMatch(requirement="Python", status="supported"),
        EvidenceMatch(requirement="SQL", status="supported"),
    ])
    assert calculate_match_score(job, assessment) == 100


def test_all_missing_scores_zero():
    job = make_job(["Python", "SQL"])
    assessment = make_assessment([
        EvidenceMatch(requirement="Python", status="not_found"),
        EvidenceMatch(requirement="SQL", status="not_found"),
    ])
    assert calculate_match_score(job, assessment) == 0


def test_partial_experience_scores_88():
    job = make_job([
        "5+ years of professional data engineering experience",
        "SQL",
        "Apache Spark",
        "Production ETL pipeline development",
    ])
    assessment = make_assessment([
        EvidenceMatch(
            requirement="5+ years of professional data engineering experience",
            status="partial",
        ),
        EvidenceMatch(requirement="SQL", status="supported"),
        EvidenceMatch(requirement="Apache Spark", status="supported"),
        EvidenceMatch(
            requirement="Production ETL pipeline development",
            status="supported",
        ),
    ])
    assert calculate_match_score(job, assessment) == 88


def test_score_is_repeatable():
    job = make_job(["AWS", "Linux", "Kubernetes", "Terraform"])
    assessment = make_assessment([
        EvidenceMatch(requirement="AWS", status="supported"),
        EvidenceMatch(requirement="Linux", status="supported"),
        EvidenceMatch(requirement="Kubernetes", status="not_found"),
        EvidenceMatch(requirement="Terraform", status="not_found"),
    ])
    scores = [calculate_match_score(job, assessment) for _ in range(10)]
    assert scores == [50] * 10
