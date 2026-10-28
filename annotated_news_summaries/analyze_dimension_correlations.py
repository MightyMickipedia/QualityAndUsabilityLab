#!/usr/bin/env python3
"""Analyze correlations, PCA structure, and summary-length effects.

The primary unit is an item-model summary. Ratings from multiple annotators are
averaged before PCA and regression so duplicated annotations do not receive
extra weight. Annotation-level correlations are also reported for comparison.
"""

from itertools import combinations
from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import f as f_distribution
from scipy.stats import spearmanr


HERE = Path(__file__).resolve().parent
INPUT = HERE / "data_files" / "annotations_clean.jsonl"
OUTPUT = HERE / "dimension_correlation_results"

DIMENSIONS = {
    "d1": "Grammaticality",
    "d2": "Non-redundancy",
    "d3": "Referential Clarity",
    "d4": "Focus",
    "d5": "Structure & Coherence",
    "d6": "Content Coverage",
    "d7": "Faithfulness",
    "d8": "Complexity",
}


def load_data() -> pd.DataFrame:
    records = []
    with INPUT.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as error:
                    raise ValueError(f"Invalid JSON on line {line_number}: {error}") from error
    data = pd.DataFrame(records)
    data[list(DIMENSIONS)] = data[list(DIMENSIONS)].apply(pd.to_numeric, errors="raise")
    return data


