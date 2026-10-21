import json
import streamlit as st
from talentflow.domain.models import ScreeningResult


def _band(score: int) -> str:
    if score >= 85:
        return "Strong Match"
    if score >= 70:
        return "Potential Match"
    if score >= 50:
        return "Needs Human Review"
    return "Weak Match"


def render_results(result: ScreeningResult) -> None:
    if result.status != "completed":
        st.warning(result.message)
    else:
        st.success(result.message)
    with st.expander("Job understanding", expanded=result.status != "completed"):
        if result.job:
            st.write("**Detected role:**", result.job.title or "Not identified")
            st.write(result.job.summary)
            st.write("**Required skills:**", ", ".join(result.job.required_skills) or "Not identified")
    with st.expander("Document classification", expanded=result.status != "completed"):
        if result.document:
            st.write("**Type:**", result.document.document_type)
            st.write("**Status:**", result.document.status.replace("_", " ").title())
            st.write(result.document.summary)
    assessment = result.assessment
    if assessment is None or assessment.match_score is None:
        return
    st.markdown("### Executive Assessment")
    score_col, detail_col = st.columns([1, 2])
    with score_col:
        st.metric("Candidate match", f"{assessment.match_score}%")
        st.markdown(f"**{_band(assessment.match_score)}**")
    with detail_col:
        st.write(assessment.assessment_reasoning)
        st.write("**Experience alignment:**", assessment.experience_alignment)
    left, right = st.columns(2)
    with left:
        st.markdown("#### Matching Skills")
        for item in assessment.matching_skills:
            st.write("✓", item)
        st.markdown("#### Strengths")
        for item in assessment.candidate_strengths:
            st.write("•", item)
    with right:
        st.markdown("#### Missing / Unverified Skills")
        for item in assessment.missing_skills:
            st.write("•", item)
        st.markdown("#### Potential Gaps")
        for item in assessment.potential_gaps:
            st.write("•", item)
    with st.expander("Evidence and recruiter questions"):
        for item in assessment.evidence:
            st.write(f"**{item.requirement}** — {item.status}: {item.resume_evidence or 'No supporting excerpt'}")
        for question in assessment.recruiter_questions:
            st.write("•", question)
    st.download_button("Download JSON report", json.dumps(result.model_dump(mode="json"), indent=2),
                       file_name="talentflow-assessment.json", mime="application/json")
