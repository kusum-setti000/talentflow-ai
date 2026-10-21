"""Dependency composition is isolated from business logic."""
from functools import lru_cache
from talentflow.config import get_settings
from talentflow.ingestion.service import ContentService
from talentflow.jobs.analyzer import JobAnalyzer
from talentflow.candidates.classifier import DocumentClassifier
from talentflow.candidates.assessor import CandidateAssessor
from talentflow.platform.llm import create_chat_model
from talentflow.screening.graph import build_screening_workflow
from talentflow.screening.service import ScreeningService


@lru_cache(maxsize=1)
def get_screening_service() -> ScreeningService:
    settings = get_settings()
    model = create_chat_model(settings)
    workflow = build_screening_workflow(JobAnalyzer(model), DocumentClassifier(model), CandidateAssessor(model))
    return ScreeningService(ContentService(settings), workflow)
