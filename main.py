import os
import json
import datetime
import google.generativeai as genai
from notion_client import Client

# 1. 初始化环境变量与客户端
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

notion = Client(auth=NOTION_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

def fetch_kol_insights():
    """调用 Gemini API 获取总结并强制返回 JSON 格式"""
    # 这里使用的是您的原始设定，要求返回严格的 JSON 数组
    prompt = """
    全网搜索并总结过去24小时内全球顶级投行及核心KOL的最新研报。
    重点覆盖人物/机构：
    1. 核心宏观/贵金属：Daniel Oliver, Jason Hunter, David Morgan, Rick Rule, Peter Schiff, Zoltan Pozsar, Steve Penny, Peter Krauth, Craig Hemke, Robert Kiyosaki, Willem Middelkoop, David Garofalo.
    2. 科技/AI/策略：Dan Ives, Michael Hartnett, Cathie Wood, Raoul Pal.
    3. 能源/大宗：Eric Nuttall, Doomberg, Rory Johnston, Kuppy.
    4. 投行：Goldman Sachs, Morgan Stanley, Citi, UBS.
    
    请输出为一个严格的 JSON 数组 (Array of Objects)，不要包含任何 Markdown 格式的 ```json 标记，直接输出纯 JSON。
    每个 Object 必须包含以下字段：
    - "Name": 人物或机构名称 (String)
    - "KOL_or_IB_View": 填 "KOL" 或 "IB View" (String)
    - "Sector": 所属大板块，如 "Macro", "Precious Metals", "Tech", "Energy" (String)
    - "Detail_Sector": 细分板块，如 "Silver Miners", "AI Software" (String)
    - "comments": 核心逻辑链与观点，控制在50字内 (String)
    - "suggestion": 交易建议与代码 (String)
    """
    
    # 强制模型输出 JSON 格式
    model = genai.GenerativeModel(
        'gemini-1.5-pro-latest',
        generation_config={"response_mime_type": "application/json"}
    )
    
    response = model.generate_content(prompt)
    return json.loads(response.text)

def push_to_notion(data_list):
    """将解析后的 JSON 数据逐行写入 Notion 表格"""
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    for item in data_list:
        try:
            notion.pages.create(
                parent={"database_id": DATABASE_ID},
                properties={
                    # 确保这里的属性名与您 Notion 表头的精确名称一致（区分大小写和空格）
                    "Name": {"title": [{"text": {"content": item.get("Name", "Unknown")}}]},
                    "KOL or IB View": {"rich_text": [{"text": {"content": item.get("KOL_or_IB_View", "")}}]},
                    "Date": {"date": {"start": today_str}},
                    "Sector": {"rich_text": [{"text": {"content": item.get("Sector", "")}}]},
                    "Detail Sector": {"rich_text": [{"text": {"content": item.get("Detail_Sector", "")}}]},
                    "comments": {"rich_text": [{"text": {"content": item.get("comments", "")}}]},
                    "suggestion": {"rich_text": [{"text": {"content": item.get("suggestion", "")}}]}
                }
            )
            print(f"成功写入: {item.get('Name')}")
        except Exception as e:
            print(f"写入失败 {item.get('Name')}: {str(e)}")

if __name__ == "__main__":
    print("开始获取全球研报与KOL观点...")
    insights = fetch_kol_insights()
    print(f"获取成功，共解析到 {len(insights)} 条数据。开始写入 Notion...")
    push_to_notion(insights)
    print("今日任务执行完毕！")
