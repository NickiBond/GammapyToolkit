from importer import *


def MakeLightCurve(path_to_log, datasets, args):
    f = open(path_to_log, "a")
    f.write("--------------------------------------------------\n")
    f.write("Light Curve: \n")
    if args.LightCurveMinEnergy != None:
        e_min = args.LightCurveMinEnergy * u.TeV
    else:
        e_min = args.EnergyAxisMin * u.TeV
    if args.LightCurveBinDuration is not None:
        if args.LightCurveStartTime is not None:
            t_min = args.LightCurveStartTime
        else:
            t_min = min([dataset.gti.time_start[0] for dataset in datasets])
        t_max = max([dataset.gti.time_stop[-1] for dataset in datasets])
        time_bin_size = args.LightCurveBinDuration * u.day
        n_bins = int(((t_max - t_min) / time_bin_size).decompose())
        time_intervals = []
        current_start = t_min
        while current_start < t_max:
            current_end = min(current_start + args.LightCurveBinDuration * u.day, t_max)
            time_intervals.append([current_start, current_end])
            current_start = current_end
        lc_maker = LightCurveEstimator(
            energy_edges=[e_min, 30 * u.TeV],
            source=args.ObjectName,
            reoptimize=False,
            time_intervals=time_intervals,
        )
    else:
        lc_maker = LightCurveEstimator(
            energy_edges=[e_min, 30 * u.TeV], source=args.ObjectName, reoptimize=False
        )
    lc_maker.n_sigma_ul = args.LightCurveNSigmaUL
    lc_maker.selection_optional = args.LightCurveSelectionOptional
    lc = lc_maker.run(datasets)

    # Plot mean of non-ul data points
    mask = ~lc.is_ul.data
    constant_flux = np.mean(lc.flux.data[mask])

    fig, ax = plt.subplots(
        figsize=(8, 6),
    )

    lc.sqrt_ts_threshold_ul = 2
    lc.plot(ax=ax, axis_name="time", sed_type="flux")
    ax.axhline(constant_flux, color="aqua", linestyle="--", label="Mean Flux")
    ax.legend()
    ax.set_title(f"Light Curve for {args.ObjectName}")
    plt.savefig(args.ADir + "/LightCurve/LightCurve.pdf", bbox_inches="tight")
    f.write("Light Curve saved to " + args.ADir + "/LightCurve/LightCurve.pdf\n")
    f.write(
        "Note mean flux line is based on flux points only (i.e. upper limits are ignored.) \n"
    )

    # these lines will print out a table with values for individual light curve bins
    lc.to_table(format="lightcurve", sed_type="flux")[
        "time_min", "time_max", "flux", "flux_err"
    ].write(args.ADir + "/LightCurve/LightCurve.ecsv", overwrite=True)
    f.write(
        "Light Curve Flux Points saved to "
        + args.ADir
        + "/LightCurve/LightCurve.ecsv\n"
    )
    f.write("To open: \n")
    f.write("from astropy.table import Table \n")
    f.write(
        f"LC = Table.read({args.ADir}/LightCurve/LightCurve.ecsv, format='ascii.ecsv') \n"
    )
    f.write("--------------------------------------------------\n")
    f.close()
    return lc
