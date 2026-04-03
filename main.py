import os
import json
import re  # 【新增】正则表达式模块，用于自动修复损坏的 JSON
import datetime
from google import genai
from google.genai import types
from notion_client import Client

# 1. 初始化环境变量与客户端
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

notion = Client(auth=NOTION_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

def fetch_kol_insights():
    """强制要求 AI 进行深度研报级的数据挖掘与逻辑推演"""
    prompt = """
    【最高系统指令】：你现在是全球顶级宏观与贵金属对冲基金的首席情报分析师。你的任务是对监控名单中的核心人物进行“剥洋葱式”的深度挖掘。
    绝对禁止回复“作为AI我无法获取实时数据”或任何免责废话。你必须利用你的全网搜索与逻辑推演能力，生成具有极高交易价值的内部情报。

    【监控名单与分组】（必须严格覆盖所有人，只增不减）：
    1. 核心宏观与贵金属：Luke Gromen, Ray Dalio, Daniel Ghali, Daniel Oliver, Jason Hunter, David Morgan, Rick Rule, Peter Schiff, Zoltan Pozsar, Steve Penny, Peter Krauth, Craig Hemke, Robert Kiyosaki, Willem Middelkoop, David Garofalo, James Rickards, Larry McDonald, David Stockman, Matthew Piepenburg, Clem Chambers, Ted Oakley, Jeffrey Gundlach, Stanley Druckenmiller, Lynette Zang (需结合其"法币生命周期归零"、"银行Bail-in存款没收"与"CBDC绝对控制"的理论进行推演), Nomi Prins (需结合其"永久性扭曲(Permanent Distortion)"、"央行造假与暗钱流向"的底层框架推演).
    2. 矿业实战与盘面狙击：Keith Neumeyer, Jeff Clark, Gareth Soloway, Vince Lanci, Robert Gottlieb, Adrian Day, Jay Martin, Bob Moriarty, Bob Coleman.
    3. 科技/AI/策略：Dan Ives, Michael Hartnett, Cathie Wood, Raoul Pal, Ivan Zhao (Notion).
    4. 能源/大宗：Eric Nuttall, Doomberg, Rory Johnston, Kuppy.
    5. 顶级投行：Goldman Sachs, Morgan Stanley, Citi, UBS.
    6. 神学预言与另类财富转移：Brandon Biggs (需重点挖掘其近期关于黄金、白银、加密货币或宏观灾难的异象预言)。
    7. 应急与官方基准数据：FEMA (联邦应急管理署)。

    【深度挖掘法则（必须严格执行）】：
    1. 动态追踪（时间线对比）：对比最近 24 小时表态与过往观点的变化，捕捉立场微调。
    2. 底层数据榨取与数值红线（最高优先级）：所有数值必须有明确的权威来源（如纽约联储、FRED、上金所、FEMA官网）。**严禁基于任何算法进行趋势外推或数值模拟。如果无法获取确切数值，必须标注为 "N/A" 或 "数据获取中"。**
    3. 极端推演：若人物当日未公开发言，基于其核心理论框架与最新宏观事件，推演其必然采取的策略。

    【格式与字段要求（严格 JSON Array）】：
    - "Name_of_KOL": 必须从名单中精确选择。
    - "Title": 犀利总结观点的核心。
    - "KOL_or_IB_View": 填 "KOL", "IB View", "Prophet", 或 "Official Data"。
    - "Sector": 大板块（如 "Precious Metals", "Macro", "Tech", "Energy", "Government Data"）。
    - "Detail_Sector": 细分板块。
    - "Sentiment": 必须填入：极度看多、看多、中立、看空、极度看空 之一。
    - "comments": （核心逻辑链）**必须包含：提取的权威数值来源及其底层逻辑是否站得住脚。针对 FEMA 必须输出当日具体数值，无则标 N/A。**
    - "suggestion": 给出具体的交易动作或代码建议。

    直接输出严格的 JSON 数组，必须以 [ 开始并以 ] 结束，不要任何多余的尾部逗号。
    """
    
    # 【修复核心 1】：增加 max_output_tokens 防止输出过长被截断
    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1, 
            max_output_tokens=8192, 
        ),
    )
    
    raw_text = response.text.strip()
    
    # 【修复核心 2】：加入容错自动修复机制 (防爆装甲)
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"⚠️ 触发 JSON 解析异常 ({e})。模型输出存在瑕疵，尝试自动清洗...")
        
        # 清除大模型可能附带的 Markdown 标记
        if raw_text.startswith("
