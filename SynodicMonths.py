#!/usr/bin/env python3

from skyfield.api import load
from skyfield.almanac import find_discrete, moon_phases
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import argparse
import csv


def SynodicMonths(start_date: str, end_date: str):
    # Load ephemeris and timescale
    eph = load("de421.bsp")
    ts = load.timescale()

    # Parse user-provided start and end dates
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    t0 = ts.utc(start_dt.year, start_dt.month, start_dt.day)
    t1 = ts.utc(end_dt.year, end_dt.month, end_dt.day)

    # Find moon phases
    times, phases = find_discrete(t0, t1, moon_phases(eph))

    # Extract new moon times
    new_moon_times_mjd = [t.tt - 2400000.5 for t, p in zip(times, phases) if p == 0]
    new_moon_times = [t.utc_datetime() for t, p in zip(times, phases) if p == 0]

    # Calculate synodic month lengths (in days)
    new_moon_lengths = np.diff([t.timestamp() for t in new_moon_times]) / 86400
    average_length = np.mean(new_moon_lengths)
    print(f"Average length of synodic months: {average_length:.2f} days")

    # Plot the results
    plt.figure(figsize=(10, 5))
    plt.plot(new_moon_times_mjd[:-1], new_moon_lengths, marker="o", linestyle="-")
    plt.title("Length of Each Lunar (Synodic) Month")
    plt.xlabel("Start Date of Lunar Month (MJD)")
    plt.ylabel("Lunar Month Length (days)")
    plt.grid(True)
    plt.tight_layout()
    plt.xticks(rotation=45)

    plot_filename = "synodic_months_plot.png"
    plt.savefig(plot_filename)
    print(f"Plot saved to: {plot_filename}")
    plt.close()

    # Save time bins to CSV
    SynodicTimeBins = [
        (new_moon_times_mjd[i], new_moon_times_mjd[i + 1])
        for i in range(len(new_moon_times_mjd) - 1)
    ]

    csv_filename = "synodic_time_bins.csv"
    with open(csv_filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Start_MJD", "End_MJD"])  # Header
        writer.writerows(SynodicTimeBins)

    print(f"Time bins saved to: {csv_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate the average length of synodic months."
    )
    parser.add_argument(
        "--start_date",
        type=str,
        default="2007-01-01",
        help="Start date for the calculation (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--end_date",
        type=str,
        default="2030-12-31",
        help="End date for the calculation (YYYY-MM-DD).",
    )
    args = parser.parse_args()

    SynodicMonths(args.start_date, args.end_date)
