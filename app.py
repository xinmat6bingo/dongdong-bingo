import re
import pandas as pd
import streamlit as st
from collections import Counter

from database import init_db, save_draw, load_draws
from crawler import update_latest
from predictor import (
    hot_cold,
    zone_analysis,
    odd_even_big_small,
    ab_transfer,
    final_recommend,
    super_mother,
    pair_frequency,
    triple_frequency,
    latest_pair_match,
    latest_triple_match
)

st.set_page_config(
    page_title="東東賓果分析系統",
    layout="wide"
)

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.main-title {
    font-size: 46px;
    font-weight: 900;
    color: #1f2937;
    margin-bottom: 0;
}

.sub-title {
    font-size: 16px;
    color: #6b7280;
    margin-bottom: 28px;
}

.card {
    background: #ffffff;
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.06);
    border: 1px solid #e5e7eb;
}

.metric-card {
    background: linear-gradient(135deg, #f8fafc, #eef2ff);
    border-radius: 18px;
    padding: 20px;
    border: 1px solid #e5e7eb;
}

.big-number {
    font-size: 32px;
    font-weight: 900;
    color: #111827;
}

.label {
    font-size: 15px;
    color: #6b7280;
}

.recommend {
    font-size: 28px;
    font-weight: 900;
    letter-spacing: 4px;
}

.good {
    color: #047857;
}

.blue {
    color: #1d4ed8;
}

.orange {
    color: #c2410c;
}

.ball {
    display: inline-block;
    padding: 6px 11px;
    margin: 4px;
    border-radius: 999px;
    background: #eef2ff;
    color: #1f2937;
    font-weight: 700;
}

.note {
    background: #fefce8;
    border: 1px solid #fde68a;
    padding: 16px;
    border-radius: 14px;
    color: #854d0e;
}
</style>
""", unsafe_allow_html=True)

init_db()

st.markdown('<div class="main-title">🎯 東東賓果分析系統</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">即時更新｜12/20/30/50/100期｜四星五星八星｜A→B｜二同三同組合｜超級獎號母盤</div>',
    unsafe_allow_html=True
)

top1, top2, top3 = st.columns([1, 1, 2])

with top1:
    if st.button("🔄 更新最新開獎", use_container_width=True):
        try:
            count = update_latest()
            st.success(f"已更新 {count} 筆")
        except Exception as e:
            st.error(f"更新失敗：{e}")

with top2:
    period_count = st.selectbox(
        "分析期數",
        [12, 20, 30, 50, 100],
        index=1
    )

with top3:
    st.info("建議每次分析前先按一次更新最新開獎。")

with st.expander("➕ 手動新增一期資料"):
    period = st.text_input("期別，例如 115030413")
    draw_time = st.text_input("時間，例如 20:50")
    nums_text = st.text_area("20個號碼，用逗號或空白分隔")
    super_num = st.number_input("超級獎號", 1, 80, 1)

    if st.button("儲存手動資料"):
        nums = [int(x) for x in re.findall(r"\d+", nums_text)]

        if len(nums) != 20:
            st.error("號碼必須剛好 20 個")
        else:
            save_draw(period, draw_time, nums, super_num)
            st.success("已儲存")
            st.rerun()

df = load_draws()

if df.empty:
    st.warning("目前沒有資料，請先按『更新最新開獎』。")
    st.stop()

hot, cold, counter = hot_cold(df, period_count)
zones = zone_analysis(counter)
odd, even, small, big = odd_even_big_small(df, period_count)
rec4, rec5, rec8, total_score = final_recommend(df, period_count)

latest = df.iloc[0]

st.markdown("## 📌 最新開獎")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">最新期別</div>
        <div class="big-number">{latest["期別"]}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">開獎時間</div>
        <div class="big-number">{latest["時間"]}</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">超級獎號</div>
        <div class="big-number">{latest["超級獎號"]:02d}</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">資料筆數</div>
        <div class="big-number">{len(df)}</div>
    </div>
    """, unsafe_allow_html=True)

balls = " ".join([f'<span class="ball">{x:02d}</span>' for x in latest["號碼"]])
st.markdown(f"""
<div class="card">
    <h3>最新開獎號碼</h3>
    {balls}
</div>
""", unsafe_allow_html=True)

st.markdown("## 🎯 今日推薦")

r1, r2, r3 = st.columns(3)

with r1:
    st.markdown(f"""
    <div class="card">
        <h3>四星主攻</h3>
        <div class="recommend good">{" ".join(f"{x:02d}" for x in rec4)}</div>
    </div>
    """, unsafe_allow_html=True)

with r2:
    st.markdown(f"""
    <div class="card">
        <h3>五星穩定</h3>
        <div class="recommend blue">{" ".join(f"{x:02d}" for x in rec5)}</div>
    </div>
    """, unsafe_allow_html=True)

