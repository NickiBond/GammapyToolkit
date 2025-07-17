from importer import *
def RunDataReductionChain(geom, energy_axis, energy_axis_true, exclusion_mask, observations, obs_ids, path_to_log, args, tmin=None, tmax=None):
    if tmin is not None and tmax is not None:
        WorkingDir = os.path.join(args.ADir, f"TimeBin_{tmin}_{tmax}")
        os.makedirs(WorkingDir, exist_ok=True)
    else:
        WorkingDir = args.ADir
    dataset_maker = SpectrumDatasetMaker(
    selection=["counts", "exposure", "edisp"]
    )
    dataset_empty = SpectrumDataset.create(geom=geom, energy_axis_true=energy_axis_true)
    if args.BackgroundMaker == "ReflectedRegions":
        bkg_maker = ReflectedRegionsBackgroundMaker(exclusion_mask=exclusion_mask)
    elif args.BackgroundMaker == "RingBackground":
        bkg_maker = RingBackgroundMaker(r_in=0.2 * u.deg, r_out=0.4 * u.deg, exclusion_mask=exclusion_mask)
    else:
        raise ValueError(f"Unknown Background Maker: {args.BackgroundMaker}. Choose 'ReflectedRegions' or 'RingBackground'.")
    safe_mask_maker = SafeMaskMaker(methods=["offset-max","aeff-max", "edisp-bias"], offset_max=1.75*u.deg,  aeff_percent=5, bias_percent = 5)
    datasets = Datasets()
    for obs_id, observation in zip(obs_ids, observations):
        dataset = dataset_maker.run(dataset_empty.copy(name=str(obs_id)), observation)
        dataset_on_off = bkg_maker.run(dataset, observation)
        dataset_on_off = safe_mask_maker.run(dataset_on_off, observation)
        datasets.append(dataset_on_off)
    CalculateAndPlotSignificanceAndExcess(datasets, path_to_log, WorkingDir, args, tmin=tmin, tmax=tmax)
    if args.SpectralModel == "PowerLaw":
        spectral_model = PowerLawSpectralModel(
            index=args.PowerLawIndex,
            amplitude=args.PowerLawAmplitude * u.Unit("cm-2 s-1 TeV-1"),
            reference=args.PowerLawReferenceEnergy * u.Unit("TeV"),
        )
    elif args.SpectralModel == "PowerLawCutOff":
        spectral_model = PowerLawSpectralModel(
            index=args.PowerLawCutOffIndex,
            amplitude=args.PowerLawCutOffAmplitude * u.Unit("cm-2 s-1 TeV-1"),
            reference=args.PowerLawCutOffReferenceEnergy * u.Unit("TeV"),
            cutoff=args.PowerLawCutOffEnergy * u.Unit("TeV"),
        )
    elif args.SpectralModel == "BrokenPowerLaw":
        spectral_model = BrokenPowerLawSpectralModel(
            index=args.BrokenPowerLawIndex,
            amplitude=args.BrokenPowerLawAmplitude * u.Unit("cm-2 s-1 TeV-1"),
            reference=args.BrokenPowerLawReferenceEnergy * u.Unit("TeV"),
            break_energy=args.BrokenPowerLawBreakEnergy * u.Unit("TeV"),
        )
    elif args.SpectralModel == "LogParabola":
        spectral_model = LogParabolaSpectralModel(
            amplitude=args.LogParabolaAmplitude * u.Unit("cm-2 s-1 TeV-1"),
            reference=args.LogParabolaReferenceEnergy * u.Unit("TeV"),
            alpha=args.LogParabolaAlpha,
            beta=args.LogParabolaBeta,
        )
    elif args.SpectralModel == "SmoothBrokenPowerLaw":
        spectral_model = SmoothBrokenPowerLawSpectralModel(
            index1=args.SmoothBrokenPowerLawIndex1,
            index2=args.SmoothBrokenPowerLawIndex2,
            amplitude=args.SmoothBrokenPowerLawAmplitude * u.Unit("cm-2 s-1 TeV-1"),
            reference=args.SmoothBrokenPowerLawEnergyReference * u.Unit("TeV"),
            ebreak= args.SmoothBrokenPowerLawEnergyBreak * u.Unit("TeV"),
            beta=args.SmoothBrokenPowerLawBeta,
        )
    model = SkyModel(spectral_model=spectral_model, name=str(args.ObjectName))
    datasets.models = [model]
    fit_joint = Fit()
    fit_result = fit_joint.run(datasets=datasets)
    with open(path_to_log, "a") as f:
        if tmin is not None and tmax is not None:
            f.write(f"Results for time bin {tmin} to {tmax}\n")
        if fit_result.success != True:
            f.write("WARNING: ERROR IN OPTIMISATION")
            f.write(str(fit_result))
        f.write("Fit Results:\n" + str(fit_result.models) + "\n")
        f.write("--------------------------------------------------\n")
    # Plot the fit
    predicted_counts_dir = os.path.join(WorkingDir, "PredictedCounts")
    os.makedirs(predicted_counts_dir, exist_ok=True)
    for i, dataset in enumerate(datasets):
        if args.Debug or i < 10:
            ax_spectrum, ax_residuals = dataset.plot_fit()
            ax_spectrum.set_ylim(0.1, 40)
            plt.savefig(predicted_counts_dir + f"/SpectrumFit_{dataset.name}.pdf")
            with open(path_to_log, "a") as f:
                f.write(f"Saved Spectrum Fit for Obs ID {dataset.name} to {predicted_counts_dir}/SpectrumFit_{dataset.name}.pdf\n")
            plt.close()
    # Next calculate flux points by fitting the fit_result model's amplitude in each energy bin
    flux_points  = FluxPointsEstimator(
        energy_edges = energy_axis.edges,
        source = str(args.ObjectName),
        selection_optional = "all",
        # The lines below are due to a bug in gammapy to do with how it fits non-detection points. This is a workaround for now. 
        norm.min=-1e2,
        norm.max=1e2,
        norm.scan_values=np.array(np.linspace(-10,10,10))
        ).run(datasets=datasets)
    flux_points.to_table().write(
            os.path.join(WorkingDir, "SED.ecsv"), overwrite=True
        )
    
    # Plot the flux points and best fit spectral model
    flux_points_dataset = FluxPointsDataset(
    data=flux_points, models=datasets.models)

    flux_points_dataset.plot_fit()
    plt.savefig(os.path.join(WorkingDir, "SED_FluxPoints.pdf"))
    return fit_result, datasets

