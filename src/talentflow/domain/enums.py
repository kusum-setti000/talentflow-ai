from enum import StrEnum


class JobInputMode(StrEnum):
    URL = "Job URL"
    TEXT = "Paste Text"


class ResumeInputMode(StrEnum):
    FILE = "PDF / DOCX"
    TEXT = "Paste Text"


class AssessmentBand(StrEnum):
    STRONG = "Strong Match"
    POTENTIAL = "Potential Match"
    REVIEW = "Needs Review"
    WEAK = "Weak Match"


class EvidenceStatus(StrEnum):
    SUPPORTED = "supported"
    PARTIAL = "partial"
    NOT_FOUND = "not_found"