with r3:
    st.markdown(f"""
    <div class="card">
        <h3>八星包牌</h3>
        <div class="recommend orange">{" ".join(f"{x:02d}" for x in rec8)}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("## ⚖️ 盤型判斷")

p1, p2, p3, p4 = st.columns(4)

with p1:
    st.metric("單數", odd)
with p2:
    st.metric("雙數", even)
with p3:
    st.metric("小號 01-40", small)
with p4:
    st.metric("大號 41-80", big)

c1, c2 = st.columns(2)

with c1:
    if odd > even:
        st.success("單雙建議：偏單")
    elif even > odd:
        st.success("單雙建議：偏雙")
    else:
        st.info("單雙建議：均衡")

with c2:
    if big > small:
        st.success("大小建議：偏大")
    elif small > big:
        st.success("大小建議：偏小")
    else:
        st.info("大小建議：均衡")

st.markdown("## 🔥 熱號 / ❄️ 冷號")

h1, h2 = st.columns(2)

with h1:
    hot_df = pd.DataFrame(hot, columns=["號碼", "出現次數"])
    st.dataframe(hot_df, use_container_width=True, hide_index=True)

with h2:
    cold_df = pd.DataFrame(cold, columns=["號碼", "出現次數"])
    st.dataframe(cold_df, use_container_width=True, hide_index=True)

st.markdown("## 📊 區段分布")

zone_df = pd.DataFrame(list(zones.items()), columns=["區段", "次數"])
st.bar_chart(zone_df.set_index("區段"))

st.markdown("## 🧠 綜合權重排行")

score_df = pd.DataFrame(
    [(num, round(score, 2)) for num, score in total_score.most_common(20)],
    columns=["號碼", "綜合分數"]
)

st.dataframe(score_df, use_container_width=True, hide_index=True)

st.markdown("## 🔬 進階分析")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "A→B 轉移",
    "二同組合排行",
    "三同組合排行",
    "最新期二同命中",
    "最新期三同命中",
    "超級獎號母盤"
])

with tab1:
    st.markdown("""
    <div class="note">
    A→B 轉移：統計近 N 期中，上一期開出後，下一期最常接續出現的號碼。
    </div>
    """, unsafe_allow_html=True)

    ab = ab_transfer(df, period_count)
    st.dataframe(
        pd.DataFrame(ab.most_common(20), columns=["號碼", "轉移次數"]),
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.markdown("""
    <div class="note">
    二同組合排行：統計近 N 期中，兩個號碼同一期一起出現的次數。
    </div>
    """, unsafe_allow_html=True)

    pair_counter = pair_frequency(df, period_count)

    pair_rows = []
    for pair, cnt in pair_counter.most_common(100):
        pair_rows.append({
            "二同組合": f"{pair[0]:02d} + {pair[1]:02d}",
            "出現次數": cnt
        })

    st.dataframe(
        pd.DataFrame(pair_rows),
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.markdown("""
    <div class="note">
    三同組合排行：統計近 N 期中，三個號碼同一期一起出現的次數。
    </div>
    """, unsafe_allow_html=True)

    triple_counter = triple_frequency(df, period_count)

    triple_rows = []
    for triple, cnt in triple_counter.most_common(100):
        triple_rows.append({
            "三同組合": f"{triple[0]:02d} + {triple[1]:02d} + {triple[2]:02d}",
            "出現次數": cnt
        })

    st.dataframe(
        pd.DataFrame(triple_rows),
        use_container_width=True,
        hide_index=True
    )

with tab4:
    st.markdown("""
    <div class="note">
    最新期二同命中：只看最新一期的20個號碼，列出其中二同組合在近 N 期出現過幾次。
    </div>
    """, unsafe_allow_html=True)

    rows = latest_pair_match(df, period_count)

    st.dataframe(
        pd.DataFrame(rows).head(100),
        use_container_width=True,
        hide_index=True
    )

with tab5:
    st.markdown("""
    <div class="note">
    最新期三同命中：只看最新一期的20個號碼，列出其中三同組合在近 N 期出現過幾次。
    </div>
    """, unsafe_allow_html=True)

    rows = latest_triple_match(df, period_count)

    st.dataframe(
        pd.DataFrame(rows).head(100),
        use_container_width=True,
        hide_index=True
    )

with tab6:
    target_super = st.number_input(
        "輸入超級獎號",
        min_value=1,
        max_value=80,
        value=int(latest["超級獎號"])
    )

    if st.button("執行母盤分析"):
        mother, results = super_mother(df, target_super)

        if mother is None:
            st.warning("資料不足，至少需要同一個超級獎號出現 2 次以上。")
        else:
            mother_text = " ".join(f"{x:02d}" for x in mother)
            st.success(f"母盤：{mother_text}")

            rows = []
            rank = Counter()

            for r in results:
                for x in r["重複號碼"]:
                    rank[x] += 1

                rows.append({
                    "超級獎號期別": r["超級獎號期別"],
                    "下一期期別": r["下一期期別"],
                    "重複顆數": r["重複顆數"],
                    "重複號碼": " ".join(f"{x:02d}" for x in r["重複號碼"])
                })

            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            st.subheader("母盤重複排行")
            st.dataframe(
                pd.DataFrame(rank.most_common(), columns=["號碼", "重複次數"]),
                use_container_width=True,
                hide_index=True
            )

with st.expander("📋 查看最近開獎資料"):
    st.dataframe(
        df[["期別", "時間", "號碼", "超級獎號"]].head(100),
        use_container_width=True,
        hide_index=True
    )

st.caption("提醒：賓果為隨機遊戲，本工具只做資料分析，不保證中獎。")