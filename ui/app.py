import streamlit as st
from talentflow.bootstrap import get_screening_service
from ui.components.form import render_screening_form
from ui.components.results import render_results


def main() -> None:
    st.set_page_config(page_title="TalentFlow AI", page_icon="✨", layout="wide")
    with open("ui/assets/styles.css", encoding="utf-8") as css:
        st.html(f"<style>{css.read()}</style>")
    st.markdown('<div class="tf-hero"><h1>TalentFlow AI</h1><p>Intelligent, evidence-grounded candidate screening</p></div>', unsafe_allow_html=True)
    request = render_screening_form()
    if request is not None:
        with st.spinner("Understanding the job and candidate document..."):
            st.session_state["result"] = get_screening_service().screen(request)
    if "result" in st.session_state:
        render_results(st.session_state["result"])


if __name__ == "__main__":
    main()
