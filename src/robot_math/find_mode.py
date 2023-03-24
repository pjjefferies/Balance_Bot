#!/usr/bin/env python3


import numpy as np
import numpy.typing as npt
from scipy import stats
from scipy.optimize import minimize
import timeit
import matplotlib.pyplot as plt

"""
def gamma_mode(data: npt.ArrayLike) -> float:
    # fit the parameters of norm distribution
    params: Tuple[float, float, float] = stats.gamma.fit(data=data)

    return minimize(gamma_density, 0).x
"""


def find_gamma_mode(data: npt.ArrayLike, initial_guess: float = 0.05):
    def gamma_density(data: float, *params: tuple[float, float, float]):
        return -stats.gamma.pdf(data, *params)[0]

    a: float  # shape
    loc: float  # location
    scale: float  # scale (theta)
    try:
        a, loc, scale = stats.gamma.fit(data=data, method="MM")
    except stats.FitError as e:
        print(f"Fit Error: {e}")
        return 0
    """
    print(f"data:/n{data}")
    print(f"a: {a} loc: {loc} scale: {scale}")

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
    plt.show()
    """
    return minimize(
        fun=gamma_density, x0=initial_guess, args=(a, loc, scale), method="Powell"
    ).x[
        0
    ]  # COBYLA - correct result, success=True, time=0.025 s - see initial commit of file for other method results
    # TNC
    # Powell


def main():
    import os

    datafileprefix: str = "2023-01-02_23_4"
    dataoutfilepostfix: str = "_mode_summary_Powell"
    current_dir: str = os.getcwd()
    log_dir: str = os.path.join(current_dir, "logs")

    """
    log_files: list[str] = [
        fname
        for fname in os.listdir(log_dir)
        if (fname.startswith(datafileprefix) and fname.endswith(".csv"))
    ]
    """
    log_files: list[str] = [
        "2023-01-02_23_45_12_position_history.csv",
        "2023-01-02_23_45_34_position_history.csv",
        "2023-01-02_23_45_56_position_history.csv",
        "2023-01-02_23_46_18_position_history.csv",
    ]

    # print(f"log_files: {log_files}")

    for fname in log_files:
        print(f"Processing file: {fname}")
        fname_path: str = os.path.join(log_dir, fname)
        fname_results: str = (
            ".".join(fname.split(".")[:-1]) + dataoutfilepostfix + ".csv"
        )
        fname_path_results = os.path.join(log_dir, fname_results)
        all_data = np.genfromtxt(fname=fname_path, delimiter=",", dtype=float)

        time_step_data: npt.ArrayLike = all_data[:, 1]
        # print(time_step_data[:15])

        result_data: npt.ArrayLike = np.zeros((len(time_step_data), 2))

        no_data: int
        mode: float
        no_data_points = len(time_step_data)

        for no_data in range(no_data_points):
            if no_data % 10 == 0:
                print(f"    Evaluating point {no_data} of {no_data_points}")
            temp_data = time_step_data[: no_data + 1]
            mode = find_gamma_mode(data=temp_data, initial_guess=np.average(temp_data))
            result_data[no_data, 0] = no_data
            result_data[no_data, 1] = mode

            # print(f"no_data: {no_data}, mode: {mode}")

        np.savetxt(
            fname=fname_path_results,
            X=result_data,
            delimiter=",",
            header="Number of Rows, Mode",
        )


if __name__ == "__main__":
    main()
