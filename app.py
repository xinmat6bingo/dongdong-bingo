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

init_db()

def fmt(nums):
    return " ".join(f"{x:02d}" for x in nums)

st.title("🎯 東東賓果分析系統")
st.caption("手機版 v3｜即時更新｜四星五星八星｜二同三同｜母盤分析")

col1, col2 = st.columns(2)

with col1:
    update = st.button("🔄 更新開獎", use_container_width=True)

with col2:
    period_count = st.selectbox(
        "分析期數",
        [12, 20, 30, 50, 100],
        index=1
    )

if update:
    try:
        count = update_latest()
        st.success(f"已更新 {count} 筆")
    except Exception as e:
        st.error(f"更新失敗：{e}")

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
    st.warning("目前沒有資料，請先按更新開獎。")
    st.stop()

hot, cold, counter = hot_cold(df, period_count)
zones = zone_analysis(counter)
odd, even, small, big = odd_even_big_small(df, period_count)
rec4, rec5, rec8, total_score = final_recommend(df, period_count)
latest = df.iloc[0]

st.divider()

st.header("📌 最新開獎")

st.subheader(f"期別：{latest['期別']}")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("時間", latest["時間"])

with c2:
    st.metric("超級獎號", f"{latest['超級獎號']:02d}")

with c3:
    st.metric("資料筆數", len(df))

st.success(fmt(latest["號碼"]))

st.divider()

st.header("🎯 推薦組合")

st.subheader("四星主攻")
st.success(fmt(rec4))

st.subheader("五星穩定")
st.info(fmt(rec5))

st.subheader("八星包牌")
st.warning(fmt(rec8))

st.divider()

st.header("⚖️ 盤型判斷")

p1, p2 = st.columns(2)
p3, p4 = st.columns(2)

with p1:
    st.metric("單數", odd)

with p2:
    st.metric("雙數", even)

with p3:
    st.metric("小號 01-40", small)

with p4:
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

st.divider()

st.header("📊 分析總覽")

tab1, tab2, tab3 = st.tabs(["🔥 熱冷號", "📊 區段", "🧠 權重"])

with tab1:
    st.subheader("🔥 熱門號碼")
    st.dataframe(
        pd.DataFrame(hot, columns=["號碼", "出現次數"]),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("❄️ 冷門號碼")
    st.dataframe(
        pd.DataFrame(cold, columns=["號碼", "出現次數"]),
        use_container_width=True,
        hide_index=True
    )

with tab2:
    zone_df = pd.DataFrame(list(zones.items()), columns=["區段", "次數"])
    st.bar_chart(zone_df.set_index("區段"))

with tab3:
    score_df = pd.DataFrame(
        [(num, round(score, 2)) for num, score in total_score.most_common(20)],
        columns=["號碼", "綜合分數"]
    )

    st.dataframe(
        score_df,
        use_container_width=True,
        hide_index=True
    )

st.divider()

st.header("🔬 進階分析")

a, b, c, d = st.tabs(["A→B", "二同", "三同", "母盤"])

with a:
    st.caption("A→B：統計近 N 期中，下一期常接續出現的號碼。")

    ab = ab_transfer(df, period_count)

    st.dataframe(
        pd.DataFrame(ab.most_common(30), columns=["號碼", "轉移次數"]),
        use_container_width=True,
        hide_index=True
    )

with b:
    st.caption("二同：統計兩個號碼同一期一起出現的次數。")

    pair_counter = pair_frequency(df, period_count)

    pair_rows = []
    for pair, cnt in pair_counter.most_common(100):
        pair_rows.append({
            "二同組合": f"{pair[0]:02d} + {pair[1]:02d}",
            "出現次數": cnt
        })

    st.subheader("二同組合排行")
    st.dataframe(
        pd.DataFrame(pair_rows),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("最新期二同")
    latest_pair_rows = latest_pair_match(df, period_count)

    st.dataframe(
        pd.DataFrame(latest_pair_rows).head(80),
        use_container_width=True,
        hide_index=True
    )

with c:
    st.caption("三同：統計三個號碼同一期一起出現的次數。")

    triple_counter = triple_frequency(df, period_count)

    triple_rows = []
    for triple, cnt in triple_counter.most_common(100):
        triple_rows.append({
            "三同組合": f"{triple[0]:02d} + {triple[1]:02d} + {triple[2]:02d}",
            "出現次數": cnt
        })

    st.subheader("三同組合排行")
    st.dataframe(
        pd.DataFrame(triple_rows),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("最新期三同")
    latest_triple_rows = latest_triple_match(df, period_count)

    st.dataframe(
        pd.DataFrame(latest_triple_rows).head(80),
        use_container_width=True,
        hide_index=True
    )

with d:
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
            st.success("母盤：" + fmt(mother))

            rows = []
            rank = Counter()

            for r in results:
                for x in r["重複號碼"]:
                    rank[x] += 1

                rows.append({
                    "超級獎號期別": r["超級獎號期別"],
                    "下一期期別": r["下一期期別"],
                    "重複顆數": r["重複顆數"],
                    "重複號碼": fmt(r["重複號碼"])
                })

            st.subheader("母盤比對結果")
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True
            )

            st.subheader("母盤重複排行")
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

st.caption("提醒：賓果為隨機遊戲，本工具只做資料分析，不保證中獎。")