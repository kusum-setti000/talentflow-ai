import hashlib
import logging

import streamlit as st

from talentflow.domain.enums import JobInputMode, ResumeInputMode
from talentflow.domain.errors import SourceUnavailable
from talentflow.domain.models import ContentInput, ScreeningRequest, SourceKind
from talentflow.ingestion.web import fetch_job_content
from ui.state import invalidate_result, reset_screening, revision_key

logger = logging.getLogger(__name__)



def _clean_job_description(text: str) -> str:
    import re

    text = re.sub(r"\s+", " ", text).strip()

    start = re.search(
        r"\bJob description\s*:",
        text,
        flags=re.IGNORECASE,
    )

    if start:
        text = text[start.end():].strip()

    end = re.search(
        r"\b(?:Show more Show less|Similar jobs|Similar Searches|People also viewed)\b",
        text,
        flags=re.IGNORECASE,
    )

    if end:
        text = text[:end.start()].strip()

    return text

def _job_url_changed():
    invalidate_result()

    st.session_state.pop("job_extracted", None)
    st.session_state.pop("job_error", None)
    st.session_state.pop("job_text", None)

    url = st.session_state.get("job_url", "").strip()

    if not url:
        return

    if not url.startswith(("https://", "http://")):
        st.session_state["job_error"] = "Enter a complete http:// or https:// URL."
        return

    try:
        with st.spinner("Extracting job description..."):
            content = _clean_job_description(fetch_job_content(url))

        if not content or not content.strip():
            raise SourceUnavailable("Empty job content")

        st.session_state["job_text"] = content
        st.session_state["job_extracted"] = url

    except Exception:
        logger.exception("Job extraction failed")
        st.session_state["job_error"] = (
            "Automatic extraction failed. Paste the job description below."
        )


def _input_changed():
    invalidate_result()
    st.session_state.pop("last_screening_signature", None)


def _job_mode_changed():
    _input_changed()


def _resume_mode_changed():
    _input_changed()


def render_job_input() -> ContentInput | None:
    st.markdown("#### Job Description")

    mode = st.radio(
        "Job source",
        options=list(JobInputMode),
        format_func=lambda value: value.value,
        horizontal=True,
        key="job_mode",
        on_change=_job_mode_changed,
        label_visibility="collapsed",
    )

    if mode == JobInputMode.TEXT:
        text = st.text_area(
            "Paste job description",
            key="job_text",
            height=200,
            placeholder="Paste the complete job description here...",
            on_change=_input_changed,
        )

        if text.strip():
            st.success("Job description ready")
            return ContentInput(kind=SourceKind.TEXT, text=text)

        return None

    url = st.text_input(
        "Job URL",
        key="job_url",
        placeholder="https://company.com/careers/...",
        on_change=_job_url_changed,
        help="Paste the URL and press Enter or click outside the field.",
    )

    extracted = st.session_state.get("job_extracted")
    error = st.session_state.get("job_error")

    if extracted == url.strip() and st.session_state.get("job_text", "").strip():
        st.success("Job description extracted successfully")

        with st.expander("View or edit extracted job description"):
            text = st.text_area(
                "Extracted description",
                key="job_text",
                height=200,
                on_change=_input_changed,
            )

        return ContentInput(
            kind=SourceKind.TEXT,
            text=st.session_state["job_text"],
        )

    if error:
        st.warning(error)

        text = st.text_area(
            "Paste job description",
            key="job_text",
            height=200,
            placeholder="Paste the job description here...",
            on_change=_input_changed,
        )

        if text.strip():
            return ContentInput(kind=SourceKind.TEXT, text=text)

    return None


def render_resume_input(job_ready: bool) -> ContentInput | None:
    st.markdown("#### Candidate Resume")

    if not job_ready:
        st.caption("Complete the job description first to unlock resume upload.")

    mode = st.radio(
        "Resume source",
        options=list(ResumeInputMode),
        format_func=lambda value: value.value,
        horizontal=True,
        key="resume_mode",
        on_change=_resume_mode_changed,
        label_visibility="collapsed",
        disabled=not job_ready,
    )

    if mode == ResumeInputMode.TEXT:
        text = st.text_area(
            "Paste resume",
            key="resume_text",
            height=200,
            placeholder="Paste candidate resume text...",
            on_change=_input_changed,
            disabled=not job_ready,
        )

        if job_ready and text.strip():
            st.success("Resume ready")
            return ContentInput(kind=SourceKind.TEXT, text=text)

        return None

    uploaded = st.file_uploader(
        "Upload resume",
        type=["pdf", "docx"],
        key=revision_key("resume_file"),
        on_change=_input_changed,
        disabled=not job_ready,
        help="Supported formats: PDF and DOCX.",
    )

    if job_ready and uploaded is not None:
        file_bytes = uploaded.getvalue()

        if not file_bytes:
            st.error("The uploaded file is empty.")
            return None

        st.success(f"Resume ready: {uploaded.name}")

        return ContentInput(
            kind=SourceKind.FILE,
            filename=uploaded.name,
            file_bytes=file_bytes,
        )

    return None


def _signature(job: ContentInput, resume: ContentInput) -> str:
    payload = (
        job.model_dump_json(exclude={"file_bytes"})
        + resume.model_dump_json(exclude={"file_bytes"})
    ).encode("utf-8")

    digest = hashlib.sha256()
    digest.update(payload)

    if job.file_bytes:
        digest.update(job.file_bytes)

    if resume.file_bytes:
        digest.update(resume.file_bytes)

    return digest.hexdigest()


def render_screening_form() -> ScreeningRequest | None:
    left, right = st.columns(2, gap="large")

    with left:
        with st.container(border=True):
            job = render_job_input()

    with right:
        with st.container(border=True):
            resume = render_resume_input(job_ready=job is not None)

    primary, secondary = st.columns([4, 1])

    ready = job is not None and resume is not None

    with primary:
        st.button(
            "Analysis starts automatically when both inputs are ready",
            disabled=True,
            use_container_width=True,
        )

    with secondary:
        st.button(
            "Clear",
            on_click=reset_screening,
            use_container_width=True,
        )

    if not ready:
        return None

    signature = _signature(job, resume)

    if st.session_state.get("last_screening_signature") == signature:
        return None

    st.session_state["last_screening_signature"] = signature

    return ScreeningRequest(
        job=job,
        candidate=resume,
    )