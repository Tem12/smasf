"""Module contains function for
plotting public blockchain after simulation.

Author: Jan Jakub Kubik (xkubik32)
Date: 10.4.2023
"""
from typing import Dict, List

import matplotlib.pyplot as plt


def plot_block_counts(block_counts: Dict[str, int], miners_info: List[float]) -> None:
    """
    Plots the percentage of blocks mined by each miner.

    Args:
        block_counts (Dict[str, int]): A dictionary with miner names as keys and
                                       the number of blocks mined as values.
        miners_info (List[float]): A list of mining powers for each miner.

    Returns:
        None
    """
    miner_names = list(block_counts.keys())
    total_blocks = sum(block_counts.values())
    block_percentages = [
        100 * block_counts[name] / total_blocks for name in miner_names
    ]

    mining_powers = miners_info
    mining_power_labels = [f"{power:.1f}%" for power in mining_powers]

    bars = plt.bar(miner_names, block_percentages)

    for bar_new, label, miner_name in zip(bars, mining_power_labels, miner_names):
        height = bar_new.get_height()
        block_count = block_counts[miner_name]
        plt.text(
            bar_new.get_x() + bar_new.get_width() / 2,
            height,
            f"{label}\n{block_count} blocks",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.xlabel("Miner")
    plt.ylabel("Percentage of Blocks Mined")
    plt.title(
        f"Percentage of Blocks Mined by Each Miner (Mining Power and Block "
        f"Count on Top of Bars)\nTotal Blocks: {total_blocks}"
    )
    plt.show()
