import os
import datetime
from notion_client import Client

# 直接读取您 GitHub Secrets 里的配置，安全不泄露
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

# 之前我们讨论过的核心精华数据
historical_data = [
    {
        "Name": "Rick Rule", "KOL_or_IB_View": "KOL", "Sector": "Precious Metals", "Detail_Sector": "Silver Miners",
        "comments": "实物白银投机结束，全面转向矿业股。白银$90下的矿企经营杠杆尚未被华尔街定价。", "suggestion": "做多矿业股: SILJ, PAAS"
    },
    {
        "Name": "David Garofalo", "KOL_or_IB_View": "KOL", "Sector": "Precious Metals", "Detail_Sector": "Royalty Companies",
        "comments": "矿业面临史诗级产量悬崖。传统开采成本失控，特许权模型是唯一能纯享金属涨幅且屏蔽通胀的载体。", "suggestion": "强烈看多特许权: GROY, WPM"
    },
    {
        "Name": "Craig Hemke", "KOL_or_IB_View": "KOL", "Sector": "Precious Metals", "Detail_Sector": "COMEX Delivery",
        "comments": "3月交割季面临结构性压力，注册库存跌破8700万盎司。多头展期至5月，纸面与实物脱节达到极限。", "suggestion": "买入纯实物: PSLV"
    },
    {
        "Name": "Willem Middelkoop", "KOL_or_IB_View": "KOL", "Sector": "Macro", "Detail_Sector": "Global Reset",
        "comments": "美联储亏损超$2450亿，唯一的数学解是大幅重估黄金价格以修复资产负债表（大重置）。", "suggestion": "长线实金，关注初级探矿商"
    },
    {
        "Name": "Robert Kiyosaki", "KOL_or_IB_View": "KOL", "Sector": "Macro", "Detail_Sector": "Fiat Crisis",
        "comments": "存现金非常愚蠢。利用低息信贷购买白银和比特币，是做空崩溃法币系统的最佳策略。", "suggestion": "看空美元，买入 BTC, PHYS"
    },
    {
        "Name": "Michael Hartnett", "KOL_or_IB_View": "IB View", "Sector": "Macro", "Detail_Sector": "Liquidity",
        "comments": "BofA牛熊指标达9.3极端看涨。AI概念股极度拥挤，资金正加速流向新兴市场和物理资产。", "suggestion": "看空纳指，买入新兴市场 EEM"
    },
    {
        "Name": "Eric Nuttall", "KOL_or_IB_View": "KOL", "Sector": "Energy", "Detail_Sector": "Natural Gas",
        "comments": "天然气不仅受地缘溢价支撑，更是AI算力竞赛不可或缺的物理护城河，长寿命资产迎重估。", "suggestion": "做多加股气权: EXE, TOU.TO"
    },
    {
        "Name": "Kuppy (Doomberg)", "KOL_or_IB_View": "KOL", "Sector": "Energy", "Detail_Sector": "Uranium",
        "comments": "算力竞赛实质上是电力竞赛。科技巨头直接下场购电，彻底扭转了铀矿的长期合同定价权。", "suggestion": "核心持仓铀矿: CCJ"
    }
]

def push_to_notion():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    print("开始执行一次性数据导入...")
    for item in historical_data:
        try:
            properties = {
                "Name": {"title": [{"text": {"content": item["Name"]}}]},
                "Date": {"date": {"start": today_str}},
                "comments": {"rich_text": [{"text": {"content": item["comments"]}}]},
                "suggestion": {"rich_text": [{"text": {"content": item["suggestion"]}}]}
            }
            if item.get("KOL_or_IB_View"): properties["KOL or IB View"] = {"select": {"name": str(item.get("KOL_or_IB_View"))}}
            if item.get("Sector"): properties["Sector"] = {"select": {"name": str(item.get("Sector"))}}
            if item.get("Detail_Sector"): properties["Detail Sector"] = {"select": {"name": str(item.get("Detail_Sector"))}}

            notion.pages.create(parent={"database_id": DATABASE_ID}, properties=properties)
            print(f"✅ 成功导入: {item['Name']}")
        except Exception as e:
            print(f"❌ 导入失败 {item['Name']}: {str(e)}")
    print("🎉 一次性历史数据导入完毕！请前往 Notion 查看。")

if __name__ == "__main__":
