#!/usr/bin/env python3
"""
Calulate Cumulative Average of series based on previous running
average, new value and number of history points
"""


def cumulative_average(
    *, prev_cumulative_average: float, new_value: float, number_of_history_points: int
):
    return (
        new_value + (number_of_history_points - 1) * prev_cumulative_average
    ) / number_of_history_points
