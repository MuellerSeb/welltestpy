"""
welltestpy subpackage to make diagnostic plots.

.. currentmodule:: welltestpy.tools.diagnostic_plots

The following classes and functions are provided

.. autosummary::
   diagnostic_plot_pump_test

"""
# pylint: disable=C0103


import numpy as np

from ..process import processlib
from . import plotter

import matplotlib.pyplot as plt


def diagnostic_plot_pump_test(
    observation,
    method="bourdet",
    linthresh_time=1.0,
    linthresh_head=1e-5,
    fig=None,
    ax=None,
    plotname=None,
    style="WTP",
):
    """plot the derivative with the original data.

    Parameters
    ----------
    observation : :class:`welltestpy.data.Observation`
         The observation to calculate the derivative.
    method : :class:`str`, optional
        Method to calculate the time derivative.
        Default: "bourdet"
    linthresh_time : :class: 'float'
        Range of time around 0 that behaves linear.
        Default: 1
    linthresh_head : :class: 'float'
        Range of head values around 0 that behaves linear.
        Default: 1e-5
    fig : Figure, optional
        Matplotlib figure to plot on.
        Default: None.
    ax : :class:`Axes`
        Matplotlib axes to plot on.
        Default: None.
    plotname : str, optional
        Plot name if the result should be saved.
        Default: None.
    style : str, optional
        Plot style.
        Default: "WTP".

     Returns
     ---------
     Diagnostic plot
    """
    derivative = processlib.smoothing_derivative(observation, method)
    head, time = observation()
    head = np.array(head, dtype=float).reshape(-1)
    time = np.array(time, dtype=float).reshape(-1)

    # setting variables
    x = time
    y = head
    sx = time
    sy = head
    dx = time[1:-1]
    dy = derivative[1:-1]

    # plotting
    if style == "WTP":
        style = "ggplot"
        font_size = plt.rcParams.get("font.size", 10.0)
        keep_fs = True
    with plt.style.context(style):
        if keep_fs:
            plt.rcParams.update({"font.size": font_size})
        fig, ax = plotter._get_fig_ax(fig, ax)
        ax.scatter(x, y, color="red", label="drawdown")
        ax.plot(sx, sy, c="red")
        ax.plot(dx, dy, c="black", linestyle="dashed")
        ax.scatter(dx, dy, c="black", marker="+", label="time derivative")
        ax.set_xscale("symlog", linthresh=linthresh_time)
        ax.set_yscale("symlog", linthresh=linthresh_head, base=10)
        ax.set_xlabel("$t$ in [s]", fontsize=16)
        ax.set_ylabel("$h$ and $dh/dx$ in [m]", fontsize=16)
        lgd = ax.legend(loc="upper left")
        ax.set_xlim(time[0], time[-1])
        min_v = min(np.min(head), np.min(derivative))
        max_v = max(np.max(head), np.max(derivative))
        max_e = int(np.ceil(np.log10(max_v)))
        if min_v < linthresh_head:
            min_e = -np.inf
        else:
            min_e = int(np.floor(np.log10(min_v)))
        ax.set_ylim(10 ** min_e, 10 ** max_e)
        fig.tight_layout()
        if plotname is not None:
            fig.savefig(
                plotname,
                format="pdf",
                bbox_extra_artists=(lgd,),
                bbox_inches="tight",
            )
    return ax