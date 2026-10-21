import json
from html import escape

import streamlit as st

from talentflow.domain.models import ScreeningResult
from talentflow.candidates.scoring import has_unverified_required_criteria, EvidenceMappingError


def _band(score: int) -> str:
    if score >= 85:
        return "Strong Match"
    if score >= 70:
        return "Potential Match"
    if score >= 50:
        return "Needs Human Review"
    return "Weak Match"


def _score_color(score: int) -> str:
    if score >= 85:
        return "#34d399"
    if score >= 70:
        return "#a78bfa"
    if score >= 50:
        return "#fbbf24"
    return "#fb7185"


def _safe(value) -> str:
    return escape(str(value or ""), quote=True)


def _section_title(title: str, subtitle: str = "") -> None:
    st.html(
        f"""
        <div style="margin:22px 0 12px;">
            <div style="font-size:20px;font-weight:750;color:#f5f3ff;">
                {_safe(title)}
            </div>
            <div style="font-size:12px;color:#a5acc9;margin-top:3px;">
                {_safe(subtitle)}
            </div>
        </div>
        """
    )


def _skill_card(title: str, items, color: str, background: str) -> None:
    chips = "".join(
        f"""
        <span style="
            display:inline-block;
            margin:4px;
            padding:8px 11px;
            border-radius:9px;
            background:{background};
            border:1px solid {color}55;
            color:{color};
            font-size:12px;
            line-height:1.45;
            overflow-wrap:anywhere;
        ">{_safe(item)}</span>
        """
        for item in items
    )

    if not chips:
        chips = '<span style="color:#a5acc9;font-size:13px;">None identified</span>'

    st.html(
        f"""
        <div style="
            background:#171b36;
            border:1px solid #30365b;
            border-radius:16px;
            padding:18px;
            margin-bottom:12px;
            min-height:170px;
        ">
            <div style="font-size:15px;font-weight:700;color:#f5f3ff;margin-bottom:13px;">
                {_safe(title).replace("&amp;#", "&#")}
            </div>
            <div>{chips}</div>
        </div>
        """
    )


def _text_card(title: str, items, color: str) -> None:
    entries = "".join(
        f"""
        <div style="
            display:flex;
            gap:10px;
            padding:9px 0;
            border-bottom:1px solid #30365b;
            color:#dbe0f3;
            font-size:13px;
            line-height:1.6;
        ">
            <span style="color:{color};font-weight:700;">&#9679;</span>
            <span style="overflow-wrap:anywhere;">{_safe(item)}</span>
        </div>
        """
        for item in items
    )

    if not entries:
        entries = '<div style="color:#a5acc9;">No items identified</div>'

    st.html(
        f"""
        <div style="
            background:#171b36;
            border:1px solid #30365b;
            border-radius:16px;
            padding:18px;
            margin-bottom:12px;
        ">
            <div style="font-size:15px;font-weight:700;color:#f5f3ff;margin-bottom:12px;">
                {_safe(title)}
            </div>
            {entries}
        </div>
        """
    )


