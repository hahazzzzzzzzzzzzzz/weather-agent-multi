"""天气查询工具函数"""

import httpx
from typing import Optional


def get_current_weather(city: str) -> str:
    """查询指定城市的实时天气（使用 wttr.in，无需 API Key）"""
    try:
        url = f"https://wttr.in/{city}?format=%C+%t+%h+%w+%p"
        resp = httpx.get(url, timeout=10)
        if resp.status_code == 200:
            raw = resp.text.strip()
            return f"{city} 的当前天气：{raw}"
        return f"查询 {city} 天气失败（状态码: {resp.status_code}）"
    except Exception as e:
        return f"查询天气时出错：{e}"


def get_weather_forecast(city: str, days: int = 3) -> str:
    """查询指定城市未来 N 天的天气预报（最多 3 天）"""
    try:
        days = min(max(days, 1), 3)
        url = f"https://wttr.in/{city}?format=j1"
        resp = httpx.get(url, timeout=10)
        if resp.status_code != 200:
            return f"查询 {city} 预报失败（状态码: {resp.status_code}）"

        data = resp.json()
        forecasts = data.get("weather", [])[:days]
        lines = [f"--- {city} 未来 {days} 天天气预报 ---"]

        for day in forecasts:
            date = day.get("date", "未知")
            maxt = day.get("maxtempC", "?")
            mint = day.get("mintempC", "?")
            desc = day.get("hourly", [{}])[0].get("weatherDesc", [{}])[0].get("value", "")
            lines.append(f"  {date}: {desc}，{mint}°C ~ {maxt}°C")

        return "\n".join(lines)
    except Exception as e:
        return f"查询天气预报时出错：{e}"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "查询某个城市的实时天气情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如 北京、Shanghai、London"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": "查询某个城市未来几天的天气预报",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称"
                    },
                    "days": {
                        "type": "integer",
                        "description": "预报天数（1-3）",
                        "default": 3
                    }
                },
                "required": ["city"]
            }
        }
    }
]

TOOL_MAP = {
    "get_current_weather": get_current_weather,
    "get_weather_forecast": get_weather_forecast,
}
