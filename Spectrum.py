from importer import *

def SpectrumTimeBins(args):
    time_bins = []
    try:
        with open(args.SEDTimeBinFile, "r") as tbfile:
            for line in tbfile:
                line = line.split("#")[0].strip()
                if not line:  # skip empty/comment-only lines
                    continue
                parts = line.strip().split()
                if len(parts) == 2:
                    tmin, tmax = map(float, parts)
                    time_bins.append((tmin, tmax))
                else:
                    raise ValueError(f"Invalid line in time bin file: {line}")
    except Exception as e:
        print(f"Error reading time bin file: {e}")
        sys.exit(1)
    return time_bins

def MakeSpectrumFluxPoints(observations, geom, energy_axis, energy_axis_true, on_region, exclusion_mask, args, tmin = None, tmax = None, path_to_log = None):
    f = open(path_to_log, "a")
    # Create empty dataset, background and safe mask makers
    dataset_empty = SpectrumDataset.create(geom=geom, energy_axis_true=energy_axis_true)
    dataset_maker = SpectrumDatasetMaker(
        selection=["counts", "exposure", "edisp"], containment_correction=False # Change to True if you want to use full-enclosure DL3 files.
    )
    # Containment correction False because otherwise get: ValueError: Cannot apply containment correction for point-like IRF.
    bkg_maker = ReflectedRegionsBackgroundMaker(exclusion_mask=exclusion_mask)
    safe_mask_maker = SafeMaskMaker(methods=["aeff-default"], aeff_percent=5, bias_percent = 5, offset_max = 1.7*u.deg)
    # Create the datasets
    datasets = Datasets()
    for obs in observations:
        obs_id = str(obs.obs_id)
        dataset = dataset_maker.run(
            dataset_empty.copy(name=str(obs_id)), obs
        )  # includes total counts but no background regions etc yet
        dataset = bkg_maker.run(
            dataset, obs
        )  # Finds total background counts, excess. No model yet
        dataset = safe_mask_maker.run(dataset, obs)
        datasets.append(dataset)

    # Diagnostic Plot
    plt.figure()
    ax = exclusion_mask.plot()
    on_region.to_pixel(ax.wcs).plot(ax=ax, color="lime")
    plot_spectrum_datasets_off_regions(ax=ax, datasets=datasets)
    plt.legend(["ON region"])
    if tmin != None and tmax != None:
        plt.title(f"Exclusion Regions from {tmin} to {tmax}")
        plt.savefig(args.ADir + f"/OnOffExclusionRegionsFrom{tmin}To{tmax}.pdf")
    else:
        plt.title("Exclusion Regions")
        plt.savefig(args.ADir + "/OnOffExclusionRegions.pdf")
    plt.close()

    # Stack Observations
    info_table = datasets.info_table(cumulative=True)
    stacked = datasets.stack_reduce(name="stacked")
    spectral_model = PowerLawSpectralModel()
    f.write("Spectral Model:" + str(spectral_model.__class__.__name__) + "\n")
    sky_model = SkyModel(spectral_model=spectral_model, name=str(args.ObjectName))
    stacked.models = Models([sky_model])
    fit = Fit()
    fit_result = fit.run(stacked)
    if fit_result.success != True:
        f.write("WARNING: ERROR IN OPTIMISATION")
        f.write(str(fit_result))
    f.write("Fit Results: " + str(stacked.models) + "\n")
    f.write("--------------------------------------------------\n")

    # Make flux points
    fp = FluxPointsEstimator(
        energy_edges=energy_axis.edges,
        source=str(args.ObjectName),
        selection_optional="all",
    ).run(datasets=stacked)
    flux_points_dataset = FluxPointsDataset(data=fp, models=sky_model)
    sed_type = "dnde"

    # Save fp table to ecsv file
    if tmin != None and tmax != None:
        fp.to_table(sed_type=sed_type).write(
            args.ADir + f"/SEDFrom{tmin}to{tmax}.ecsv", overwrite=True
        )
    else:
        fp.to_table(sed_type=sed_type).write(
            args.ADir + "/SED.ecsv", overwrite=True
        )
    f.write("SED Type: " + sed_type + "\n")
    f.write("Flux Points: \n")
    f.write("e_ref  dnde  dnde_err  dnde_ul   is_ul  ts  e_min  e_max  \n")
    for row in fp.to_table(sed_type=sed_type)[
        "e_ref", "dnde", "dnde_err", "dnde_ul", "is_ul", "ts", "e_min", "e_max"
    ]:
        f.write(str(np.array(row)) + "\n")
    f.write("--------------------------------------------------\n")
    if tmin != None and tmax != None: 
        f.write("SED saved to " + args.ADir + f"/SEDFrom{tmin}to{tmax}.ecsv\n")
    else:
        f.write("SED saved to " + args.ADir + "/SED.ecsv\n")
    f.write("To open: \n")
    f.write("from astropy.table import Table \n")
    if tmin != None and tmax != None: 
        f.write(
            "SED = Table.read('"
            + args.ADir
            + f"/SEDFrom{tmin}to{tmax}.ecsv', format='ascii.ecsv') \n"
        )
    else:
        f.write(
            "SED = Table.read('"
            + args.ADir
            + "/SED.ecsv', format='ascii.ecsv') \n"
        )
    f.write("--------------------------------------------------\n")
    f.close()
    return flux_points_dataset, stacked, info_table, fit_result, datasets


