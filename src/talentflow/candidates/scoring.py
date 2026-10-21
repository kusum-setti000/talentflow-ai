"""Deterministic screening score with strict evidence mapping."""

from talentflow.domain.models import CandidateAssessment, JobAnalysis

CREDIT = {
    "supported": 1.0,
    "partial": 0.5,
    "not_found": 0.0,
}


class EvidenceMappingError(ValueError):
    """Required criteria cannot be mapped unambiguously."""


def _normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def validate_evidence_mapping(job: JobAnalysis, assessment: CandidateAssessment):
    requirements = job.required_skills

    if not requirements:
        raise EvidenceMappingError("No required criteria were extracted.")

    expected = [_normalize(value) for value in requirements]
    actual = [_normalize(item.requirement) for item in assessment.evidence]

    if len(expected) != len(set(expected)):
        raise EvidenceMappingError("Duplicate job requirements.")

    if len(actual) != len(set(actual)):
        raise EvidenceMappingError("Duplicate evidence records.")

    if set(expected) != set(actual):
        raise EvidenceMappingError(
            "Evidence does not map one-to-one to job requirements."
        )

    return {
        _normalize(item.requirement): item.status
        for item in assessment.evidence
    }


def calculate_match_score(
    job: JobAnalysis,
    assessment: CandidateAssessment,
) -> int:
    evidence = validate_evidence_mapping(job, assessment)

    total = sum(
        CREDIT[evidence[_normalize(requirement)]]
        for requirement in job.required_skills
    )

    return round(100 * total / len(job.required_skills))


def has_unverified_required_criteria(
    job: JobAnalysis,
    assessment: CandidateAssessment,
) -> bool:
    evidence = validate_evidence_mapping(job, assessment)

    return any(
        evidence[_normalize(requirement)] != "supported"
        for requirement in job.required_skills
    )
