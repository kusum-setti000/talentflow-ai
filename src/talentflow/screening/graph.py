"""LangGraph owns control flow. LLMs never choose executable tools."""
from langgraph.graph import StateGraph, START, END
from talentflow.screening.state import ScreeningState


def build_screening_workflow(job_analyzer, document_classifier, candidate_assessor):
    def analyze_job(state: ScreeningState):
        return {"job_analysis": job_analyzer.analyze(state["job_text"])}

    def classify_resume(state: ScreeningState):
        return {"document_analysis": document_classifier.classify(state["resume_text"])}

    def decide(state: ScreeningState) -> str:
        job = state["job_analysis"]
        document = state["document_analysis"]
        return "assess" if job.status == "valid" and document.status == "valid_resume" else "stop"

    def assess(state: ScreeningState):
        return {"assessment": candidate_assessor.assess(state["job_analysis"], state["resume_text"])}

    workflow = StateGraph(ScreeningState)
    workflow.add_node("analyze_job", analyze_job)
    workflow.add_node("classify_resume", classify_resume)
    workflow.add_node("assess", assess)
    workflow.add_edge(START, "analyze_job")
    workflow.add_edge(START, "classify_resume")
    # A barrier node waits for both independent analyses before routing.
    workflow.add_node("eligibility", lambda state: {})
    workflow.add_edge(["analyze_job", "classify_resume"], "eligibility")
    workflow.add_conditional_edges("eligibility", decide, {"assess": "assess", "stop": END})
    workflow.add_edge("assess", END)
    return workflow.compile()
