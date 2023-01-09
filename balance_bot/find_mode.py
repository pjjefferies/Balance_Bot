#! /usr/bin/python3


import numpy as np
import numpy.typing as npt
from scipy import stats
from scipy.optimize import minimize
import timeit
from typing import Tuple

"""
def gamma_mode(data: npt.ArrayLike) -> float:
    # fit the parameters of norm distribution
    params: Tuple[float, float, float] = stats.gamma.fit(data=data)

    return minimize(gamma_density, 0).x
"""


def main():
    data: npt.ArrayLike = np.array(
        [
            0.0816066,
            0.0816066,
            0.0409791,
            0.0712433,
            0.101588,
            0.041008,
            0.0411217,
            0.0409477,
            0.1015785,
            0.0410812,
            0.0409825,  # 10
            0.0409279,
            0.040946,
            0.0712287,
            0.1520696,
            0.071275,
            0.101578,
            0.0915549,
            0.1318302,
            0.0409186,
            0.0409307,
            0.0409021,
            0.1318047,
            0.0409203,
            0.0409887,
            0.0409431,
            0.0409384,
            0.1015184,
            0.0409539,
        ]
    )

    def gamma_density(data: float, *params: Tuple[float, float, float]):
        return -stats.gamma.pdf(data, *params)[0]

    a: float  # shape
    loc: float  # location
    scale: float  # scale (theta)
    a, loc, scale = stats.gamma.fit(data=data)
    print(f"a: {a}, loc: {loc}, scale: {scale}")

    mode = minimize(
        fun=gamma_density, x0=0.05, args=(a, loc, scale), method="COBYLA"
    ).x[
        0
    ]  # COBYLA - correct result, success=True, time=0.025 s - see initial commit of file for other method results

    print(f"The mode of data1 is: {mode}.")

    fig, ax = plt.subplots(1, 1)
    ax.hist(
        data,
        density=True,
        bins=[x / 20 / 8 for x in range(1, 21, 1)],
        histtype="stepfilled",
        alpha=0.2,
    )
    x = np.linspace(0.001, 0.125, 1000)

    ax.plot(
        x, stats.gamma.pdf(x, a, loc, scale), "r-", lw=2, alpha=0.6, label="gamma pdf"
    )
    ax.text(0.06, 40, s="".join(["Mode: ", str(round(mode, 4))]))
    ax.set_xlim([x[0], x[-1]])
    ax.legend(loc="best", frameon=False)
    plt.show()


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    main()
