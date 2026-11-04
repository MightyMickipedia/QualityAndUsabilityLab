#!/usr/bin/env python3
"""Create rating-distribution tables and figures for the eight dimensions.

The analysis uses individual annotation responses, retaining the interpretable
1--7 scale. It reports exact rating frequencies overall and, separately for
each system, the proportions of severe (1--2), intermediate (3--4), and strong
(5--7) ratings.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE / "data_files" / "annotations_clean.jsonl"
DEFAULT_OUTPUT = HERE / "rating_distribution_results"

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

RATING_COLORS = {
    1: "#67001f",
    2: "#b2182b",
    3: "#d6604d",
    4: "#f4a582",
    5: "#92c5de",
    6: "#4393c3",
    7: "#2166ac",
}

SYSTEM_DISPLAY_NAMES = {
    "gpt3.5": "GPT-3.5",
    "llama-1b": "LLaMA-1B",
    "llama-3b": "LLaMA-3B",
    "mistral-nemo": "German-Leo",
    "sauerkraut": "Sauerkraut",
    "wiedervereinigung": "Wiedervereinigung",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--min-annotators",
        type=int,
        default=2,
        help=(
            "Retain item-model units with at least this many distinct annotators "
            "(default: 2, corresponding to 1,470 units)."
        ),
    )
    return parser.parse_args()


def load_annotations(path: Path) -> pd.DataFrame:
    records = []
    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON on line {line_number}: {error}") from error
    data = pd.DataFrame(records)
    columns = list(DIMENSIONS)
    data[columns] = data[columns].apply(pd.to_numeric, errors="raise")
    invalid = ~data[columns].isin(range(1, 8))
    if invalid.any().any():
        locations = np.argwhere(invalid.to_numpy())
        raise ValueError(f"Found {len(locations)} dimension ratings outside the 1--7 scale")
    return data


def long_ratings(data: pd.DataFrame) -> pd.DataFrame:
    long = data.melt(
        id_vars=["annotation_id", "annotator", "item_id", "model"],
        value_vars=list(DIMENSIONS),
        var_name="dimension_column",
        value_name="rating",
    )
    long["dimension"] = long["dimension_column"].map(DIMENSIONS)
    long["rating"] = long["rating"].astype(int)
    return long


def exact_distribution(long: pd.DataFrame) -> pd.DataFrame:
    counts = (
        long.groupby(["dimension_column", "dimension", "rating"])
        .size()
        .rename("count")
        .reset_index()
    )
    totals = counts.groupby("dimension_column")["count"].transform("sum")
    counts["percent"] = 100 * counts["count"] / totals
    return counts.sort_values(["dimension_column", "rating"])


def band_distribution(long: pd.DataFrame) -> pd.DataFrame:
    long = long.copy()
    long["rating_band"] = pd.cut(
        long["rating"],
        bins=[0, 2, 4, 7],
        labels=["Severe (1--2)", "Intermediate (3--4)", "Strong (5--7)"],
    )
    counts = (
        long.groupby(
            ["model", "dimension_column", "dimension", "rating_band"],
            observed=True,
        )
        .size()
        .rename("count")
        .reset_index()
    )
    totals = counts.groupby(["model", "dimension_column"])["count"].transform("sum")
    counts["percent"] = 100 * counts["count"] / totals
    return counts.sort_values(["model", "dimension_column", "rating_band"])


def save_overall_plot(distribution: pd.DataFrame, destination: Path) -> None:
    percentages = distribution.pivot(
        index="dimension", columns="rating", values="percent"
    ).reindex(DIMENSIONS.values())
    figure, axis = plt.subplots(figsize=(11, 6))
    left = np.zeros(len(percentages))
    for rating in range(1, 8):
        values = percentages[rating].to_numpy()
        axis.barh(
            percentages.index,
            values,
            left=left,
            color=RATING_COLORS[rating],
            label=str(rating),
        )
        left += values
    axis.set(
        xlabel="Percentage of individual ratings",
        ylabel="",
        xlim=(0, 100),
        title="Rating distributions across evaluation dimensions",
    )
    axis.invert_yaxis()
    axis.legend(title="Rating", ncol=7, loc="lower center", bbox_to_anchor=(0.5, 1.01))
    figure.tight_layout()
    figure.savefig(destination, dpi=200, bbox_inches="tight")
    plt.close(figure)


def save_system_plot(long: pd.DataFrame, destination: Path) -> None:
    systems = [
        system
        for system in SYSTEM_DISPLAY_NAMES
        if system in set(long["model"].astype(str))
    ]
    dimensions = list(DIMENSIONS.values())
    y_positions = np.arange(len(dimensions))
    figure, axes = plt.subplots(2, 3, figsize=(18, 12), sharex=True, sharey=True)
    for axis, system in zip(axes.flat, systems):
        subset = long[long["model"].astype(str) == system]
        distribution = exact_distribution(subset)
        percentages = distribution.pivot(
            index="dimension", columns="rating", values="percent"
        ).reindex(index=dimensions, columns=range(1, 8), fill_value=0).fillna(0)
        left = np.zeros(len(percentages))
        for rating in range(1, 8):
            values = percentages[rating].to_numpy()
            axis.barh(y_positions, values, left=left, color=RATING_COLORS[rating])
            left += values
        axis.set_title(SYSTEM_DISPLAY_NAMES[system], fontsize=16, pad=8)
        axis.set_xlim(0, 100)
        axis.set_yticks(y_positions, labels=dimensions, fontsize=12)
        axis.tick_params(axis="x", labelsize=12)
    # The panels share one y-axis; invert it only once so the displayed order
    # matches Table 9 (Grammaticality first, Complexity last).
    axes.flat[0].invert_yaxis()
    figure.supxlabel("Percentage of individual ratings", fontsize=14)
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=RATING_COLORS[rating])
        for rating in range(1, 8)
    ]
    figure.legend(handles, [str(rating) for rating in range(1, 8)],
                  title="Rating", ncol=7, loc="upper center",
                  bbox_to_anchor=(0.5, 0.985), fontsize=12, title_fontsize=13)
    figure.tight_layout(rect=(0, 0.03, 1, 0.925))
    figure.savefig(destination, dpi=200, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    args = parse_args()
    data = load_annotations(args.input)
    unit_columns = ["item_id", "model"]
    annotators_per_unit = data.groupby(unit_columns)["annotator"].nunique()
    retained_units = annotators_per_unit[
        annotators_per_unit >= args.min_annotators
    ].index
    data = (
        data.set_index(unit_columns)
        .loc[retained_units]
        .reset_index()
    )
    n_units = data[unit_columns].drop_duplicates().shape[0]
    long = long_ratings(data)
    overall = exact_distribution(long)
    by_system_exact = (
        long.groupby(["model", "dimension_column", "dimension", "rating"])
        .size()
        .rename("count")
        .reset_index()
    )
    totals = by_system_exact.groupby(["model", "dimension_column"])["count"].transform("sum")
    by_system_exact["percent"] = 100 * by_system_exact["count"] / totals
    bands = band_distribution(long)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    overall.to_csv(args.output_dir / "rating_distribution_by_dimension.csv",
                   index=False, float_format="%.6f")
    by_system_exact.to_csv(args.output_dir / "rating_distribution_by_system_dimension.csv",
                           index=False, float_format="%.6f")
    bands.to_csv(args.output_dir / "rating_failure_bands_by_system_dimension.csv",
                 index=False, float_format="%.6f")
    save_overall_plot(overall, args.output_dir / "rating_distribution_by_dimension.png")
    save_system_plot(long, args.output_dir / "rating_distribution_by_system_dimension.png")

    print(f"Retained item-model units: {n_units:,}")
    print(f"Individual annotations in retained units: {len(data):,}")
    print(f"Individual ratings per dimension: {len(data):,}")
    print(f"Saved results to: {args.output_dir}")


if __name__ == "__main__":
    main()