def pairwise_results(data: pd.DataFrame, analysis: str) -> pd.DataFrame:
    rows = []
    for left, right in combinations(DIMENSIONS, 2):
        paired = data[[left, right]].dropna()
        rho, p_value = spearmanr(paired[left], paired[right])
        rows.append(
            {
                "analysis": analysis,
                "dimension_1": DIMENSIONS[left],
                "dimension_2": DIMENSIONS[right],
                "rho": rho,
                "p_value": p_value,
                "n": len(paired),
            }
        )
    result = pd.DataFrame(rows)
    # Benjamini-Hochberg false-discovery-rate correction across the 28 pairs.
    order = np.argsort(result["p_value"].to_numpy())
    ranked = result["p_value"].to_numpy()[order] * len(result) / np.arange(1, len(result) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adjusted = np.empty(len(result))
    adjusted[order] = np.minimum(ranked, 1.0)
    result["p_fdr_bh"] = adjusted
    return result.sort_values("rho", ascending=False)


def save_heatmap(correlation: pd.DataFrame, title: str, destination: Path) -> None:
    labels = [DIMENSIONS[column] for column in correlation.columns]
    figure, axis = plt.subplots(figsize=(10, 8))
    image = axis.imshow(correlation, vmin=-1, vmax=1, cmap="RdBu_r")
    axis.set_xticks(range(len(labels)), labels=labels, rotation=45, ha="right")
    axis.set_yticks(range(len(labels)), labels=labels)
    for row in range(len(labels)):
        for column in range(len(labels)):
            value = correlation.iloc[row, column]
            axis.text(column, row, f"{value:.2f}", ha="center", va="center",
                      color="white" if abs(value) > 0.55 else "black")
    axis.set_title(title)
    figure.colorbar(image, ax=axis, label="Spearman’s rho", shrink=0.8)
    figure.tight_layout()
    figure.savefig(destination, dpi=200)
    plt.close(figure)


def run_pca(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run PCA using the Spearman correlation matrix of the ordinal ratings."""
    correlation = data.corr(method="spearman").to_numpy()
    eigenvalues, eigenvectors = np.linalg.eigh(correlation)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    # Fix arbitrary eigenvector signs: the largest absolute loading is positive.
    for component in range(eigenvectors.shape[1]):
        pivot = np.argmax(np.abs(eigenvectors[:, component]))
        if eigenvectors[pivot, component] < 0:
            eigenvectors[:, component] *= -1
    loadings = eigenvectors * np.sqrt(np.maximum(eigenvalues, 0))
    components = [f"PC{i}" for i in range(1, len(eigenvalues) + 1)]
    variance = pd.DataFrame(
        {
            "component": components,
            "eigenvalue": eigenvalues,
            "explained_variance_ratio": eigenvalues / eigenvalues.sum(),
            "cumulative_variance_ratio": np.cumsum(eigenvalues / eigenvalues.sum()),
        }
    )
    loading_table = pd.DataFrame(
        loadings,
        index=[DIMENSIONS[column] for column in data.columns],
        columns=components,
    )
    return variance, loading_table


def save_scree_plot(variance: pd.DataFrame, destination: Path) -> None:
    figure, axis = plt.subplots(figsize=(8, 5))
    x = np.arange(1, len(variance) + 1)
    axis.plot(x, variance["eigenvalue"], marker="o")
    axis.axhline(1, color="grey", linestyle="--", label="Kaiser threshold (1.0)")
    axis.set(xticks=x, xlabel="Principal component", ylabel="Eigenvalue",
             title="PCA scree plot (Spearman correlation matrix)")
    axis.legend()
    figure.tight_layout()
    figure.savefig(destination, dpi=200)
    plt.close(figure)


def residualize_by_item(values: np.ndarray, item_codes: np.ndarray) -> np.ndarray:
    """Remove item fixed effects by subtracting each item's column means."""
    frame = pd.DataFrame(values)
    frame["_item"] = item_codes
    means = frame.groupby("_item").transform("mean")
    return frame.drop(columns="_item").to_numpy() - means.to_numpy()


def fit_ols(y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, float, int, int]:
    """Return coefficients, RSS, residual df, and design rank."""
    beta, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    residual = y - x @ beta
    return beta, float(residual @ residual), len(y) - rank, rank


def nested_f_test(
    y: np.ndarray, reduced: np.ndarray, full: np.ndarray
) -> tuple[float, float, int, int, float]:
    """Classical partial F test comparing nested OLS designs."""
    _, rss_reduced, _, rank_reduced = fit_ols(y, reduced)
    _, rss_full, df_denominator, rank_full = fit_ols(y, full)
    df_numerator = rank_full - rank_reduced
    if df_numerator <= 0 or rss_full <= 0:
        return np.nan, np.nan, df_numerator, df_denominator, np.nan
    statistic = ((rss_reduced - rss_full) / df_numerator) / (rss_full / df_denominator)
    p_value = f_distribution.sf(max(statistic, 0), df_numerator, df_denominator)
    partial_r2 = max(rss_reduced - rss_full, 0) / rss_reduced
    return statistic, p_value, df_numerator, df_denominator, partial_r2


def analyze_length_and_systems(averaged: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Relate length to ratings and test system effects with item fixed effects."""
    data = averaged.copy()
    data["summary_words"] = data["summary"].fillna("").str.findall(r"\b\w+\b").str.len()
    item_codes, _ = pd.factorize(data["item_id"], sort=True)
    systems = sorted(data["model"].astype(str).unique())
    reference = systems[0]
    system_matrix = np.column_stack(
        [(data["model"].astype(str) == system).astype(float) for system in systems[1:]]
    )
    length = data["summary_words"].to_numpy(dtype=float)[:, None]

    # Within-item transformation is equivalent to including one fixed effect
    # per source item, without constructing a very large dummy matrix.
    system_within = residualize_by_item(system_matrix, item_codes)
    length_within = residualize_by_item(length, item_codes)
    length_rows = []
    system_rows = []

    for dimension in DIMENSIONS:
        y = data[dimension].to_numpy(dtype=float)
        y_within = residualize_by_item(y[:, None], item_codes).ravel()
        rho, rho_p = spearmanr(data["summary_words"], y)

        # Does length relate to ratings after holding item and system constant?
        beta_full, _, df_full, _ = fit_ols(
            y_within, np.column_stack([system_within, length_within])
        )
        _, rss_no_length, _, _ = fit_ols(y_within, system_within)
        _, rss_with_length, _, _ = fit_ols(
            y_within, np.column_stack([system_within, length_within])
        )
        length_f = ((rss_no_length - rss_with_length) / 1) / (rss_with_length / df_full)
        length_p = f_distribution.sf(max(length_f, 0), 1, df_full)
        length_rows.append(
            {
                "dimension": DIMENSIONS[dimension],
                "spearman_rho_words": rho,
                "spearman_p_value": rho_p,
                "adjusted_rating_change_per_10_words": beta_full[-1] * 10,
                "length_partial_f": length_f,
                "length_p_value_item_and_system_adjusted": length_p,
                "n_item_model_units": len(data),
            }
        )

        # Test system differences before and after adding length. Both models
        # include item fixed effects through within-item residualization.
        zero = np.zeros((len(data), 0))
        f_raw, p_raw, df_num_raw, df_den_raw, r2_raw = nested_f_test(
            y_within, zero, system_within
        )
        f_adjusted, p_adjusted, df_num_adjusted, df_den_adjusted, r2_adjusted = nested_f_test(
            y_within, length_within, np.column_stack([length_within, system_within])
        )
        system_rows.append(
            {
                "dimension": DIMENSIONS[dimension],
                "reference_system_for_coefficients": reference,
                "system_f_before_length_control": f_raw,
                "system_p_before_length_control": p_raw,
                "system_partial_r2_before_length_control": r2_raw,
                "system_df_num_before": df_num_raw,
                "system_df_den_before": df_den_raw,
                "system_f_after_length_control": f_adjusted,
                "system_p_after_length_control": p_adjusted,
                "system_partial_r2_after_length_control": r2_adjusted,
                "system_df_num_after": df_num_adjusted,
                "system_df_den_after": df_den_adjusted,
                "system_effect_remains_at_0.05": p_adjusted < 0.05,
            }
        )

    return pd.DataFrame(length_rows), pd.DataFrame(system_rows)


def main() -> None:
    OUTPUT.mkdir(exist_ok=True)
    data = load_data()
    dimensions = list(DIMENSIONS)

    raw = data[dimensions]
    # Each underlying summary is identified by item_id + model and may have
    # ratings from multiple annotators.
    averaged = (
        data.groupby(["item_id", "model"], as_index=False)
        .agg(
            **{dimension: (dimension, "mean") for dimension in dimensions},
            summary=("summary", "first"),
        )
    )

    raw_correlation = raw.corr(method="spearman").rename(index=DIMENSIONS, columns=DIMENSIONS)
    averaged_correlation = (
        averaged[dimensions].corr(method="spearman").rename(index=DIMENSIONS, columns=DIMENSIONS)
    )
    raw_correlation.to_csv(OUTPUT / "spearman_annotation_level.csv", float_format="%.6f")
    averaged_correlation.to_csv(
        OUTPUT / "spearman_item_model_averaged.csv", float_format="%.6f"
    )

    tests = pd.concat(
        [
            pairwise_results(raw, "annotation_level"),
            pairwise_results(averaged[dimensions], "item_model_averaged"),
        ],
        ignore_index=True,
    )
    tests.to_csv(OUTPUT / "spearman_pairwise_tests.csv", index=False, float_format="%.8g")

    save_heatmap(
        raw.corr(method="spearman"),
        f"Dimension correlations: individual annotations (n={len(raw):,})",
        OUTPUT / "spearman_annotation_level.png",
    )
    save_heatmap(
        averaged[dimensions].corr(method="spearman"),
        f"Dimension correlations: item–model means (n={len(averaged):,})",
        OUTPUT / "spearman_item_model_averaged.png",
    )

    pca_variance, pca_loadings = run_pca(averaged[dimensions])
    pca_variance.to_csv(OUTPUT / "pca_explained_variance.csv", index=False, float_format="%.6f")
    pca_loadings.to_csv(OUTPUT / "pca_loadings.csv", float_format="%.6f")
    save_scree_plot(pca_variance, OUTPUT / "pca_scree_plot.png")

    length_results, system_results = analyze_length_and_systems(averaged)
    length_results.to_csv(OUTPUT / "length_dimension_relationships.csv", index=False,
                          float_format="%.8g")
    system_results.to_csv(OUTPUT / "system_effects_controlling_length.csv", index=False,
                          float_format="%.8g")

    print(f"Valid annotation records: {len(data):,}")
    print(f"Unique item–model units: {len(averaged):,}")
    print(f"Missing dimension ratings: {int(data[dimensions].isna().sum().sum()):,}")
    print("\nItem–model-averaged correlations (strongest first):")
    print(
        tests[tests["analysis"] == "item_model_averaged"]
        .loc[:, ["dimension_1", "dimension_2", "rho", "p_fdr_bh"]]
        .to_string(index=False)
    )
    print("\nPCA explained variance:")
    print(pca_variance.head(4).to_string(index=False))
    print("\nLength relationships:")
    print(
        length_results[
            ["dimension", "spearman_rho_words", "adjusted_rating_change_per_10_words",
             "length_p_value_item_and_system_adjusted"]
        ].to_string(index=False)
    )
    print("\nDo system effects remain after controlling for item and length?")
    print(
        system_results[
            ["dimension", "system_p_after_length_control",
             "system_partial_r2_after_length_control", "system_effect_remains_at_0.05"]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
