import logging

from stark.tools.levenshtein import (
    SIMPLEPHONE_PROXIMITY_GRAPH,
    levenshtein_distance_substring,
    levenshtein_matrix,
)

logger = logging.getLogger(__name__)

import numpy as np


if __name__ == "__main__":
    s1 = "imagine dragons"
    s2 = "play imagine dragons and linkin park"

    narrow = False
    proximity_graph = SIMPLEPHONE_PROXIMITY_GRAPH
    ignore_prefix = True
    ignore_suffix = False  # looks like over removing distance info

    dp = levenshtein_matrix(
        s1=s1,
        s2=s2,
        narrow=narrow,
        proximity_graph=proximity_graph,
        ignore_prefix=ignore_prefix,
        ignore_suffix=ignore_suffix,
        max_distance=len(s1) * 0.1,
    )

    import matplotlib.pyplot as plt

    def plot(dp, s1, s2, s1_list=None, s2_list=None):
        """
        Plot the Levenshtein distance matrix using matplotlib.

        Args:
            dp: Distance matrix.
            s1: First string.
            s2: Second string.
            s1_list: Optional custom row labels.
            s2_list: Optional custom column labels.
        """
        s1_list = s1_list or ["s1"] + list(s1)
        s2_list = s2_list or ["s2"] + list(s2)

        def auto_figsize(
            arr: np.ndarray, cell_w: float = 0.6, cell_h: float = 0.6
        ) -> tuple[float, float]:
            return arr.shape[1] * cell_w, arr.shape[0] * cell_h

        fig, ax = plt.subplots(figsize=auto_figsize(dp))
        masked = np.ma.masked_where(dp >= 1e6, dp)
        cax = ax.matshow(masked, cmap="viridis", alpha=0.7)

        for (i, j), val in np.ndenumerate(dp):
            if val < 1e6:
                weight = "bold" if val == 0 else "normal"
                ax.text(
                    j,
                    i,
                    f"{val:.2f}",
                    va="center",
                    ha="center",
                    color="white",
                    fontsize=8,
                    fontweight=weight,
                )

        ax.set_xticks(range(len(s2) + 1))
        ax.set_yticks(range(len(s1) + 1))
        ax.set_xticklabels(s2_list)
        ax.set_yticklabels(s1_list)
        plt.colorbar(cax, ax=ax)
        plt.tight_layout()

    def plot_chart(values: np.ndarray, s2, title: str):
        """
        Plot a bar chart for values using matplotlib.

        Args:
            values: Array of values to plot.
            s2: String for x-axis labels.
            title: Chart title.
        """
        fig, ax = plt.subplots(figsize=(len(s2) * 0.6, 2.5))
        bars = ax.bar(
            range(len(values)),
            values,
            color=plt.cm.viridis(values / (values.max() or 1)),
        )
        for i, val in enumerate(values):
            weight = "bold" if val == 0 else "normal"
            ax.text(
                i,
                val,
                f"{val:.2f}",
                ha="center",
                va="bottom",
                color="white",
                fontsize=8,
                fontweight=weight,
            )
        ax.set_xticks(range(len(s2)))
        ax.set_xticklabels(list(s2))
        ax.set_title(title)
        plt.tight_layout()

    plot(dp, s1, s2)

    matches = levenshtein_distance_substring(
        s1=s1,
        s2=s2,
        narrow=narrow,
        proximity_graph=proximity_graph,
        ignore_prefix=ignore_prefix,
        ignore_suffix=ignore_suffix,
    )

    for span, distance in matches:
        print(span, s2[span.slice], distance)

    plt.show()  # <- show both at once
