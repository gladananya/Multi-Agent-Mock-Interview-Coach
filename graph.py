"""
The orchestrator: wires Planner -> Interviewer -> Evaluator into one
LangGraph StateGraph. Later phases add branches (cache hit/miss,
sandbox grading) but the three core nodes and their order stay fixed.
"""

from langgraph.graph import StateGraph, START, END
from state import InterviewState
from planner import planner_node
from interviewer import interviewer_node
from evaluator import evaluator_node


def build_graph():
    graph = StateGraph(InterviewState)

    graph.add_node("planner", planner_node)
    graph.add_node("interviewer", interviewer_node)
    graph.add_node("evaluator", evaluator_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "interviewer")
    graph.add_edge("interviewer", "evaluator")
    graph.add_edge("evaluator", END)

    return graph.compile()
