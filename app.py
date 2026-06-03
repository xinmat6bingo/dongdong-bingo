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
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-left: 0.8rem;
    padding-right: 0.8rem;
    padding-bottom: 3rem;
    max-width: 760px;
}

.main-title {
    font-size: 34px;
    font-weight: 900;
    color: #111827;
    line-height: 1.25;
    margin-bottom: 4px;
}

.sub-title {
    font-size: 14px;
    color: #6b7280;
    line-height: 1.6;
    margin-bottom: 18px;
}

.section-title {
    font-size: 24px;
    font-weight: 900;
    margin-top: 26px;
    margin-bottom: 12px;
    color: #111827;
}

.card {
    background: #ffffff;
    border-radius: 20px;
    padding: 18px;
    margin-bottom: 14px;
    box-shadow: 0 5px 18px rgba(0,0,0,0.06);
    border: 1px solid #e5e7eb;
}

.dark-card {
    background: linear-gradient(135deg, #111827, #1f2937);
    color: white;
    border-radius: 22px;
    padding: 20px;
    margin-bottom: 14px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}

.info-row {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    margin-top: 8px;
}

.info-box {
    flex: 1;
    background: #f3f4f6;
    border-radius: 16px;
    padding: 12px;
    text-align: center;
}

.info-label {
    font-size: 12px;
    color: #6b7280;
    margin-bottom: 4px;
}

.info-value {
    font-size: 20px;
    font-weight: 900;
    color: #111827;
}

.ball {
    display: inline-block;
    min-width: 34px;
    padding: 7px 8px;
    margin: 4px;
    border-radius: 999px;
    background: #eef2ff;
    color: #1f2937;
    font-weight: 800;
    text-align: center;
    font-size: 15px;
}

.super-ball {
    display: inline-block;
    min-width: 42px;
    padding: 10px;
    border-radius: 999px;
    background: #f97316;
    color: white;
    font-size: 22px;
    font-weight: 900;
    text-align: center;
}

.recommend-card {
    border-radius: 22px;
    padding: 18px;
    margin-bottom: 14px;
    color: white;
}

.rec-green {
    background: linear-gradient(135deg, #059669, #047857);
}

.rec-blue {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
}

.rec-orange {
    background: linear-gradient(135deg, #f97316, #c2410c);
}

.rec-title {
    font-size: 16px;
    font-weight: 700;
    opacity: 0.9;
}

.rec-number {
    font-size: 32px;
    font-weight: 900;
    letter-spacing: 5px;
    margin-top: 8px;
    line-height: 1.4;
}

.note {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    color: #9a3412;
    border-radius: 16px;
    padding: 14px;
    font-size: 14px;
    line-height: 1.6;
    margin-bottom: 12px;
}

.small-note {
    font-size: 13px;
    color: #6b7280;
    line-height: 1.6;
}

div[data-testid="stMetric"] {
    background: #ffffff;
    padding: 14px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 14px rgba(0,0,0,0.04);
}

.stButton > button {
    border-radius: 16px;
    height: 48px;
    font-weight: 800;
}

div[data-baseweb="select"] {
    border-radius: 16px;
}

@media (max-width: 600px) {
    .main-title {
        font-size: 30px;
    }

    .section-title {
        font-size: 22px;
    }

    .rec-number {
        font-size: 28px;
        letter-spacing: 3px;
    }

    .ball {
        min-width: 31px;
        padding: 6px 7px;
        font-size: 14px;
    }

    .info-row {
        flex-direction: column;
    }
}
</style>
""", unsafe_allow_html=True)

init_db()

def num_text(nums):
    return " ".join(f"{x:02d}" for x in nums)

def ball_html(nums):
    return " ".join(f'<span class="ball">{x:02d}</span>' for x in nums)

st.markdown('<div class="main-title">🎯 東東賓果分析系統</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">手機版介面｜即時更新｜四星 / 五星 / 八星｜二同三同｜母盤分析</div>',
    unsafe_allow_html=True
)

# 控制區
with st.container():
    c1, c2 = st.columns([1, 1])

    with c1:
        update_btn = st.button("🔄 更新開獎", use_container_width=True)

    with c2:
        period_count = st.selectbox(
            "分析期數",
            [12, 20, 30, 50, 100],
            index=1
        )

    if update_btn:
        try:
            count = update_latest()
            st.success(f"已更新 {count} 筆")
        except Exception as e:
            st.error(f"更新失敗：{e}")

# 手動新增
with st.expander("➕ 手動新增一期"):
    period = st.text_input("期別，例如 115030413")
    draw_time = st.text_input("時間，例如 20:50")
    nums_text = st.text_area("20個號碼，用逗號或空白分隔")
    super_num = st.number_input("超級獎號", 1, 80, 1)

    if st.button("儲存手動資料", use_container_width=True):
        nums = [int(x) for x in re.findall(r"\d+", nums_text)]

        if len(nums) != 20:
            st.error("號碼必須剛好 20 個")
        else:
            save_draw(period, draw_time, nums, super_num)
            st.success("已儲存")
            st.rerun()

df = load_draws()

if df.empty:
    st.warning("目前沒有資料，請先按『更新開獎』。")
    st.stop()

hot, cold, counter = hot_cold(df, period_count)
zones = zone_analysis(counter)
odd, even, small, big = odd_even_big_small(df, period_count)
rec4, rec5, rec8, total_score = final_recommend(df, period_count)

latest = df.iloc[0]

# 最新開獎
st.markdown('<div class="section-title">📌 最新開獎</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="dark-card">
    <div style="font-size:14px;opacity:.8;">最新期別</div>
    <div style="font-size:30px;font-weight:900;">{latest["期別"]}</div>

    <div class="info-row">
        <div class="info-box">
            <div class="info-label">時間</div>
            <div class="info-value">{latest["時間"]}</div>
        </div>
        <div class="info-box">
            <div class="info-label">超級獎號</div>
            <div class="super-ball">{latest["超級獎號"]:02d}</div>
        </div>
        <div class="info-box">
            <div class="info-label">資料筆數</div>
            <div class="info-value">{len(df)}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="card">
    <div style="font-size:17px;font-weight:900;margin-bottom:10px;">開獎號碼</div>
    {ball_html(latest["號碼"])}
</div>
""", unsafe_allow_html=True)

# 推薦
st.markdown('<div class="section-title">🎯 推薦組合</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="recommend-card rec-green">
    <div class="rec-title">四星主攻</div>
    <div class="rec-number">{num_text(rec4)}</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="recommend-card rec-blue">
    <div class="rec-title">五星穩定</div>
    <div class="rec-number">{num_text(rec5)}</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="recommend-card rec-orange">
    <div class="rec-title">八星包牌</div>
    <div class="rec-number">{num_text(rec8)}</div>
</div>
""", unsafe_allow_html=True)

# 盤型
st.markdown('<div class="section-title">⚖️ 盤型判斷</div>', unsafe_allow_html=True)

m1, m2 = st.columns(2)
m3, m4 = st.columns(2)

with m1:
    st.metric("單數", odd)
with m2:
    st.metric("雙數", even)
with m3:
    st.metric("小號 01-40", small)
with m4:
    st.metric("大號 41-80", big)

if odd > even:
    st.success("單雙建議：偏單")
elif even > odd:
    st.success("單雙建議：偏雙")
else:
    st.info("單雙建議：均衡")

if big > small:
    st.success("大小建議：偏大")
elif small > big:
    st.success("大小建議：偏小")
else:
    st.info("大小建議：均衡")

# 分析總覽
st.markdown('<div class="section-title">📊 分析總覽</div>', unsafe_allow_html=True)

tab_hot, tab_zone, tab_score = st.tabs(["🔥 熱冷號", "📊 區段", "🧠 權重"])

with tab_hot:
    hot_df = pd.DataFrame(hot, columns=["號碼", "出現次數"])
    cold_df = pd.DataFrame(cold, columns=["號碼", "出現次數"])

    st.markdown("### 🔥 熱門號碼")
    st.dataframe(hot_df, use_container_width=True, hide_index=True)

    st.markdown("### ❄️ 冷門號碼")
    st.dataframe(cold_df, use_container_width=True, hide_index=True)

with tab_zone:
    zone_df = pd.DataFrame(list(zones.items()), columns=["區段", "次數"])
    st.bar_chart(zone_df.set_index("區段"))

with tab_score:
    score_df = pd.DataFrame(
        [(num, round(score, 2)) for num, score in total_score.most_common(20)],
        columns=["號碼", "綜合分數"]
    )
    st.dataframe(score_df, use_container_width=True, hide_index=True)

# 進階分析
st.markdown('<div class="section-title">🔬 進階分析</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "A→B",
    "二同",
    "三同",
    "母盤"
])

with tab1:
    st.markdown('<div class="note">A→B：統計近 N 期中，下一期常接續出現的號碼。</div>', unsafe_allow_html=True)

    ab = ab_transfer(df, period_count)
    st.dataframe(
        pd.DataFrame(ab.most_common(30), columns=["號碼", "轉移次數"]),
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.markdown('<div class="note">二同：統計兩個號碼同一期一起出現的次數。</div>', unsafe_allow_html=True)

    pair_counter = pair_frequency(df, period_count)
    pair_rows = []

    for pair, cnt in pair_counter.most_common(100):
        pair_rows.append({
            "二同組合": f"{pair[0]:02d} + {pair[1]:02d}",
            "出現次數": cnt
        })

    st.dataframe(pd.DataFrame(pair_rows), use_container_width=True, hide_index=True)

    st.markdown("### 最新期二同")
    latest_pair_rows = latest_pair_match(df, period_count)
    st.dataframe(pd.DataFrame(latest_pair_rows).head(80), use_container_width=True, hide_index=True)

with tab3:
    st.markdown('<div class="note">三同：統計三個號碼同一期一起出現的次數。</div>', unsafe_allow_html=True)

    triple_counter = triple_frequency(df, period_count)
    triple_rows = []

    for triple, cnt in triple_counter.most_common(100):
        triple_rows.append({
            "三同組合": f"{triple[0]:02d} + {triple[1]:02d} + {triple[2]:02d}",
            "出現次數": cnt
        })

    st.dataframe(pd.DataFrame(triple_rows), use_container_width=True, hide_index=True)

    st.markdown("### 最新期三同")
    latest_triple_rows = latest_triple_match(df, period_count)
    st.dataframe(pd.DataFrame(latest_triple_rows).head(80), use_container_width=True, hide_index=True)

with tab4:
    target_super = st.number_input(
        "輸入超級獎號",
        min_value=1,
        max_value=80,
        value=int(latest["超級獎號"])
    )

    if st.button("執行母盤分析", use_container_width=True):
        mother, results = super_mother(df, target_super)

        if mother is None:
            st.warning("資料不足，至少需要同一個超級獎號出現 2 次以上。")
        else:
            st.success(f"母盤：{num_text(mother)}")

            rows = []
            rank = Counter()

            for r in results:
                for x in r["重複號碼"]:
                    rank[x] += 1

                rows.append({
                    "超級獎號期別": r["超級獎號期別"],
                    "下一期期別": r["下一期期別"],
                    "重複顆數": r["重複顆數"],
                    "重複號碼": num_text(r["重複號碼"])
                })

            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            st.markdown("### 母盤重複排行")
            st.dataframe(
                pd.DataFrame(rank.most_common(), columns=["號碼", "重複次數"]),
                use_container_width=True,
                hide_index=True
            )

with st.expander("📋 最近開獎資料"):
    st.dataframe(
        df[["期別", "時間", "號碼", "超級獎號"]].head(100),
        use_container_width=True,
        hide_index=True
    )

st.markdown('<div class="small-note">提醒：賓果為隨機遊戲，本工具只做資料分析，不保證中獎。</div>', unsafe_allow_html=True)