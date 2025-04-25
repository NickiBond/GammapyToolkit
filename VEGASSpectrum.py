#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
from uncertainties import ufloat
from SpectralModels import PowerLawFunction


def vegas_spectrum(
    file_path,
    print_points=False,
    plot_points=False,
    IncludeAsymmetricXErrs=True,
    colour="blue",
    alpha=0.5,
    spectrum_label="VEGAS Spectrum",
    figure=None,
    ax1=None,
    ax2=None,
    log_file=None,
):
    if log_file is not None:
        logf = open(log_file, "a")
        logf.write("VEGAS Spectral Model Results (for comparison) \n")
        logf.close()

    all_data = pd.DataFrame()
    RelevantData = False

    # Columns are now defined outside of conditionals
    columns = [
        "Bin",
        "Energy",
        "E_error",
        "Flux",
        "Flux_error",
        "Non",
        "Noff",
        "Nexcess",
        "RawOff",
        "Alpha",
        "Sig",
        "Low_Edge",
        "High_Edge",
    ]

    with open(file_path, "r") as f:
        for line in f:
            stripped_line = line.strip()
            split_line = line.split()

            if (
                stripped_line
                == "Bin    Energy    error     Flux    error  Non    Noff Nexcess  RawOff Alpha    Sig  Low Edge High Edge"
            ):
                RelevantData = True
            elif stripped_line == "****************************************":
                RelevantData = False
            elif RelevantData:
                if len(split_line) == 14:  # Spectrum data point
                    new_row = pd.DataFrame([split_line[1:]], columns=columns)
                    new_row["is_upper_limit"] = False
                    all_data = pd.concat([all_data, new_row], ignore_index=True)
                elif len(split_line) == 13:  # Upper limit
                    new_row = pd.DataFrame([split_line], columns=columns)
                    new_row["is_upper_limit"] = True
                    all_data = pd.concat([all_data, new_row], ignore_index=True)
            if line.strip()[0:4] == "Norm":
                v_norm = ufloat(float(line.split()[2]), float(line.split()[4]))
            if line.strip()[0:5] == "Index":
                v_index = ufloat(float(line.split()[2]), float(line.split()[4]))

    # Convert columns to correct dtypes
    float_columns = [
        "Energy",
        "E_error",
        "Flux",
        "Flux_error",
        "Non",
        "Noff",
        "Nexcess",
        "RawOff",
        "Alpha",
        "Sig",
        "Low_Edge",
        "High_Edge",
    ]
    all_data["Bin"] = all_data["Bin"].astype("int32")
    all_data[float_columns] = all_data[float_columns].astype("float64")

    # Fix yerr for plotting: set Flux_error to 0 for upper limits to avoid errors
    safe_yerr = all_data["Flux_error"].copy()
    safe_yerr[all_data["is_upper_limit"]] = (
        0.5 * all_data["Flux"]
    )  # Set to 50% of flux for upper limits

    # VEGAS Power Law
    energy_vals = np.logspace(-1, 2, 10000)
    VEGAS_PL_val = []
    VEGAS_PL_err = []
    VEGAS_PL = PowerLawFunction(
        index=v_index, E=energy_vals, normalisation=v_norm / 10000
    )
    for val in VEGAS_PL:
        VEGAS_PL_val.append(val.nominal_value)
        VEGAS_PL_err.append(val.std_dev)
    VEGAS_PL_val = np.array(VEGAS_PL_val)
    VEGAS_PL_err = np.array(VEGAS_PL_err)

    # VEGAS Residuals
    v_residuals = []
    v_energy = []
    v_flux = []
    for i in range(0, len(all_data)):
        if not all_data.iloc[i]["is_upper_limit"]:
            v_energy.append(
                all_data.iloc[i]["Energy"],
            )
            v_flux.append(
                ufloat(
                    all_data.iloc[i]["Flux"],
                    all_data.iloc[i]["Flux_error"],
                )
            )
    v_flux = np.array(v_flux)
    v_energy = np.array(v_energy)
    model_for_residuals = PowerLawFunction(v_energy, v_index, v_norm)

    v_residuals = (v_flux - model_for_residuals) / model_for_residuals
    v_residuals_val = [val.n for val in v_residuals]
    v_residuals_std = [val.s for val in v_residuals]

    if log_file is not None:
        logf = open(log_file, "a")
        logf.write("VEGAS Normalisation Constant:" + str(v_norm) + "\n")
        logf.write("VEGAS Index:" + str(v_index) + "\n")
        logf.close()

    if print_points:
        print("VEGAS Spectrum Data Points:")
        print(all_data)

    if plot_points:

        if figure is None:
            figure, (ax1, ax2) = plt.subplots(
                2,
                1,
                sharex=True,
                gridspec_kw={"height_ratios": [10, 4]},
                figsize=(8, 8),
                tight_layout=True,
            )
        else:
            ax1 = figure.axes[0]
            ax2 = figure.axes[1]
            ax1.set_xlabel("Energy [TeV]")
            ax1.set_ylabel(
                r"dN/dE $\left[\frac{1}{\text{cm}^2 \, \text{s} \, \text{TeV}}\right]$"
            )

        if IncludeAsymmetricXErrs:
            data_xerr = [
                all_data["Energy"] - all_data["Low_Edge"],
                all_data["High_Edge"] - all_data["Energy"],
            ]
            data_points_xerr = [  # Exclude ULs for residual plot
                all_data["Energy"][all_data["is_upper_limit"] == False]
                - all_data["Low_Edge"][all_data["is_upper_limit"] == False],
                all_data["High_Edge"][all_data["is_upper_limit"] == False]
                - all_data["Energy"][all_data["is_upper_limit"] == False],
            ]
        else:
            data_xerr = all_data["E_error"]
            data_points_xerr = all_data["E_error"][all_data["is_upper_limit"] == False]

        # Plot data points
        ax1.errorbar(
            all_data["Energy"].values,
            all_data["Flux"].values / 10000,
            xerr=data_xerr,
            yerr=safe_yerr.values / 10000,
            linestyle="None",
            marker=".",
            capsize=3,
            label=spectrum_label,
            color=colour,
            uplims=all_data["is_upper_limit"].values,
            alpha=alpha,
        )
        print("Warning: length of upper limit arrows set at 50% of flux")

        ax2.errorbar(
            x=v_energy,
            y=v_residuals_val,
            xerr=data_points_xerr,  # Accounts for Asymetric X errors if flag on.
            yerr=v_residuals_std,
            linestyle="None",
            marker=".",
            capsize=3,
            color="blue",
            label="VEGAS Residuals",
        )

        ax1.plot(energy_vals, VEGAS_PL_val, color="b", label="VEGAS Power Law")
        ax1.fill_between(
            x=energy_vals,
            y1=VEGAS_PL_val - VEGAS_PL_err,
            y2=VEGAS_PL_val + VEGAS_PL_err,
            color="blue",
            alpha=0.3,
            label="VEGAS Power Law Error",
        )
        ax1.legend()
        ax2.legend()
    return all_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Look at VEGAS spectrum data.")
    parser.add_argument("file_path", help="Path to the VEGAS Stage 6 log file.")
    parser.add_argument(
        "--print_points", action="store_true", help="Print the data points."
    )
    parser.add_argument(
        "--plot_points", action="store_true", help="Plot the data points."
    )
    parser.add_argument(
        "--IncludeAsymmetricXErrs",
        action="store_true",
        help="Include asymmetric X errors in the plot.",
    )
    parser.add_argument(
        "--colour", type=str, default="blue", help="Colour of the plot points."
    )
    parser.add_argument(
        "--alpha", type=float, default=0.5, help="Transparency of the plot points."
    )
    parser.add_argument(
        "--spectrum_label",
        type=str,
        default="VEGAS Flux Points",
        help="Label for the spectrum.",
    )
    parser.add_argument("--figure", type=str, default=None, help="Figure to add to.")
    parser.add_argument("--ax1", type=str, default=None, help="Axis 1 to add to.")
    parser.add_argument("--ax2", type=str, default=None, help="Axis 2 to add to.")
    parser.add_argument(
        "--log_file", type=str, default=None, help="Log file to write to."
    )

    args = parser.parse_args()

    vegas_spectrum(
        args.file_path,
        print_points=args.print_points,
        plot_points=args.plot_points,
        IncludeAsymmetricXErrs=args.IncludeAsymmetricXErrs,
        colour=args.colour,
        alpha=args.alpha,
        spectrum_label=args.spectrum_label,
        figure=args.figure,
        log_file=None,
    )
