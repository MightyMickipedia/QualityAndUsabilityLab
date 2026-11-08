#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Compute inter-annotator agreement for Konvens publication data.

Input:
  annotations_clean.jsonl

Outputs:
  iaa_all_units_by_dimension.csv
  iaa_exactly_2_annotators_by_dimension.csv
  iaa_exactly_3_annotators_by_dimension.csv
  iaa_preference_alpha.csv
  stats_overall_by_dimension.csv
"""

from __future__ import annotations

import argparse
import itertools
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


AXIS_NAMES = {
    "d1": "Grammaticality",
    "d2": "Non-redundancy",
    "d3": "Referential Clarity",
    "d4": "Focus",
    "d5": "Structure & Coherence",
    "d6": "Content Coverage",
    "d7": "Faithfulness",
    "d8": "Complexity",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="annotations_clean.jsonl")
    parser.add_argument("--alpha-level", choices=["ordinal", "interval"], default="ordinal")
    return parser.parse_args()


def load_jsonl(path: Path) -> pd.DataFrame:
    return pd.read_json(path, lines=True)


def get_dim_cols(df: pd.DataFrame) -> list[str]:
    return sorted(
        [col for col in df.columns if col.startswith("d") and col[1:].isdigit()],
        key=lambda col: int(col[1:]),
    )


def units_from_matrix(matrix: np.ndarray) -> list[np.ndarray]:
    units = []
    for row in matrix:
        values = row[~np.isnan(row)].astype(float)
        if values.size >= 2:
            units.append(values)
    return units


def krippendorff_alpha_interval_squared(matrix: np.ndarray) -> float:
    units = units_from_matrix(matrix)
    if not units:
        return np.nan

    observed_num = 0.0
    observed_den = 0
    for values in units:
        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                observed_num += (values[i] - values[j]) ** 2
                observed_den += 1
    observed = observed_num / observed_den if observed_den else np.nan

    all_vals = []
    all_wts = []
    for values in units:
        weight = len(values) - 1
        all_vals.append(values)
        all_wts.append(np.full_like(values, weight, dtype=float))
    all_vals = np.concatenate(all_vals)
    all_wts = np.concatenate(all_wts)

    cats = np.unique(all_vals)
    n_c = np.array([all_wts[all_vals == cat].sum() for cat in cats], dtype=float)
    n = n_c.sum()
    if n <= 1:
        return np.nan

    expected_num = 0.0
    for i, cat_i in enumerate(cats):
        for j, cat_j in enumerate(cats):
            if i != j:
                expected_num += n_c[i] * n_c[j] * (cat_i - cat_j) ** 2
    expected = expected_num / (n * (n - 1))
    return 1.0 - observed / expected if expected > 0 else np.nan


def krippendorff_alpha_ordinal(matrix: np.ndarray) -> float:
    units = units_from_matrix(matrix)
    if not units:
        return np.nan

    all_vals = []
    all_wts = []
    for values in units:
        weight = len(values) - 1
        all_vals.append(values)
        all_wts.append(np.full_like(values, weight, dtype=float))
    all_vals = np.concatenate(all_vals)
    all_wts = np.concatenate(all_wts)

    cats = np.unique(all_vals)
    cats.sort()
    n_c = np.array([all_wts[all_vals == cat].sum() for cat in cats], dtype=float)
    n = n_c.sum()
    if n <= 1:
        return np.nan

    p = n_c / n
    cum_p = np.cumsum(p)

    def mass_between(i: int, j: int) -> float:
        if i == j:
            return 0.0
        lo, hi = (i, j) if i < j else (j, i)
        if hi - lo <= 1:
            return 0.0
        return float(cum_p[hi - 1] - cum_p[lo])

    distance = np.zeros((len(cats), len(cats)), dtype=float)
    for i in range(len(cats)):
        for j in range(len(cats)):
            if i != j:
                between = mass_between(i, j)
                distance[i, j] = between * between

    cat_to_idx = {cat: idx for idx, cat in enumerate(cats)}
    observed_num = 0.0
    observed_den = 0
    for values in units:
        idxs = [cat_to_idx[value] for value in values]
        for i in range(len(idxs)):
            for j in range(i + 1, len(idxs)):
                observed_num += distance[idxs[i], idxs[j]]
                observed_den += 1
    observed = observed_num / observed_den if observed_den else np.nan

    expected_num = 0.0
    for i in range(len(cats)):
        for j in range(len(cats)):
            if i != j:
                expected_num += n_c[i] * n_c[j] * distance[i, j]
    expected = expected_num / (n * (n - 1))
    return 1.0 - observed / expected if expected > 0 else np.nan


def krippendorff_alpha(matrix: np.ndarray, level: str) -> float:
    if level == "ordinal":
        return krippendorff_alpha_ordinal(matrix)
    if level == "interval":
        return krippendorff_alpha_interval_squared(matrix)
    raise ValueError(level)


def krippendorff_alpha_nominal(matrix: np.ndarray) -> float:
    units = []
    for row in matrix:
        vals = [x for x in row if pd.notna(x)]
        if len(vals) >= 2:
            units.append(np.array(vals, dtype=object))
    if not units:
        return np.nan

    observed_num = 0.0
    observed_den = 0
    for values in units:
        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                observed_num += 0.0 if values[i] == values[j] else 1.0
                observed_den += 1
    observed = observed_num / observed_den if observed_den else np.nan

    all_vals = []
    all_wts = []
    for values in units:
        weight = len(values) - 1
        all_vals.extend(values.tolist())
        all_wts.extend([weight] * len(values))
    all_vals = np.array(all_vals, dtype=object)
    all_wts = np.array(all_wts, dtype=float)
    cats = pd.unique(all_vals)
    n_c = np.array([all_wts[all_vals == cat].sum() for cat in cats], dtype=float)
    n = n_c.sum()
    if n <= 1:
        return np.nan
    p = n_c / n
    expected = 1.0 - np.sum(p ** 2)
    return 1.0 - observed / expected if expected > 0 else np.nan


def subset_by_exact_annotators_per_unit(df: pd.DataFrame, n_annotators: int) -> pd.DataFrame:
    unit_n = df.groupby("unit")["annotator"].nunique()
    keep = unit_n[unit_n == n_annotators].index
    return df[df["unit"].isin(keep)].copy()


def alpha_table(df: pd.DataFrame, dim_cols: Iterable[str], level: str) -> pd.DataFrame:
    rows = []
    for dim in dim_cols:
        pivot = df.pivot_table(index="unit", columns="annotator", values=dim, aggfunc="mean")
        pivot = pivot[pivot.notna().sum(axis=1) >= 2]
        alpha = krippendorff_alpha(pivot.values, level=level)
        rows.append(
            {
                "Dimension": AXIS_NAMES.get(dim, dim),
                "dim_col": dim,
                "Alpha_all": round(float(alpha), 3) if pd.notna(alpha) else np.nan,
                "N_units": int(len(pivot)),
            }
        )
    return pd.DataFrame(rows).sort_values("Alpha_all", na_position="last")


def descriptive_stats_overall(df: pd.DataFrame, dim_cols: list[str]) -> pd.DataFrame:
    rows = []
    for dim in dim_cols:
        vals = df[dim].dropna()
        rows.append(
            {
                "Dimension": AXIS_NAMES.get(dim, dim),
                "dim_col": dim,
                "N_ratings": int(len(vals)),
                "mean": round(float(vals.mean()), 3),
                "std": round(float(vals.std(ddof=1)), 3),
                "var": round(float(vals.var(ddof=1)), 3),
            }
        )
    return pd.DataFrame(rows)


def preference_alpha_table(df: pd.DataFrame) -> pd.DataFrame:
    dfx = df[df["preferred"].isin([0, 1, True, False])].copy()
    dfx["preferred"] = dfx["preferred"].astype(int)
    valid = (
        dfx.groupby(["sr_no", "annotator"])["preferred"]
        .agg(["count", "sum"])
        .reset_index()
    )
    valid = valid[(valid["count"] == 2) & (valid["sum"] == 1)][["sr_no", "annotator"]]
    dfx = dfx.merge(valid, on=["sr_no", "annotator"], how="inner")
    chosen = dfx[dfx["preferred"] == 1][["sr_no", "annotator", "model"]]
    pivot = chosen.pivot_table(index="sr_no", columns="annotator", values="model", aggfunc="first")

    rows = []
    for label, n_annotators in [("all (>=2)", None), ("exactly 2", 2), ("exactly 3", 3)]:
        sub = pivot.copy()
        if n_annotators is None:
            sub = sub[sub.notna().sum(axis=1) >= 2]
        else:
            sub = sub[sub.notna().sum(axis=1) == n_annotators]
        alpha = krippendorff_alpha_nominal(sub.values) if len(sub) else np.nan
        rows.append(
            {
                "subset": label,
                "alpha_nominal": round(float(alpha), 3) if pd.notna(alpha) else np.nan,
                "N_units": int(len(sub)),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    base = Path(__file__).resolve().parent
    df = load_jsonl(base / args.input)

    dim_cols = get_dim_cols(df)
    df[dim_cols] = df[dim_cols].apply(pd.to_numeric, errors="coerce")
    df["unit"] = df["item_id"].astype(str) + "||" + df["model"].astype(str)

    outputs = {
        "iaa_all_units_by_dimension.csv": alpha_table(df, dim_cols, args.alpha_level),
        "iaa_exactly_2_annotators_by_dimension.csv": alpha_table(
            subset_by_exact_annotators_per_unit(df, 2), dim_cols, args.alpha_level
        ),
        "iaa_exactly_3_annotators_by_dimension.csv": alpha_table(
            subset_by_exact_annotators_per_unit(df, 3), dim_cols, args.alpha_level
        ),
        "iaa_preference_alpha.csv": preference_alpha_table(df),
        "stats_overall_by_dimension.csv": descriptive_stats_overall(df, dim_cols),
    }

    for filename, out_df in outputs.items():
        out_df.to_csv(base / filename, index=False)
        print(f"\n{filename}")
        print(out_df.to_string(index=False))


if __name__ == "__main__":
    main()
