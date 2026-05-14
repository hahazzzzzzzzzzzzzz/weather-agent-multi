"""Agent 节点函数定义"""

from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from utils.llm import get_llm, get_model_name
from agent.state import AgentState
from agent.tools import TOOLS, TOOL_MAP

SUPERVISOR_PROMPT = """你是一个智能任务路由主管。分析用户的输入，判断应该由哪个子智能体来处理。

规则：
- 如果用户询问天气、温度、降雨、天气预报等天气相关内容，选择 weather_agent
- 其他所有问题，选择 general_agent

只输出一行智能体名称：weather_agent 或 general_agent，不要输出其他任何内容。"""

WEATHER_SYSTEM_PROMPT = """你是一个天气助手。你可以使用以下工具查询天气信息：
1. get_current_weather - 查询实时天气
2. get_weather_forecast - 查询未来天气预报

请根据用户需求选择合适的工具，并用中文给出友好的回答。
重要：回复中绝对不要使用任何表情符号或特殊 Unicode 符号。"""

GENERAL_SYSTEM_PROMPT = """你是一个多智能体系统中的通用助手。你可以回答各种问题，但遇到天气相关的问题时，
请引导用户使用天气功能。请用中文友好地回答用户的问题。
重要：回复中绝对不要使用任何表情符号或特殊 Unicode 符号。"""


def supervisor_node(state: AgentState) -> AgentState:
    """主管节点：判断下一个该调用哪个智能体"""
    llm = get_llm()
    model = get_model_name()

    history = state.get("messages", [])
    user_input = state.get("user_input", "")

    # 让 LLM 做路由决策
    resp = llm.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SUPERVISOR_PROMPT},
            *[{"role": "user" if isinstance(m, HumanMessage) else "assistant",
               "content": m.content} for m in history[-4:]],
            {"role": "user", "content": user_input}
        ],
        temperature=0.1,
    )

    decision = resp.choices[0].message.content.strip().lower()
    if "weather" in decision:
        state["next_agent"] = "weather_agent"
    else:
        state["next_agent"] = "general_agent"

    return state


def weather_agent_node(state: AgentState) -> AgentState:
    """天气智能体节点：处理天气查询，可调用工具"""
    llm = get_llm()
    model = get_model_name()

    user_input = state.get("user_input", "")

    # 第一轮：LLM 决定是否调用工具
    resp = llm.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": WEATHER_SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        tools=TOOLS,
        tool_choice="auto",
    )

    msg = resp.choices[0].message

    # 如果需要调用工具
    if msg.tool_calls:
        # 执行工具函数
        import json
        tool_results = []
        for tc in msg.tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments)
            fn = TOOL_MAP.get(fn_name)
            if fn:
                result = fn(**fn_args)
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })

        # 第二轮：用正确的消息格式传给 LLM
        messages = [
            {"role": "system", "content": WEATHER_SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
            msg.model_dump(),  # 包含 tool_calls 的 assistant 消息
            *tool_results,
        ]

        final_resp = llm.chat.completions.create(
            model=model,
            messages=messages,
        )

        answer = final_resp.choices[0].message.content
    else:
        answer = msg.content or "抱歉，我没有找到相关天气信息。"

    # 更新消息历史
    new_messages = list(state.get("messages", []))
    new_messages.append(HumanMessage(content=user_input))
    new_messages.append(AIMessage(content=answer))
    state["messages"] = new_messages
    state["next_agent"] = "FINISH"

    return state


def general_agent_node(state: AgentState) -> AgentState:
    """通用智能体节点：处理非天气类对话"""
    llm = get_llm()
    model = get_model_name()

    user_input = state.get("user_input", "")

    resp = llm.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": GENERAL_SYSTEM_PROMPT},
            *[{"role": "user" if isinstance(m, HumanMessage) else "assistant",
               "content": m.content} for m in state.get("messages", [])[-6:]],
            {"role": "user", "content": user_input}
        ],
    )

    answer = resp.choices[0].message.content

    new_messages = list(state.get("messages", []))
    new_messages.append(HumanMessage(content=user_input))
    new_messages.append(AIMessage(content=answer))
    state["messages"] = new_messages
    state["next_agent"] = "FINISH"

    return state


def router_condition(state: AgentState) -> Literal["weather_agent", "general_agent", "__end__"]:
    """路由条件：根据 supervisor 的决策返回下一个节点"""
    next_agent = state.get("next_agent", "general_agent")
    if next_agent == "FINISH":
        return "__end__"
    return next_agent
