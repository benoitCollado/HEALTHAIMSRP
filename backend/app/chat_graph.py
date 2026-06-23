"""Agent chat LangGraph — contexte objectifs, tools microservice, forçage Mistral."""

from __future__ import annotations

import json
from typing import Any, Literal

from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

from app.chat_agent import (
    MAX_TOOL_ROUNDS,
    MISTRAL_MICROSERVICE_TOOLS,
    AgentContext,
    build_objectifs_context_message,
    build_objectifs_microservice,
    detect_required_tools,
    execute_microservice_tool,
    merge_tool_result,
    _parse_tool_arguments,
)
from app.external_clients import ExternalServiceResponseError, call_mistral_chat_completion


class ChatGraphState(TypedDict, total=False):
    messages: list[dict[str, Any]]
    user_id: int
    profile_payload: dict[str, Any]
    objectifs: list[dict[str, Any]]
    objectifs_microservice: list[str]
    required_tools: list[str]
    completed_tools: list[str]
    tool_results: dict[str, Any]
    last_assistant_message: dict[str, Any]
    answer: str
    iteration: int


def _last_user_message(messages: list[dict[str, Any]]) -> str:
    for message in reversed(messages):
        if message.get("role") == "user":
            return str(message.get("content") or "")
    return ""


def _pending_required_tools(state: ChatGraphState) -> list[str]:
    required = state.get("required_tools") or []
    completed = set(state.get("completed_tools") or [])
    return [tool for tool in required if tool not in completed]


def enrich_context(state: ChatGraphState) -> ChatGraphState:
    objectifs = state.get("objectifs") or []
    profile_payload = state["profile_payload"]
    objectifs_microservice = build_objectifs_microservice(objectifs, profile_payload)
    context_message = build_objectifs_context_message(objectifs, objectifs_microservice)
    messages = list(state["messages"])
    messages.insert(1, {"role": "system", "content": context_message})
    return {
        **state,
        "messages": messages,
        "objectifs_microservice": objectifs_microservice,
        "tool_results": state.get("tool_results") or {},
        "completed_tools": state.get("completed_tools") or [],
        "iteration": 0,
    }


def detect_requirements(state: ChatGraphState) -> ChatGraphState:
    user_message = _last_user_message(state["messages"])
    return {**state, "required_tools": detect_required_tools(user_message)}


def invoke_model(state: ChatGraphState) -> ChatGraphState:
    iteration = int(state.get("iteration") or 0) + 1
    pending = _pending_required_tools(state)
    tool_choice: str | dict[str, Any] = "auto"
    if pending:
        tool_choice = {"type": "function", "function": {"name": pending[0]}}

    assistant_message = call_mistral_chat_completion(
        state["messages"],
        tools=MISTRAL_MICROSERVICE_TOOLS,
        tool_choice=tool_choice,
        max_tokens=800 if pending else 500,
    )
    messages = list(state["messages"])
    messages.append(assistant_message)
    return {
        **state,
        "messages": messages,
        "last_assistant_message": assistant_message,
        "iteration": iteration,
    }


def run_tools(state: ChatGraphState) -> ChatGraphState:
    assistant_message = state.get("last_assistant_message") or {}
    tool_calls = assistant_message.get("tool_calls") or []
    context = AgentContext(
        user_id=int(state["user_id"]),
        profile_payload=state["profile_payload"],
        objectifs=state.get("objectifs") or [],
        objectifs_microservice=state.get("objectifs_microservice") or [],
    )
    tool_results = dict(state.get("tool_results") or {})
    completed_tools = list(state.get("completed_tools") or [])
    messages = list(state["messages"])

    for tool_call in tool_calls:
        function = tool_call.get("function") or {}
        tool_name = str(function.get("name") or "")
        arguments_raw = function.get("arguments")
        if isinstance(arguments_raw, dict):
            arguments = arguments_raw
        else:
            arguments = _parse_tool_arguments(arguments_raw)
        result = execute_microservice_tool(tool_name, context, arguments)
        merge_tool_result(tool_results, tool_name, result)
        if tool_name and tool_name not in completed_tools:
            completed_tools.append(tool_name)
        messages.append(
            {
                "role": "tool",
                "content": json.dumps(result, ensure_ascii=False),
                "tool_call_id": tool_call.get("id", ""),
                "name": tool_name,
            }
        )

    return {
        **state,
        "messages": messages,
        "tool_results": tool_results,
        "completed_tools": completed_tools,
    }


