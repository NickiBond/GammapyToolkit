from importer import *
def RunDataReductionChain(geom, energy_axis, energy_axis_true, exclusion_mask, observations, obs_ids, path_to_log, args, tmin=None, tmax=None):
    if tmin is not None and tmax is not None:
        WorkingDir = os.path.join(args.ADir, f"SpectralVariability/TimeBin_{tmin}_{tmax}")
        os.makedirs(WorkingDir, exist_ok=True)
    else:
        WorkingDir = args.ADir
        os.makedirs(WorkingDir + "/LightCurve", exist_ok=True)
    os.makedirs(WorkingDir + "/Diagnostics", exist_ok=True)
    os.makedirs(WorkingDir + "/Spectrum", exist_ok=True)
    
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
    """
    datasets_not_safe = Datasets()
    datasets = Datasets()
    for obs_id, observation in zip(obs_ids, observations):
        dataset = dataset_maker.run(dataset_empty.copy(name=str(obs_id)), observation)
        dataset_on_off = bkg_maker.run(dataset, observation)
        datasets_not_safe.append(dataset_on_off)
        dataset_on_off = safe_mask_maker.run(dataset_on_off, observation)
        datasets.append(dataset_on_off)
        plt.figure()

    # Significance Calculation
    CalculateAndPlotSignificanceAndExcess(datasets_not_safe, path_to_log, WorkingDir, args, tmin=tmin, tmax=tmax, safe=False)
    CalculateAndPlotSignificanceAndExcess(datasets, path_to_log, WorkingDir, args, tmin=tmin, tmax=tmax, safe=True)
    """
    datasets = Datasets()
    for obs_id, observation in zip(obs_ids, observations):
        dataset = dataset_maker.run(dataset_empty.copy(name=str(obs_id)), observation)
        dataset_on_off = bkg_maker.run(dataset, observation)
        datasets.append(dataset_on_off)
        plt.figure()
    # Significance Calculation
    CalculateAndPlotSignificanceAndExcess(datasets, path_to_log, WorkingDir, args, tmin=tmin, tmax=tmax, safe=False)
    datasets = Datasets()
    for obs_id, observation in zip(obs_ids, observations):
        dataset = dataset_maker.run(dataset_empty.copy(name=str(obs_id)), observation)
        dataset_on_off = bkg_maker.run(dataset, observation)
        dataset_on_off = safe_mask_maker.run(dataset_on_off, observation)
        datasets.append(dataset_on_off)
        plt.figure()

    # Significance Calculation
    CalculateAndPlotSignificanceAndExcess(datasets, path_to_log, WorkingDir, args, tmin=tmin, tmax=tmax, safe=True)


    # Plot on and off regions
    ax = exclusion_mask.plot()
    on_region = CircleSkyRegion(center=SkyCoord.from_name(args.ObjectName).icrs, radius=args.OnRegionRadius * u.deg)
    on_region.to_pixel(ax.wcs).plot(ax=ax, color="lime")
    plot_spectrum_datasets_off_regions(ax=ax, datasets=datasets)
    plt.legend(["ON region"])
    if tmin != None and tmax != None:
        plt.title(f"Exclusion Regions from {tmin} to {tmax}")
        plt.savefig(WorkingDir+ f"/Diagnostics/OnOffExclusionRegionsFrom{tmin}To{tmax}.pdf")
    else:
        plt.title("Exclusion Regions")
        plt.savefig(WorkingDir + "/Diagnostics/OnOffExclusionRegions.pdf")
    plt.close()

    spectral_model = BuildModel(args)
    model = SkyModel(spectral_model=spectral_model, name=str(args.ObjectName))
    with open(path_to_log, "a") as f:
        f.write("Initial Model Parameters \n")
        f.write("Model: " + str(model) + "\n")
        f.write("Spectral Model: " + str(args.SpectralModel) + "\n")
        f.write("Spectral Model Parameters: \n")
        if isinstance(spectral_model, CompoundSpectralModel):
            f.write(f"  Compound Model: {spectral_model.__class__.__name__}\n")
            f.write(f"  Operator: {spectral_model.operator.__name__}\n")

            for i, component in enumerate([spectral_model.model1, spectral_model.model2], start=1):
                f.write(f"  Component {i} ({component.__class__.__name__}):\n")
                for par in component.parameters:
                    f.write(f"    {par.name} = {par.value} {par.unit}\n")
        else:
            f.write(f"  Model: {spectral_model.__class__.__name__}\n")
            for par in spectral_model.parameters:
                f.write(f"    {par.name} = {par.value} {par.unit}\n")
                f.write("--------------------------------------------------\n")
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
    predicted_counts_dir = os.path.join(WorkingDir, "Diagnostics", "PredictedCounts")
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
    fpe  = FluxPointsEstimator(
        energy_edges = energy_axis.edges,
        source = str(args.ObjectName),
        selection_optional = "all",
        )
    # The lines below are due to a bug in gammapy to do with how it fits non-detection points. This is a workaround for now. 
    fpe.norm_min=-1e2,
    fpe.norm_max=1e2,
    fpe.norm.scan_values=np.array(np.linspace(-10,10,10))
    flux_points=fpe.run(datasets=datasets)
    flux_points.to_table().write(
            os.path.join(WorkingDir, "Spectrum/SED.ecsv"), overwrite=True
        )
    
    # Plot the flux points and best fit spectral model
    flux_points_dataset = FluxPointsDataset(
        data=flux_points, 
        models=datasets.models)
    plot_success = safe_plot_fit(flux_points_dataset, WorkingDir=WorkingDir)
    if plot_success:
        with open(path_to_log, "a") as f:
            f.write("Plot generated successfully.\n")
            f.write(f"Saved SED plot to {WorkingDir}/Spectrum/Spectrum_FluxPoints.pdf\n")
    else:
        with open(path_to_log, "a") as f:
            f.write(f"Failed to generate plot {WorkingDir}/Spectrum/Spectrum_FluxPoints.pdf. Continuing...\n")
    return fit_result, datasets

