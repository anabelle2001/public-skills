"""Shared Matplotlib plot formatting for this paper."""

from matplotlib.axes import Axes
from matplotlib.ticker import EngFormatter


def label_si_axes(
    ax: Axes, *, x_label: str, x_unit: str, y_label: str, y_unit: str
) -> None:
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.xaxis.set_major_formatter(EngFormatter(unit=x_unit))
    ax.yaxis.set_major_formatter(EngFormatter(unit=y_unit))
