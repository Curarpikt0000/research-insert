import json
import os

def build_dashboard():
    file_name = "kol_history_data.json"
    if not os.path.exists(file_name):
        print("未找到历史数据，跳过生成。")
        return
        
    with open(file_name, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    json_str = json.dumps(data, ensure_ascii=False)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>KOL 投研情绪雷达</title>
        <style>
            :root {{ --bg: #121212; --panel: #1e1e1e; --text: #e0e0e0; --bull: #00fa9a; --bear: #ff4757; --neutral: #888; }}
            body {{ background-color: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 20px; margin: 0; }}
            h2 {{ font-size: 1.5rem; border-bottom: 1px solid #333; padding-bottom: 10px; margin-top: 0; }}
            .controls {{ display: flex; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; }}
            select {{ background: #2a2a2a; color: white; border: 1px solid #444; padding: 8px 12px; border-radius: 6px; outline: none; font-size: 14px; cursor: pointer; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }}
            .card {{ background: var(--panel); padding: 16px; border-radius: 8px; border-left: 4px solid var(--neutral); box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: transform 0.2s; }}
            .card:hover {{ transform: translateY(-2px); }}
            .card.bullish {{ border-left-color: var(--bull); }}
            .card.bearish {{ border-left-color: var(--bear); }}
            .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
            .name {{ font-weight: bold; font-size: 1.1rem; }}
            .date {{ font-size: 0.8rem; color: #888; }}
            .tags {{ display: flex; gap: 8px; margin-bottom: 12px; font-size: 0.75rem; }}
            .tag {{ background: #333; padding: 3px 8px; border-radius: 4px; }}
            .tag.bull-tag {{ color: var(--bull); background: rgba(0, 250, 154, 0.1); }}
            .tag.bear-tag {{ color: var(--bear); background: rgba(255, 71, 87, 0.1); }}
            .title {{ font-size: 0.95rem; line-height: 1.5; color: #ccc; margin-bottom: 10px; }}
            .suggestion {{ font-size: 0.85rem; color: #aaa; background: #252525; padding: 8px; border-radius: 4px; border-left: 2px solid #555; }}
            .stats {{ margin-bottom: 20px; font-size: 0.9rem; color: #888; }}
        </style>
    </head>
    <body>
        <h2>📊 华尔街 KOL 多空情绪与逻辑追踪</h2>
        
        <div class="controls">
            <select id="timeF" onchange="render()">
                <option value="all">时间跨度: 全部</option>
                <option value="24h" selected>过去 24 小时</option>
                <option value="7d">过去 7 天</option>
            </select>
            <select id="sectorF" onchange="render()">
                <option value="all">板块: 全部监控区</option>
                <option value="Precious Metals">核心宏观与贵金属</option>
                <option value="Tech">科技 / AI / 策略</option>
                <option value="Energy">能源 / 大宗商品</option>
            </select>
            <select id="sentimentF" onchange="render()">
                <option value="all">情绪: 多空全景</option>
                <option value="多">看多阵营</option>
                <option value="空">看空阵营</option>
            </select>
        </div>

        <div class="stats" id="statsBar">加载中...</div>
        <div class="grid" id="board"></div>

        <script>
            const db = {json_str};
            
            function render() {{
                const t = document.getElementById('timeF').value;
                const s = document.getElementById('sectorF').value;
                const emo = document.getElementById('sentimentF').value;
                const board = document.getElementById('board');
                
                board.innerHTML = '';
                let bullCount = 0, bearCount = 0, total = 0;

                db.forEach(item => {{
                    // 容错处理
                    const sector = item.Sector || 'Macro';
                    const sentiment = item.Sentiment || '中立';
                    const time = item.Timeframe || '24h';

                    if (t !== 'all' && time !== t) return;
                    if (s !== 'all' && !sector.includes(s)) return;
                    if (emo !== 'all' && !sentiment.includes(emo)) return;

                    total++;
                    let isBull = sentiment.includes('多');
                    let isBear = sentiment.includes('空');
                    
                    if(isBull) bullCount++;
                    if(isBear) bearCount++;

                    let borderCls = isBull ? 'bullish' : (isBear ? 'bearish' : '');
                    let tagCls = isBull ? 'bull-tag' : (isBear ? 'bear-tag' : '');

                    board.innerHTML += `
                        <div class="card ${{borderCls}}">
                            <div class="card-header">
                                <span class="name">${{item.Name_of_KOL || '官方数据'}}</span>
                                <span class="date">${{item.Date}}</span>
                            </div>
                            <div class="tags">
                                <span class="tag">${{sector}}</span>
                                <span class="tag ${{tagCls}}">${{sentiment}}</span>
                            </div>
                            <div class="title">${{item.Title || ''}}</div>
                            <div class="suggestion">💡 ${{item.suggestion || '持续观察'}}</div>
                        </div>
                    `;
                }});

                document.getElementById('statsBar').innerText = 
                    `当前视图包含 ${{total}} 条研报记录 | 看多: ${{bullCount}} | 看空: ${{bearCount}}`;
            }}
            
            render(); // 页面加载完立即执行
        </script>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ Dashboard 生成完毕！")

if __name__ == "__main__":
    build_dashboard()
