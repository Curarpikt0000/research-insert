import os
import json
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
    1. 核心宏观与贵金属：Luke Gromen, Ray Dalio, Daniel Ghali, Daniel Oliver, Jason Hunter, David Morgan, Rick Rule, Peter Schiff, Zoltan Pozsar, Steve Penny, Peter Krauth, Craig Hemke, Robert Kiyosaki, Willem Middelkoop, David Garofalo, James Rickards, Larry McDonald, David Stockman, Matthew Piepenburg, Clem Chambers, Ted Oakley.
    2. 矿业实战与盘面狙击：Keith Neumeyer, Jeff Clark, Gareth Soloway, Vince Lanci, Robert Gottlieb, Adrian Day, Jay Martin, Bob Moriarty, Bob Coleman.
    3. 科技/AI/策略：Dan Ives, Michael Hartnett, Cathie Wood, Raoul Pal, Ivan Zhao (Notion).
    4. 能源/大宗：Eric Nuttall, Doomberg, Rory Johnston, Kuppy.
    5. 顶级投行：Goldman Sachs, Morgan Stanley, Citi, UBS.
    6. 神学预言与另类财富转移：Brandon Biggs (需重点挖掘他近期在 YouTube 和 X 上关于黄金、白银、加密货币或宏观灾难的异象预言与报告)。
    7. 应急与官方基准数据：FEMA (联邦应急管理署)。

    【深度挖掘法则（必须严格执行）】：
    1. 动态追踪（时间线对比）：不要只给一个静态结论。你必须搜索并对比他们最近 24 小时的表态与前几天/前几个月的观点。他们改口了吗？目标价微调了吗？
    2. 底层数据榨取与数值红线（极其重要）：提取观点的“物理依据”或“量化指标”。**特别要求：针对 FEMA，必须获取其每天公布的相关数值并输出。所有提取的数值必须有明确的权威来源，如果因网络或接口延迟无法获取最新的确切数值，你必须在结果中标注为 "N/A" 或 "数据获取中"，绝对禁止基于任何算法进行趋势外推或数值模拟！**
    3. 极端推演：如果该人物过去 24 小时没有公开发言，强制推演出他今天必然会采取的应对策略。

    【格式与字段要求（严格 JSON Array）】：
    - "Name_of_KOL": 必须从名单中精确选择。
    - "Title": 犀利的一句话总结（如："放弃 40 美元做空目标" 或 "FEMA灾害响应资金余额更新"）。
    - "KOL_or_IB_View": 填 "KOL", "IB View", "Prophet", 或 "Official Data"。
    - "Sector": 所属大板块（如 "Precious Metals", "Macro", "Tech", "Alternative/Prophecy", "Government Data"）。
    - "Detail_Sector": 细分板块（如 "Silver Miners", "Wealth Transfer", "Technical Sniper", "Disaster Relief"）。
    - "comments": （核心逻辑链）**极其重要！长度放宽至 150-250 字。** 他依据的特定数据是什么？底层逻辑站得住脚吗？对于 FEMA 必须包含当天具体的权威数值或标注 N/A。
    - "suggestion": 给出非常具体的交易动作或代码建议。

    绝不允许交白卷，必须生成至少 10-15 条深度记录。直接输出 JSON 数组，不要任何 Markdown 的 ```json 标记。
    """
    
    # 调低 temperature 保证输出的严谨性与逻辑的连贯性
    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2, 
        ),
    )
    
    return json.loads(response.text)

def push_to_notion(data_list):
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    filtered_data = [item for item in data_list if item.get("Name_of_KOL") not in ["AI Assistant", "AI", "System", None, ""]]
    
    for item in filtered_data:
        try:
            kol_name = str(item.get("Name_of_KOL", "Unknown")).replace(",", " ").strip()
            title = str(item.get("Title", f"{kol_name} 的深度观点")).strip()
            comments = str(item.get("comments", "")).strip()[:2000] 
            suggestion = str(item.get("suggestion", "")).strip()[:2000]

            properties = {
                "Name": {"title": [{"text": {"content": title}}]},
                "Date": {"date": {"start": today_str}},
                "comments": {"rich_text": [{"text": {"content": comments}}]},
                "suggestion": {"rich_text": [{"text": {"content": suggestion}}]}
            }
            
            if kol_name and kol_name != "Unknown":
                properties["Name of KOL"] = {"select": {"name": kol_name}}
                
            kol_view = str(item.get("KOL_or_IB_View", "")).replace(",", " ").strip()
            if kol_view:
                properties["KOL or IB View"] = {"select": {"name": kol_view}}
                
            sector = str(item.get("Sector", "")).replace(",", " ").strip()
            if sector:
                properties["Sector"] = {"select": {"name": sector}}
                
            detail = str(item.get("Detail_Sector", "")).replace(",", " ").strip()
            if detail:
                properties["Detail Sector"] = {"select": {"name": detail}}

            notion.pages.create(parent={"database_id": DATABASE_ID}, properties=properties)
            print(f"✅ 成功深度写入: [{kol_name}] {title}")
            
        except Exception as e:
            print(f"❌ 写入失败 [{item.get('Name_of_KOL')}]: {str(e)}")

if __name__ == "__main__":
    print("开始执行深度情报挖掘与逻辑推演...")
    insights = fetch_kol_insights()
    print(f"情报获取成功，开始写入 Notion 数据库...")
    push_to_notion(insights)
    print("今日深度投研任务执行完毕！")
