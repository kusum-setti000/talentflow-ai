from pathlib import Path
import logging

import streamlit as st

from talentflow.bootstrap import get_screening_service
from ui.components.form import render_screening_form
from ui.components.results import render_results

logger = logging.getLogger(__name__)
UI_DIR = Path(__file__).resolve().parent


def load_html(filename: str) -> None:
    path = UI_DIR / "templates" / filename
    st.html(path.read_text(encoding="utf-8"))


def load_css() -> None:
    for filename in ("styles.css", "responsive.css"):
        path = UI_DIR / "assets" / filename
        st.html(f"<style>{path.read_text(encoding='utf-8')}</style>")


def main() -> None:
    st.set_page_config(
        page_title="TalentFlow AI",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    load_css()
    load_html("hero.html")

    request = render_screening_form()

    if request is not None:
        st.session_state.pop("result", None)

        try:
            with st.spinner("Analyzing candidate..."):
                result = get_screening_service().screen(request)
                st.session_state["result"] = result
        except Exception:
            logger.exception("Screening failed")
            st.error("Analysis failed. Check the server logs.")

    if "result" in st.session_state:
        render_results(st.session_state["result"])
    else:
        pass


if __name__ == "__main__":
    main()