import streamlit as st
from talentflow.domain.models import ContentInput, ScreeningRequest, SourceKind


def _source_input(label: str, *, allow_url: bool, key: str) -> ContentInput | None:
    options = ["🔗 Job URL", "📋 Paste Text", "📄 PDF / DOCX"] if allow_url else ["📄 PDF / DOCX", "📋 Paste Text"]
    selected = st.radio(label, options, horizontal=True, key=f"{key}_mode")
    if selected.startswith("🔗"):
        url = st.text_input("Job posting URL", placeholder="https://company.com/careers/job/...", key=f"{key}_url")
        return ContentInput(kind=SourceKind.URL, url=url) if url.strip() else None
    if selected.startswith("📋"):
        text = st.text_area("Job description" if allow_url else "Resume text", height=190, key=f"{key}_text")
        return ContentInput(kind=SourceKind.TEXT, text=text) if text.strip() else None
    uploaded = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"], key=f"{key}_file")
    return ContentInput(kind=SourceKind.FILE, filename=uploaded.name, file_bytes=uploaded.getvalue()) if uploaded else None


def render_screening_form() -> ScreeningRequest | None:
    st.subheader("New Candidate Screening")
    with st.form("screening"):
        job = _source_input("Job requirements", allow_url=True, key="job")
        st.divider()
        candidate = _source_input("Candidate resume", allow_url=False, key="candidate")
        submitted = st.form_submit_button("✨ Analyze Candidate", use_container_width=True, type="primary")
    if not submitted:
        return None
    if job is None:
        st.warning("Job details required. Enter a job posting URL, paste the JD, or upload a job document.")
        return None
    if candidate is None:
        st.warning("Candidate information required. Upload a resume or paste its text.")
        return None
    return ScreeningRequest(job=job, candidate=candidate)
