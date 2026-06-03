from collections import Counter
from itertools import combinations

def hot_cold(df, n):
    sample = df.head(n)
    nums = []

    for row in sample["號碼"]:
        nums.extend(row)

    counter = Counter(nums)

    hot = counter.most_common(20)

    cold = sorted(
        [(i, counter.get(i, 0)) for i in range(1, 81)],
        key=lambda x: x[1]
    )[:20]

    return hot, cold, counter

def zone_analysis(counter):
    zones = {}

    for start in range(1, 81, 10):
        end = start + 9
        key = f"{start:02d}-{end:02d}"
        zones[key] = sum(counter.get(i, 0) for i in range(start, end + 1))

    return zones

def odd_even_big_small(df, n):
    sample = df.head(n)
    nums = []

    for row in sample["號碼"]:
        nums.extend(row)

    odd = sum(1 for x in nums if x % 2 == 1)
    even = sum(1 for x in nums if x % 2 == 0)
    small = sum(1 for x in nums if x <= 40)
    big = sum(1 for x in nums if x >= 41)

    return odd, even, small, big

def ab_transfer(df, n):
    sample = df.head(n).reset_index(drop=True)
    score = Counter()

    for i in range(len(sample) - 1):
        current_nums = sample.loc[i + 1, "號碼"]
        next_nums = sample.loc[i, "號碼"]

        for b in next_nums:
            score[b] += 1

    return score

def resonance(df, n, size=2):
    sample = df.head(n).reset_index(drop=True)
    score = Counter()

    for i in range(len(sample) - 1):
        current_nums = sample.loc[i + 1, "號碼"]
        next_nums = sample.loc[i, "號碼"]

        for combo in combinations(current_nums, size):
            for b in next_nums:
                score[b] += 1

    return score

def pair_frequency(df, n):
    sample = df.head(n)
    pair_counter = Counter()

    for nums in sample["號碼"]:
        nums = sorted(nums)

        for pair in combinations(nums, 2):
            pair_counter[pair] += 1

    return pair_counter

def triple_frequency(df, n):
    sample = df.head(n)
    triple_counter = Counter()

    for nums in sample["號碼"]:
        nums = sorted(nums)

        for triple in combinations(nums, 3):
            triple_counter[triple] += 1

    return triple_counter

def latest_pair_match(df, n):
    """
    最新一期號碼中，哪些二同組合在近 n 期出現最多次
    """
    latest_nums = sorted(df.iloc[0]["號碼"])
    pair_counter = pair_frequency(df, n)

    rows = []

    for pair in combinations(latest_nums, 2):
        rows.append({
            "二同組合": f"{pair[0]:02d} + {pair[1]:02d}",
            "出現次數": pair_counter.get(pair, 0)
        })

    rows = sorted(rows, key=lambda x: x["出現次數"], reverse=True)
    return rows

def latest_triple_match(df, n):
    """
    最新一期號碼中，哪些三同組合在近 n 期出現最多次
    """
    latest_nums = sorted(df.iloc[0]["號碼"])
    triple_counter = triple_frequency(df, n)

    rows = []

    for triple in combinations(latest_nums, 3):
        rows.append({
            "三同組合": f"{triple[0]:02d} + {triple[1]:02d} + {triple[2]:02d}",
            "出現次數": triple_counter.get(triple, 0)
        })

    rows = sorted(rows, key=lambda x: x["出現次數"], reverse=True)
    return rows

def final_recommend(df, n):
    hot, cold, hot_score = hot_cold(df, n)
    ab_score = ab_transfer(df, n)
    pair_score = resonance(df, n, 2)
    triple_score = resonance(df, n, 3)

    total = Counter()

    for num in range(1, 81):
        total[num] += hot_score.get(num, 0) * 4
        total[num] += ab_score.get(num, 0) * 2
        total[num] += pair_score.get(num, 0) * 1.5
        total[num] += triple_score.get(num, 0) * 1

    ranked = [num for num, score in total.most_common()]

    return ranked[:4], ranked[:5], ranked[:8], total

def super_mother(df, target_super):
    df2 = df.sort_values("期別").reset_index(drop=True)

    hits = []

    for i, row in df2.iterrows():
        if row["超級獎號"] == target_super:
            hits.append(i)

    if len(hits) < 2:
        return None, []

    first = hits[0]

    if first + 1 >= len(df2):
        return None, []

    mother = df2.loc[first + 1, "號碼"]

    results = []

    for idx in hits[1:]:
        if idx + 1 < len(df2):
            next_nums = df2.loc[idx + 1, "號碼"]
            same = sorted(set(mother) & set(next_nums))

            results.append({
                "超級獎號期別": df2.loc[idx, "期別"],
                "下一期期別": df2.loc[idx + 1, "期別"],
                "重複顆數": len(same),
                "重複號碼": same
            })

    return mother, results