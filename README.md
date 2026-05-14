# AI-Agent

基于 LangGraph 的 AI 智能体实战项目集合。

## 📁 项目列表

### 🌤️ weather-agent-multi — 多智能体天气助手

基于 LangGraph 构建的多智能体天气查询系统，采用 Supervisor 路由架构，自动判断用户意图并调度对应智能体。

- 🧭 **Supervisor** 节点：分析意图、自动分发
- 🌤️ **Weather Agent**：调用工具查询实时天气与天气预报
- 💬 **General Agent**：处理日常对话

```bash
cd weather-agent-multi
pip install -r requirements.txt
python main.py "北京天气"
```

### ✈️ MultiAgent\_Travel\_Planner — 多智能体旅行规划器

基于 LangGraph 的多智能体协作旅行规划系统，多角色协同完成旅行计划制定。

```bash
cd MultiAgent_Travel_Planner
pip install -r requirements.txt
python main.py
```

## 🛠️ 技术栈

- [LangGraph](https://github.com/langchain-ai/langgraph) — 状态图工作流引擎
- [LangChain Core](https://github.com/langchain-ai/langchain) — 消息抽象
- [OpenAI SDK](https://github.com/openai/openai-python) — LLM API 调用
- [Rich](https://github.com/Textualize/rich) — CLI 美化输出

## 📝 License

MIT