def render_results(result: ScreeningResult) -> None:
    if result.status != "completed":
        st.warning(result.message)
    else:
        st.success(result.message)

    assessment = result.assessment
    if assessment is not None and assessment.match_score is not None:
        if assessment.match_score < 50:
            st.error(
                "Job Description Does Not Match Resume - "
                "the candidate does not demonstrate sufficient alignment "
                "with the role's core requirements. "
                "Review the missing skills and evidence below."
            )

    if assessment is None or assessment.match_score is None:
        with st.expander("Job understanding"):
            if result.job:
                st.write(result.job.model_dump())
        with st.expander("Document classification"):
            if result.document:
                st.write(result.document.model_dump())

        with st.expander("Assessment diagnostics"):
            st.write("Screening status:", result.status)
            if assessment is not None:
                st.json(assessment.model_dump(mode="json"))
            else:
                st.write("No assessment was returned.")
        return

    score = max(0, min(100, int(assessment.match_score)))
    color = _score_color(score)
    band = _band(score)

    if result.job is not None:
        try:
            if has_unverified_required_criteria(result.job, assessment):
                band = "Needs Human Review"
        except EvidenceMappingError:
            band = "Needs Human Review"

    if band == "Needs Human Review":
        color = "#fbbf24"

    _section_title(
        "Executive Assessment",
        "Evidence-grounded candidate evaluation"
    )

    score_col, summary_col = st.columns([1, 2], gap="medium")

    with score_col:
        st.html(
            f"""
            <div style="
                background:#171b36;
                border:1px solid #30365b;
                border-radius:18px;
                padding:24px 14px;
                text-align:center;
                height:100%;
            ">
                <div style="
                    width:160px;
                    height:160px;
                    border-radius:50%;
                    background:conic-gradient(
                        {color} {score}%,
                        #30365b {score}%
                    );
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    margin:0 auto 15px;
                ">
                    <div style="
                        width:130px;
                        height:130px;
                        background:#171b36;
                        border-radius:50%;
                        display:flex;
                        flex-direction:column;
                        align-items:center;
                        justify-content:center;
                    ">
                        <div style="
                            font-size:40px;
                            font-weight:800;
                            color:#fff;
                        ">{score}%</div>
                        <div style="font-size:11px;color:#a5acc9;">
                            Match Score
                        </div>
                    </div>
                </div>
                <div style="
                    color:{color};
                    font-size:15px;
                    font-weight:700;
                ">{_safe(band)}</div>
            </div>
            """
        )

    with summary_col:
        st.html(
            f"""
            <div style="
                background:#171b36;
                border:1px solid #30365b;
                border-radius:18px;
                padding:22px;
                height:100%;
            ">
                <div style="
                    color:#c4b5fd;
                    font-weight:700;
                    font-size:15px;
                    margin-bottom:12px;
                ">Assessment Summary</div>

                <div style="
                    color:#e0e4f5;
                    font-size:13px;
                    line-height:1.75;
                    white-space:pre-wrap;
                    overflow-wrap:anywhere;
                ">{_safe(assessment.assessment_reasoning)}</div>

                <div style="
                    margin-top:18px;
                    padding-top:13px;
                    border-top:1px solid #30365b;
                    color:#a5acc9;
                    font-size:12px;
                ">
                    <strong style="color:#c4b5fd;">
                        Experience alignment
                    </strong>
                    <div style="margin-top:7px;color:#e0e4f5;line-height:1.6;">
                        {_safe(assessment.experience_alignment)}
                    </div>
                </div>
            </div>
            """
        )

    _section_title(
        "Skill Analysis",
        "Matching capabilities and requirements needing verification"
    )

    left, right = st.columns(2, gap="medium")

    with left:
        _skill_card(
            "&#10003; Matching Skills",
            assessment.matching_skills,
            "#6ee7b7",
            "#153b37"
        )

    with right:
        _skill_card(
            "&#10005; Missing / Unverified Skills",
            assessment.missing_skills,
            "#fda4af",
            "#46232f"
        )

    _section_title(
        "Candidate Insights",
        "Strengths and potential gaps"
    )

    left, right = st.columns(2, gap="medium")

    with left:
        _text_card(
            "Candidate Strengths",
            assessment.candidate_strengths,
            "#34d399"
        )

    with right:
        _text_card(
            "Potential Gaps",
            assessment.potential_gaps,
            "#fb923c"
        )

    _section_title(
        "Detailed Analysis",
        "Supporting evidence and screening details"
    )

    with st.expander("Job Understanding"):
        if result.job:
            st.write("**Detected role:**", result.job.title or "Not identified")
            st.write(result.job.summary)
            st.write(
                "**Required skills:**",
                ", ".join(result.job.required_skills) or "Not identified"
            )

    with st.expander("Document Classification"):
        if result.document:
            st.write("**Type:**", result.document.document_type)
            st.write(
                "**Status:**",
                result.document.status.replace("_", " ").title()
            )
            st.write(result.document.summary)

    with st.expander("Evidence and Recruiter Questions"):
        st.markdown("#### Supporting Evidence")

        for item in assessment.evidence:
            st.markdown(f"**{item.requirement}**")
            st.write("Status:", item.status)
            st.write(
                "Resume evidence:",
                item.resume_evidence or "No supporting excerpt"
            )
            st.divider()

        st.markdown("#### Recruiter Questions")

        for question in assessment.recruiter_questions:
            st.write("-", question)
    st.download_button(
        "Download JSON Report",
        data=json.dumps(
            result.model_dump(mode="json"),
            indent=2
        ),
        file_name="talentflow-assessment.json",
        mime="application/json",
        use_container_width=True,
    )


