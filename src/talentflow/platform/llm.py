"""Centralized LangChain model adapter. Services receive an injected model."""
from langchain_openai import ChatOpenAI
from talentflow.config import Settings


def create_chat_model(settings: Settings) -> ChatOpenAI:
    if settings.openai_api_key is None:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to your local .env file.")
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
        timeout=settings.openai_timeout,
        max_retries=settings.openai_max_retries,
    )
