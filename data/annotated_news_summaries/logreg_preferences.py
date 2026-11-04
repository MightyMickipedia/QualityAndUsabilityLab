#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logistic regression for pairwise preference decisions.

Input:
  annotations_clean.jsonl

Model:
  preference ~ chosen-minus-rejected rating deltas for d1..d8
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit
from scipy.stats import norm


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
    return parser.parse_args()


def get_dim_cols(df: pd.DataFrame) -> List[str]:
    dim_cols = sorted(
        [col for col in df.columns if col.startswith("d") and col[1:].isdigit()],
        key=lambda col: int(col[1:]),
    )
    if not dim_cols:
        raise RuntimeError("No dimension columns d1..d8 found.")
    return dim_cols


def build_preference_pairs(df: pd.DataFrame, dim_cols: List[str]) -> pd.DataFrame:
    dfx = df[df["preferred"].isin([0, 1, True, False])].copy()
    dfx["preferred"] = dfx["preferred"].astype(int)

    rows = []
    for (row_idx, annotator), group in dfx.groupby(["row_idx", "annotator"], sort=False):
        group = group.dropna(subset=dim_cols, how="any")
        if len(group) != 2:
            continue
        chosen = group[group["preferred"] == 1]
        rejected = group[group["preferred"] == 0]
        if len(chosen) != 1 or len(rejected) != 1:
            continue

        chosen = chosen.iloc[0]
        rejected = rejected.iloc[0]
        row = {
            "row_idx": int(row_idx),
            "annotator": str(annotator),
            "item_id": str(chosen["item_id"]),
            "sr_no": str(chosen["sr_no"]),
            "chosen_model": str(chosen["model"]),
            "rejected_model": str(rejected["model"]),
        }
        for dim in dim_cols:
            row[f"delta_{dim}"] = float(chosen[dim]) - float(rejected[dim])
        rows.append(row)
    return pd.DataFrame(rows)


def build_preference_consensus(df: pd.DataFrame) -> pd.DataFrame:
    dfx = df[df["preferred"].isin([0, 1, True, False])].copy()
    dfx["preferred"] = dfx["preferred"].astype(int)

    rows = []
    for (row_idx, annotator), group in dfx.groupby(["row_idx", "annotator"], sort=False):
        if len(group) != 2:
            continue
        chosen = group[group["preferred"] == 1]
        rejected = group[group["preferred"] == 0]
        if len(chosen) != 1 or len(rejected) != 1:
            continue
        rows.append(
            {
                "row_idx": int(row_idx),
                "annotator": str(annotator),
                "item_id": str(group["item_id"].iloc[0]),
                "sr_no": str(group["sr_no"].iloc[0]),
                "chosen_model": str(chosen["model"].iloc[0]),
            }
        )

    choices = pd.DataFrame(rows)
    if choices.empty:
        return choices

    consensus_rows = []
    for row_idx, group in choices.groupby("row_idx", sort=False):
        counts = group["chosen_model"].value_counts()
        consensus_rows.append(
            {
                "row_idx": int(row_idx),
                "item_id": str(group["item_id"].iloc[0]),
                "sr_no": str(group["sr_no"].iloc[0]),
                "n_annotators": int(group["annotator"].nunique()),
                "winner_counts": ", ".join(f"{model}:{count}" for model, count in counts.items()),
                "all_agree": bool(counts.iloc[0] == len(group)),
                "at_least_2_agree": bool(counts.iloc[0] >= 2),
            }
        )
    return pd.DataFrame(consensus_rows)


def fit_logit_with_symmetric_trick(pairs: pd.DataFrame, dim_cols: List[str]):
    x_cols = [f"delta_{dim}" for dim in dim_cols]
    x = pairs[x_cols].to_numpy(dtype=float)
    x2 = np.vstack([x, -x])
    y2 = np.concatenate([np.ones(len(pairs)), np.zeros(len(pairs))])
    x2 = np.column_stack([np.ones(len(x2)), x2])

    def nll(beta: np.ndarray) -> float:
        z = x2 @ beta
        return float(np.sum(np.logaddexp(0.0, z) - y2 * z))

    def grad(beta: np.ndarray) -> np.ndarray:
        z = x2 @ beta
        return x2.T @ (expit(z) - y2)

    def hess(beta: np.ndarray) -> np.ndarray:
        z = x2 @ beta
        p = expit(z)
        w = p * (1.0 - p)
        return x2.T @ (x2 * w[:, None])

    result = minimize(nll, np.zeros(x2.shape[1]), method="BFGS", jac=grad)
    if not result.success:
        raise RuntimeError(f"Logistic regression failed: {result.message}")

    beta = result.x
    cov = np.linalg.pinv(hess(beta))
    se = np.sqrt(np.diag(cov))
    zvals = np.divide(beta, se, out=np.full_like(beta, np.nan), where=se > 0)
    pvals = 2.0 * (1.0 - norm.cdf(np.abs(zvals)))
    names = ["const", *x_cols]
    return pd.Series(beta, index=names), pd.Series(pvals, index=names)


def format_p_value(pval: float) -> str:
    if pd.isna(pval):
        return "NA"
    if pval < 0.0001:
        return "< 0.0001"
    return f"{pval:.4f}"


def main() -> None:
    args = parse_args()
    base = Path(__file__).resolve().parent
    df = pd.read_json(base / args.input, lines=True)

    dim_cols = get_dim_cols(df)
    df[dim_cols] = df[dim_cols].apply(pd.to_numeric, errors="coerce")

    pairs = build_preference_pairs(df, dim_cols)
    consensus = build_preference_consensus(df)
    if pairs.empty:
        raise RuntimeError("No valid preference pairs found.")

    params, pvalues = fit_logit_with_symmetric_trick(pairs, dim_cols)

    rows = []
    for dim in dim_cols:
        feat = f"delta_{dim}"
        rows.append(
            {
                "Dimension": AXIS_NAMES.get(dim, dim),
                "Odds Ratio": round(float(np.exp(params[feat])), 2),
                "p_value": format_p_value(float(pvalues[feat])),
            }
        )
    out = pd.DataFrame(rows).sort_values("Odds Ratio", ascending=False)
    out.to_csv(base / "logreg_preference_odds.csv", index=False)

    print("Preference Drivers (Logistic Regression)")
    print("========================================")
    print(f"Preference selections analysed: {len(pairs)}")
    if not consensus.empty:
        print(f"Pairwise tasks with unanimous winner: {int(consensus['all_agree'].sum())}")
        print(f"Pairwise tasks with at least 2 annotators agreeing: {int(consensus['at_least_2_agree'].sum())}")
    print()
    print(out.to_string(index=False))
    print("\nSaved: logreg_preference_odds.csv")


if __name__ == "__main__":
    main()
