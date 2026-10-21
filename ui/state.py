import streamlit as st


def invalidate_result() -> None:
    st.session_state.pop("result", None)


def reset_screening() -> None:
    revision = st.session_state.get("screening_revision", 0)
    st.session_state["screening_revision"] = revision + 1

    for key in (
        "result",
        "job_mode",
        "job_url",
        "job_text",
        "job_error",
        "job_extracted",
        "resume_mode",
        "resume_text",
    ):
        st.session_state.pop(key, None)


def revision_key(name: str) -> str:
    revision = st.session_state.get("screening_revision", 0)
    return f"{name}_{revision}"