def route_after_model(state: ChatGraphState) -> Literal["tools", "continue", "end"]:
    if int(state.get("iteration") or 0) >= MAX_TOOL_ROUNDS:
        return "end"

    assistant_message = state.get("last_assistant_message") or {}
    if assistant_message.get("tool_calls"):
        return "tools"

    pending = _pending_required_tools(state)
    if pending:
        return "continue"

    content = (assistant_message.get("content") or "").strip()
    if content:
        return "end"
    return "continue"


def finalize(state: ChatGraphState) -> ChatGraphState:
    assistant_message = state.get("last_assistant_message") or {}
    content = (assistant_message.get("content") or "").strip()
    if content:
        return {**state, "answer": content}

    tool_results = state.get("tool_results") or {}
    if tool_results:
        return {
            **state,
            "answer": (
                "Voici les donnees recuperees depuis le microservice IA. "
                f"{json.dumps(tool_results, ensure_ascii=False)}"
            ),
        }
    raise ExternalServiceResponseError("Reponse Mistral vide")


def build_chat_graph():
    graph = StateGraph(ChatGraphState)
    graph.add_node("enrich_context", enrich_context)
    graph.add_node("detect_requirements", detect_requirements)
    graph.add_node("invoke_model", invoke_model)
    graph.add_node("run_tools", run_tools)
    graph.add_node("finalize", finalize)

    graph.set_entry_point("enrich_context")
    graph.add_edge("enrich_context", "detect_requirements")
    graph.add_edge("detect_requirements", "invoke_model")
    graph.add_conditional_edges(
        "invoke_model",
        route_after_model,
        {"tools": "run_tools", "continue": "invoke_model", "end": "finalize"},
    )
    graph.add_edge("run_tools", "invoke_model")
    graph.add_edge("finalize", END)
    return graph.compile()


_CHAT_GRAPH = None


def get_chat_graph():
    global _CHAT_GRAPH
    if _CHAT_GRAPH is None:
        _CHAT_GRAPH = build_chat_graph()
    return _CHAT_GRAPH


def run_chat_graph(
    messages: list[dict[str, Any]],
    user_id: int,
    profile_payload: dict[str, Any],
    objectifs: list[dict[str, Any]],
) -> tuple[str, dict[str, Any] | None]:
    final_state = get_chat_graph().invoke(
        {
            "messages": messages,
            "user_id": user_id,
            "profile_payload": profile_payload,
            "objectifs": objectifs,
        }
    )
    answer = str(final_state.get("answer") or "").strip()
    if not answer:
        raise ExternalServiceResponseError("Reponse Mistral vide")
    tool_results = final_state.get("tool_results") or {}
    recommendation = tool_results if tool_results else None
    if recommendation and "objectifs" not in recommendation:
        recommendation = {
            **recommendation,
            "objectifs": objectifs,
            "objectifs_microservice": final_state.get("objectifs_microservice") or [],
        }
    return answer, recommendation


def run_chat_with_tools(
    messages: list[dict[str, Any]],
    profile_payload: dict[str, Any],
    *,
    user_id: int = 0,
    objectifs: list[dict[str, Any]] | None = None,
    max_rounds: int = MAX_TOOL_ROUNDS,
) -> tuple[str, dict[str, Any] | None]:
    """Compatibilite tests — delegue au graphe LangGraph."""
    _ = max_rounds
    return run_chat_graph(
        messages,
        user_id=user_id,
        profile_payload=profile_payload,
        objectifs=objectifs or [],
    )