def safe_plot_fit(flux_points_dataset, WorkingDir):
        """Safely attempt to plot fit results, continuing on failure."""
        try:
            flux_points_dataset.plot_fit()
            plt.savefig(os.path.join(WorkingDir, "Spectrum/Spectrum_FluxPoints.pdf"))
            return True
        except ValueError as e:
            if "Axis limits cannot be NaN or Inf" in str(e):
                print(f"Warning: Cannot make plot {WorkingDir}/Spectrum/Spectrum_FluxPoints.pdf. - data contains NaN/Inf values")
            else:
                print(f"Warning: Cannot make plot {WorkingDir}/Spectrum/Spectrum_FluxPoints.pdf. - ValueError: {e}")
            return False
        except Exception as e:
            print(f"Warning: Cannot make plot {WorkingDir}/Spectrum/Spectrum_FluxPoints.pdf. - Unexpected error: {e}")
            return False
        

    
def BuildModel(args):
    models = {}
    if "PowerLaw" in args.SpectralModel:
        models["PowerLaw"] = PowerLawSpectralModel(
            index=args.PowerLawIndex,
            amplitude=args.PowerLawAmplitude * u.Unit("cm-2 s-1 TeV-1"),
            reference=args.PowerLawReferenceEnergy * u.Unit("TeV"),
        )
    if "PowerLawCutOff" in args.SpectralModel:
        models["PowerLawCutOff"] = PowerLawSpectralModel(
            index=args.PowerLawCutOffIndex,
            amplitude=args.PowerLawCutOffAmplitude * u.Unit("cm-2 s-1 TeV-1"),
            reference=args.PowerLawCutOffReferenceEnergy * u.Unit("TeV"),
            cutoff=args.PowerLawCutOffEnergy * u.Unit("TeV"),
        )
    if "BrokenPowerLaw" in args.SpectralModel:
        models["BrokenPowerLaw"] = BrokenPowerLawSpectralModel(
            index=args.BrokenPowerLawIndex,
            amplitude=args.BrokenPowerLawAmplitude * u.Unit("cm-2 s-1 TeV-1"),
            reference=args.BrokenPowerLawReferenceEnergy * u.Unit("TeV"),
            break_energy=args.BrokenPowerLawBreakEnergy * u.Unit("TeV"),
        )
    if "LogParabola" in args.SpectralModel:
        models["LogParabola"] = LogParabolaSpectralModel(
            amplitude=args.LogParabolaAmplitude * u.Unit("cm-2 s-1 TeV-1"),
            reference=args.LogParabolaReferenceEnergy * u.Unit("TeV"),
            alpha=args.LogParabolaAlpha,
            beta=args.LogParabolaBeta,
        )
    if "SmoothBrokenPowerLaw" in args.SpectralModel:
        models["SmoothBrokenPowerLaw"] = SmoothBrokenPowerLawSpectralModel(
            index1=args.SmoothBrokenPowerLawIndex1,
            index2=args.SmoothBrokenPowerLawIndex2,
            amplitude=args.SmoothBrokenPowerLawAmplitude * u.Unit("cm-2 s-1 TeV-1"),
            reference=args.SmoothBrokenPowerLawReferenceEnergy * u.Unit("TeV"),
            ebreak= args.SmoothBrokenPowerLawEnergyBreak * u.Unit("TeV"),
            beta=args.SmoothBrokenPowerLawBeta,
        )
    parts = re.split(r'([+])', args.SpectralModel)
    if len(parts) == 1:
        return models[parts[0]]
    elif len(parts) == 3:
        model1, operation, model2 = parts
        if operation == "+":
            return CompoundSpectralModel(
                models[model1],
                models[model2],
                operator.add
            )
        if operation not in ["+"]:
            raise ValueError(f"Unsupported operator: {operation}")
    else:
        raise ValueError("Only binary compound models are supported.")

def CalculateAndPlotSignificanceAndExcess(datasets, path_to_log, WorkingDir, args, tmin=None, tmax=None, safe = True):
    info_table = datasets.info_table(cumulative = True)
    with open(path_to_log, "a") as f:
        if tmin is None and tmax is None:
            f.write("Significance and Excess for all observations")
        else:
            f.write(f"Significance and Excess for time bin {tmin} to {tmax}\n")
        if safe:
            f.write(" (after safe mask applied)\n")
        else:
            f.write(" (before safe mask applied)\n")
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
    with open(path_to_log, "a") as f:
        if safe:
            plt.savefig(WorkingDir + "/Spectrum/SignificanceAndExcess_Safe.pdf")
            f.write(f"Saving Figure to {WorkingDir}/Spectrum/SignificanceAndExcess_Safe.pdf\n")
        else:
            plt.savefig(WorkingDir + "/Spectrum/SignificanceAndExcess_NotSafe.pdf")
            f.write(f"Saving Figure to {WorkingDir}/Spectrum/SignificanceAndExcess_NotSafe.pdf\n")
        f.write("--------------------------------------------------\n")
    plt.close()
    return