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
            0.0409825,
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

    # mode1 = gamma_mode(data1)
    params: Tuple[float, float, float] = stats.gamma.fit(data=data)
    a: float  # shape
    loc: float  # location
    scale: float  # scale (theta)
    a, loc, scale = params
    print(f"a: {a}, loc: {loc}, scale: {scale}")

    min_result = minimize(
        fun=gamma_density, x0=0.05, args=(a, loc, scale), method="COBYLA"
    )

    # t = timeit.Timer(lambda: foo(A, B))

    t = timeit.Timer(
        lambda: minimize(
            fun=gamma_density, x0=0.05, args=(a, loc, scale), method="Powell"
        ),
    )
    duration = t.timeit(number=1000)
    print(f"Powell duration: {duration:.2f} seconds")

    t = timeit.Timer(
        lambda: minimize(
            fun=gamma_density, x0=0.05, args=(a, loc, scale), method="TNC"
        ),
    )
    duration = t.timeit(number=1000)
    print(f"TNC duration: {duration} seconds")

    t = timeit.Timer(
        lambda: minimize(
            fun=gamma_density, x0=0.05, args=(a, loc, scale), method="COBYLA"
        ),
    )
    duration = t.timeit(number=1000)
    print(f"COBYLA duration: {duration} seconds")

    # Powell - correct resuts, success=True, time=0.28 s
    # TNC - correct result, success=True, time=0.16 s
    # COBYLA - correct result, success=True, time=0.025 s

    # Nelder-Mead - correct result, success=False
    # CG - incorrect result, success=False
    # BFGS - incorrect result, success=False
    # Newton-CG - couldn't run
    # L-BFGS-B - close result, success=False
    # SLSQP - incorrect result, success=True  #SCARY
    # trust-constr - correct result, success=True but received warning
    # dogleg - couldn't run
    # trust-ncg - couln't run
    # trust-exact - couldn't run
    # trust-krylov - couldn't run

    print(f"min_result: {min_result}")

    mode = min_result.x

    print(f"The mode of data1 is: {mode}.")

    fig, ax = plt.subplots(1, 1)
    ax.hist(
        data,
        density=True,
        bins=[x / 20 / 8 for x in range(1, 21, 1)],
        histtype="stepfilled",
        alpha=0.2,
    )
    # x = np.linspace(stats.gamma.ppf(0.01, a), stats.gamma.ppf(0.99, a), 100)
    x = np.linspace(0.001, 0.125, 1000)

    ax.plot(
        x, stats.gamma.pdf(x, a, loc, scale), "r-", lw=2, alpha=0.6, label="gamma pdf"
    )

    ax.set_xlim([x[0], x[-1]])
    ax.legend(loc="best", frameon=False)
    # plt.show()


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    main()