def CalculateAndPlotSignificanceAndExcess(datasets, path_to_log, WorkingDir, args, tmin=None, tmax=None):
    info_table = datasets.info_table(cumulative = True)
    with open(path_to_log, "a") as f:
        f.write("--------------------------------------------------\n")
        if tmin is None and tmax is None:
            f.write("Significance and Excess for all observations\n")
        else:
            f.write(f"Significance and Excess for time bin {tmin} to {tmax}\n")
        f.write(f"Total Livetime: {info_table['livetime'].to('h')[-1]:.2f}\n")
        f.write(f"ON: {info_table['counts'][-1]}\n")
        f.write(f"OFF: {info_table['counts_off'][-1]}\n")
        f.write(f"Significance: {info_table['sqrt_ts'][-1]:.2f} sigma\n")
        f.write(f"Alpha: {info_table['alpha'][-1]:.2f}\n")

    fig, (ax_excess, ax_sqrt_ts) = plt.subplots(figsize=(10, 4), ncols=2, nrows=1)
    ax_excess.plot(
        info_table["livetime"].to("h"),
        info_table["excess"],
        marker=".",
    )

    ax_excess.set_title("Excess")
    ax_excess.set_xlabel("Livetime [h]")
    ax_excess.set_ylabel("Excess events")

    ax_sqrt_ts.plot(
        info_table["livetime"].to("h"),
        info_table["sqrt_ts"],
        marker=".",
    )

    ax_sqrt_ts.set_title("Significance")
    ax_sqrt_ts.set_xlabel("Livetime [h]")
    ax_sqrt_ts.set_ylabel(r"Significance [$\sigma$]")
    plt.savefig(WorkingDir + "/SignificanceAndExcess.pdf")
    with open(path_to_log, "a") as f:
       f.write(f"Saving Figure to {WorkingDir}/SignificanceAndExcess.pdf\n")
       f.write("--------------------------------------------------\n")

    return