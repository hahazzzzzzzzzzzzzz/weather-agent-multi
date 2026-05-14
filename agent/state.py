"""LangGraph 状态定义"""

from typing import Annotated, Sequence, TypedDict, Literal
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """多智能体系统的全局状态"""
    messages: Annotated[list, add_messages]
    next_agent: Literal["weather_agent", "general_agent", "FINISH"]
    user_input: str
