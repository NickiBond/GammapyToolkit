from importer import *

def MakeLightCurve(path_to_log, datasets, args):
    f = open(path_to_log, "a")
    f.write("--------------------------------------------------\n")
    f.write("Light Curve: \n")
    if args.LightCurveMinEnergy != None:
        e_min = args.LightCurveMinEnergy * u.TeV
    else:
        e_min = args.EnergyAxisMin * u.TeV
    lc_maker = LightCurveEstimator(
        energy_edges=[e_min, 30 * u.TeV], source=args.ObjectName, reoptimize=False
    )
    lc_maker.n_sigma_ul = args.LightCurveNSigmaUL
    lc_maker.selection_optional = args.LightCurveSelectionOptional
    lc = lc_maker.run(datasets)
    fig, ax = plt.subplots(
        figsize=(8, 6),
    )

    lc.sqrt_ts_threshold_ul = 2
    lc.plot(ax=ax, axis_name="time",sed_type='flux')
    ax.set_title(f"Light Curve for {args.ObjectName}")
    plt.savefig(args.ADir + "/LightCurve.pdf", bbox_inches="tight")
    f.write("Light Curve saved to " + args.ADir + "/LightCurve.pdf\n")


    # these lines will print out a table with values for individual light curve bins
    lc.to_table(format="lightcurve", sed_type="flux")["time_min", "time_max", "flux", "flux_err"].write(
        args.ADir + "/LightCurve.ecsv", overwrite=True)
    f.write("Light Curve Flux Points saved to " + args.ADir + "/LightCurve.ecsv\n")
    f.write("To open: \n")
    f.write("from astropy.table import Table \n")
    f.write(f"LC = Table.read({args.ADir}/LightCurve.ecsv, format='ascii.ecsv') \n")
    f.write("--------------------------------------------------\n")
    f.close()
    """
    spectral_model = PowerLawSpectralModel()
    f.write("Spectral Model:" + str(spectral_model.__class__.__name__) + "\n")
    sky_model = SkyModel(spectral_model=spectral_model, name=str(args.ObjectName))
    datasets.models = Models([sky_model])
    fit = Fit()
    result = fit.run(datasets)
    if result.success != True:
        f.write("WARNING: ERROR IN OPTIMISATION")
        f.write(str(result))
    bin_duration = args.LightCurveBinDuration * u.day
    n_time_bins = (
        Time(args.ToDate).mjd - Time(args.FromDate).mjd
    ) / bin_duration.value  # Number of bins is Total Time / Duration of 1 Bin
    times = (
        Time(args.FromDate) + np.arange(n_time_bins + 1) * bin_duration
    )  # np.arange rounds down to the nearest bin so add 1 to ensure we go to end of time period
    time_intervals = [
        Time([tstart, tstop]) for tstart, tstop in zip(times[:-1], times[1:])
    ]
    f.write("\n")
    f.write("Time Intervals: \n")
    for interval in time_intervals:
        f.write(str(interval) + "\n")
    if args.LightCurveMinEnergy != None:
        e_min = args.LightCurveMinEnergy * u.TeV
    else:
        e_min = args.EnergyAxisMin * u.TeV
    e_max = args.EnergyAxisMax * u.TeV

    lc_maker = LightCurveEstimator(
        energy_edges=[e_min, e_max],
        time_intervals=time_intervals,
        source=args.ObjectName,
        n_jobs=6,
        n_sigma_ul=args.LightCurveNSigmaUL,
        n_sigma=args.LightCurveNSigma,
        selection_optional=args.LightCurveSelectionOptional,
    )
    lc = lc_maker.run(datasets)
    # print("LightCurve object info:")
    # print(lc)
    # print("Axes:", lc.axes)
    # print("Available columns:", lc.table.colnames)
    # print("Units of time_min:", lc.table['time_min'].unit)
    # print("Units of time_max:", lc.table['time_max'].unit)
    # print("Units of flux:", lc.table['flux'].unit)
    average_flux = np.nanmean(lc.flux.data)

    f.write("Light CurveFlux Points: \n")
    i = 0
    f.write(
        "time_min   time_max   e_min  e_max  flux   flux_err    ts    sqrt_ts  stat    stat_null   success \n"
    )
    for row in lc.to_table(sed_type="flux")[
        "time_min",
        "time_max",
        "e_min",
        "e_max",
        "flux",
        "flux_err",
        "ts",
        "sqrt_ts",
        "stat",
        "stat_null",
        "success",
    ]:
        # print(row)
        f.write(str(np.array(row)) + "\n")
        i += 1
    f.write("Size of LC Table:" + str(i) + "\n")

    # Write Light Curve to file
    lc.to_table(sed_type="flux").write(args.ADir + "/LC.ecsv", overwrite=True)
    f.write("--------------------------------------------------\n")
    f.write("Light Curve saved to " + args.ADir + "/LC.ecsv\n")
    f.write("To open: \n")
    f.write("from astropy.table import Table \n")
    f.write("LC = Table.read( +'" + args.ADir + "LC.ecsv', format='ascii.ecsv') \n")
    f.write("--------------------------------------------------\n")
    """
    return lc

def PlotLightCurve(lc, args, path_to_log):
    start_time_mjd = Time(args.FromDate).mjd
    end_time_mjd = Time(args.ToDate).mjd

    lc.plot(
        sed_type="flux",
        axis_name="time",
        time_format="mjd",
        color="blue",
        marker=".",
        alpha=0.5,
        markersize=5,
        label=f"VEGAS -> Gammapy LightCurve with {args.LightCurveBinDuration} day bins",
    )

    def format_mjd(x, pos):
        return f"{x:.0f}"

    if args.LightCurveComparisonPoints != None:
        with open(args.LightCurveComparisonPoints, "r") as EDLCfile:
            comparison_data = np.loadtxt(EDLCfile, delimiter=",")
        comparison_time = comparison_data[0, :] + 29.53 / 2.0 #TODO: This is just for the data Leo gave me as it has start times not mean times for bins
        comparison_flux = comparison_data[1, :]
        comparison_flux_err = comparison_data[2, :]

        plt.errorbar(
            comparison_time,
            comparison_flux,
            yerr=comparison_flux_err,
            fmt=".",
            label="ED Light Curve",
            color="orange",
            alpha=0.5,
        )
    if args.LightCurveComparisonULs != None:
        with open(args.LightCurveComparisonULs, "r") as EDLCfile:
            comparison_data = np.loadtxt(EDLCfile, delimiter=",")
        comparison_time = comparison_data[0, :]
        comparison_flux = comparison_data[1, :]
        comparison_flux_err = comparison_data[2, :]

        plt.errorbar(
            comparison_time,
            comparison_flux,
            yerr=comparison_flux_err,
            fmt="v",
            label="ED Upper Limits",
            color="orange",
            alpha=0.5,
        )
    plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(format_mjd))
    plt.xlim(start_time_mjd, end_time_mjd)

    plt.xlabel("Time")
    plt.yscale("linear")
    plt.grid()
    # plt.axhline(average_flux, color="black", linestyle="--", label="Average Flux")
    plt.axhline(0, color="black")
    plt.ylim(
        0, 1.2 * np.nanmax(lc.flux.data)
    )  # Should be based on comparison data as well if exists
    plt.legend()
    plt.savefig(args.ADir + "/LightCurve.pdf", bbox_inches="tight")
    plt.close()

    return 