def PlotSpectrum(flux_points_dataset, args, path_to_log, tmin = None, tmax = None):
    plt.figure()
    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        sharex=True,
        gridspec_kw={"height_ratios": [10, 4]},
        figsize=(8, 8),
        tight_layout=True,
    )
    ax1.yaxis.set_units(u.Unit("TeV-1 cm-2 s-1"))
    flux_points_dataset.plot_fit(
        ax_spectrum=ax1,
        ax_residuals=ax2,
        kwargs_spectrum={
            "kwargs_fp": {
                "sed_type": "dnde",
                "label": "VEGAS -> Gammapy Flux points",
                "color": "red",
                "capsize": 3,
                "marker": ".",
            },
            "kwargs_model": {
                "sed_type": "dnde",
                "label": "VEGAS -> Gammapy Power Law",
                "color": "red",
            },
        },
        kwargs_residuals={
            "label": "VEGAS -> Gammapy Residuals",
            "color": "red",
            "marker": ".",
            "capsize": 3,
        },
    )
    for collection in ax1.collections:  # Change background region to orange
        if isinstance(collection, PolyCollection):
            collection.set_facecolor("red")
            collection.set_alpha(0.3)
            collection.set_label("VEGAS-> Gammapy Power Law Error")
    # Plotting
    ax1.legend(fontsize=9)
    ax2.legend(loc="lower right", fontsize=9)
    ax2.axhline(0, color="black")
    ax1.set_xlabel(xlabel="", fontsize=11)
    label_resid = r"Residuals: $\frac{\mathrm{data}-\mathrm{model}}{\mathrm{model}}$"
    ax2.set_ylabel(label_resid, fontsize=16)
    if tmin != None and tmax != None:
        ax1.set_title(f"{args.ObjectName} Spectrum from {tmin} to {tmax}", fontsize=16)
    else:
        ax1.set_title(f"{args.ObjectName} Spectrum", fontsize=16)
    ax1.set_ylabel(
        ylabel=r"$\frac{dN}{dE}$ [TeV$^{-1}$ s$^{-1}$ cm$^{-2}$]", fontsize=16
    )
    ax2.set_xlabel(xlabel="Energy [TeV]", fontsize=16)

    # Compare to VEGAS
    if args.VEGASLogFile != None:
        vegas_spectrum(
            args.VEGASLogFile,
            print_points=False,
            plot_points=True,
            IncludeAsymmetricXErrs=True,
            colour="blue",
            alpha=1,
            spectrum_label="VEGAS Spectrum",
            figure=fig,
            ax1=ax1,
            ax2=ax2,
            log_file=path_to_log,
        )
    if tmin != None and tmax != None:
        fig.savefig(args.ADir + f"/SpectrumFrom{tmin}To{tmax}.pdf")
    else:
        fig.savefig(args.ADir + "/Spectrum.pdf")
    plt.close()
    return 
