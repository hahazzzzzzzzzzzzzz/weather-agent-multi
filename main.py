"""AI Agent 实战：LangGraph 多智能体天气助手

运行方式：
    python main.py              # 交互式 CLI 模式
    python main.py "北京天气"    # 单次查询模式
"""

import sys
import os
import warnings

# 抑制 LangChain 的弃用警告
os.environ["LANGCHAIN_DEPRECATION_MODE"] = "silent"

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from agent.state import AgentState
from graph.builder import get_graph

console = Console()
WELCOME_ART = """
╔══════════════════════════════════════════╗
║       多智能体天气助手                   ║
║    ---  LangGraph 实战  ---              ║
║                                          ║
║  主管 -> 天气智能体 / 通用智能体         ║
╚══════════════════════════════════════════╝
"""


def run_single_query(user_input: str) -> str:
    """执行单次查询，返回最终回复"""
    graph = get_graph()

    initial_state: AgentState = {
        "messages": [],
        "next_agent": "supervisor",
        "user_input": user_input,
    }

    final_state = None
    for output in graph.stream(initial_state):
        final_state = output

    # 从最终状态中获取最后一条 AI 消息
    if final_state:
        # final_state 是 dict，key 是节点名
        for node_name, node_state in final_state.items():
            if node_state and "messages" in node_state and node_state["messages"]:
                msgs = node_state["messages"]
                return msgs[-1].content

    return "抱歉，处理请求时出错了。"


def interactive_mode():
    """交互式 CLI 模式"""
    console.print(Panel.fit(WELCOME_ART, style="cyan"))
    console.print("[yellow]输入 'quit' 或 'exit' 退出程序[/yellow]\n")
    console.print("[dim]提示：支持天气查询和日常对话[/dim]\n")

    graph = get_graph()

    while True:
        user_input = console.input("[bold green]You: [/bold green] ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            console.print("\n[cyan]再见！[/cyan]")
            break

        # 显示处理中动画
        with console.status("[cyan]智能体路由处理中...", spinner="dots"):
            initial_state: AgentState = {
                "messages": [],
                "next_agent": "supervisor",
                "user_input": user_input,
            }

            final_output = None
            for output in graph.stream(initial_state):
                final_output = output

            # 找最终回答
            answer = "抱歉，处理出错了。"
            if final_output:
                for node_name, node_state in final_output.items():
                    if node_state and "messages" in node_state and node_state["messages"]:
                        msgs = node_state["messages"]
                        answer = msgs[-1].content

        console.print(Panel(
            Markdown(answer),
            title="[bold cyan]Agent 回答[/bold cyan]",
            border_style="cyan",
            width=80
        ))
        print()


def main():
    if len(sys.argv) > 1:
        # 命令行参数模式
        query = " ".join(sys.argv[1:])
        console.print(f"[cyan]查询：[/cyan]{query}\n")
        answer = run_single_query(query)
        console.print(Panel(
            Markdown(answer),
            title="[bold cyan]Agent 回答[/bold cyan]",
            border_style="cyan",
            width=80
        ))
    else:
        # 交互模式
        interactive_mode()


if __name__ == "__main__":
    main()
