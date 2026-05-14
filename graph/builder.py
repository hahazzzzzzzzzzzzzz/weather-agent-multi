"""LangGraph 工作流构建器"""

from langgraph.graph import StateGraph, START
from agent.state import AgentState
from agent.nodes import (
    supervisor_node,
    weather_agent_node,
    general_agent_node,
    router_condition,
)


def build_weather_graph() -> StateGraph:
    """构建多智能体天气助手工作流图

    图结构：
    START → supervisor → (router)
        ├── weather_agent → FINISH
        └── general_agent → FINISH
    """
    builder = StateGraph(AgentState)

    # 注册节点
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("weather_agent", weather_agent_node)
    builder.add_node("general_agent", general_agent_node)

    # 注册边
    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges(
        "supervisor",
        router_condition,
        {
            "weather_agent": "weather_agent",
            "general_agent": "general_agent",
            "__end__": "__end__",
        }
    )
    builder.add_edge("weather_agent", "__end__")
    builder.add_edge("general_agent", "__end__")

    return builder.compile()


# 全局单例
_compiled_graph = None


def get_graph():
    """获取编译后的图（单例）"""
    global _compiled_graph
    if _compiled_graph is None:
        graph = build_weather_graph()
        _compiled_graph = graph
    return _compiled_graph
