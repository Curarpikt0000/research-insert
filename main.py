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
    """调用 Gemini API 获取每个 KOL 的独立总结并强制返回 JSON 数组"""
    prompt = """
    全网搜索并总结过去24小时内全球顶级投行及核心KOL的最新研报。
    重点覆盖人物/机构：
    1. 核心宏观/贵金属：Daniel Oliver, Jason Hunter, David Morgan, Rick Rule, Peter Schiff, Zoltan Pozsar, Steve Penny, Peter Krauth, Craig Hemke, Robert Kiyosaki, Willem Middelkoop, David Garofalo.
    2. 科技/AI/策略：Dan Ives, Michael Hartnett, Cathie Wood, Raoul Pal.
    3. 能源/大宗：Eric Nuttall, Doomberg, Rory Johnston, Kuppy.
    4. 投行：Goldman Sachs, Morgan Stanley, Citi, UBS.
    
    【极其重要的格式要求】：
    请你针对每一位有最新观点的人物或机构，生成一个独立的 JSON Object。最终输出必须是一个包含多条记录的严格 JSON 数组 (Array)。例如：如果你总结了10个人的观点，就必须输出包含10个Object的Array。
    
    每个 Object 必须精确包含以下字段：
    - "Name": 人物或机构名称 (String)
    - "KOL_or_IB_View": 严格填入 "KOL" 或 "IB View" (String)
    - "Sector": 所属大板块，尽量精简，如 "Macro", "Precious Metals", "Tech", "Energy" (String)
    - "Detail_Sector": 细分板块，如 "Silver Miners", "AI Software" (String)
    - "comments": 核心逻辑链与观点，控制在50字内 (String)
    - "suggestion": 交易建议与代码 (String)
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    
    return json.loads(response.text)

def push_to_notion(data_list):
    """将解析后的 JSON 数据分条（每人一行）写入 Notion 表格"""
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    for item in data_list:
        try:
            # 基础文本与日期属性
            properties = {
                "Name": {"title": [{"text": {"content": item.get("Name", "Unknown")}}]  },
                "Date": {"date": {"start": today_str}},
                "comments": {"rich_text": [{"text": {"content": item.get("comments", "")}}]},
                "suggestion": {"rich_text": [{"text": {"content": item.get("suggestion", "")}}]}
            }
            
            # 针对 Select (单选标签) 类型的字段特殊处理
            # 只有当 AI 生成了该字段的值时，才向 Notion 写入该 Select 标签，避免空值报错
            if item.get("KOL_or_IB_View"):
                properties["KOL or IB View"] = {"select": {"name": str(item.get("KOL_or_IB_View"))}}
                
            if item.get("Sector"):
                properties["Sector"] = {"select": {"name": str(item.get("Sector"))}}
                
            if item.get("Detail_Sector"):
                properties["Detail Sector"] = {"select": {"name": str(item.get("Detail_Sector"))}}

            notion.pages.create(
                parent={"database_id": DATABASE_ID},
                properties=properties
            )
            print(f"✅ 成功写入: {item.get('Name')}")
        except Exception as e:
            print(f"❌ 写入失败 {item.get('Name')}: {str(e)}")

if __name__ == "__main__":
    print("开始获取全球研报与KOL观点...")
    insights = fetch_kol_insights()
    print(f"获取成功，共解析到 {len(insights)} 条独立数据。开始写入 Notion...")
    push_to_notion(insights)
    print("今日任务执行完毕！")
