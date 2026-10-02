import os
import requests
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """查询指定城市的当前天气，包括温度、天气状况、湿度、风速。
    当用户问某个城市天气、气温、冷不冷、热不热、下不下雨时用这个工具。

    Args:
        city: 城市名称
    """
    try:
        url = f"https://wttr.in/{city}?format=j1&lang=zh"
        resp = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "curl/7.68.0"}
        )
        resp.raise_for_status()
        data = resp.json()
        cur = data["current_condition"][0]
        area = data["nearest_area"][0]

        return (
            f"【{area['areaName'][0]['value']}天气】 "
            f"{cur['weatherDesc'][0]['value']}; "
            f"{cur['temp_C']}°C（体感{cur['FeelsLikeC']}°C）, "
            f"湿度{cur['humidity']}%, 风速{cur['windspeedKmph']}km/h"
        )
    except Exception as e:
        return f"无法获取 {city} 的天气信息：{str(e)}"


tools = [get_weather]


llm = ChatOpenAI(
    model=os.getenv("DATA_MODEL"),
    api_key=os.getenv("DATA_API_KEY"),
    base_url=os.getenv("DATA_BASE_URL"),
    temperature=0,
)


agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
        你是天气小助手，专业友好。
        1. 问天气必须调用get_weather工具，不要编造
        2. 回答简洁自然，根据温度给穿衣建议（<10度保暖，>30度防暑）
        3. 用户没说城市时礼貌询问
        4. 非天气问题礼貌说明你主要提供天气服务
        """,
)


class WeatherChat:
    """多轮对话会话，自己维护消息历史"""

    def __init__(self):
        self.messages = []  # 消息列表，存所有历史

    def send(self, user_input: str) -> str:
        """发送用户消息，返回助手回答"""

        # 1. 把用户消息加入历史
        self.messages.append(HumanMessage(content=user_input))

        # 2. 调用agent（传入完整历史）
        result = agent.invoke({"messages": self.messages})

        # 3. 用agent返回的完整消息列表更新历史（包含工具调用过程）
        self.messages = result["messages"]

        # 4. 最后一条就是最终回答
        return self.messages[-1].content

    def clear(self):
        """清空对话"""
        self.messages = []


if __name__ == "__main__":
    print("=" * 50)
    print("  天气助手 V2（多轮对话版）")
    print("命令：quit 退出 | clear 清空对话")
    print("=" * 50)

    chat = WeatherChat()

    while True:
        user_input = input("\n你：").strip()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("再见！")
            break

        if user_input.lower() == "clear":
            chat.clear()
            print("对话已清空，重新开始～")
            continue

        answer = chat.send(user_input)
        print(f"助手：{answer}")