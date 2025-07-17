import argparse

def get_parser():
    parser = argparse.ArgumentParser(
        description="DL3 to Dl5 in Gammapy\narguments are as follows: \n",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-Debug",
        help="Make all the debugging plots (i.e. for some plots 1 per run rather than the max of 10). Note: this slows down analysis.Default is False.",
        action="store_true"
    )

    # Data Selection Parameters
    parser.add_argument(
        "-ObjectName",
        help="Only accept runs with this object name. Also used to determine source co-ordinates. Required.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-IncludeNearby",
        help="Include observations of sources within 5 deg of <ObjectName> in the analysis. default= False",
        action="store_true",
    )
    parser.add_argument(
        "-DL3Path",
        help="Path to the DL3 data folder. default= './DL3'",
        type=str,
        required=False,
        default="./DL3",
    )
    parser.add_argument(
        "-ADir",
        help="Path to the directory to save the analysis. default= './'",
        type=str,
        required=False,
        default="./",
    )
    parser.add_argument(
        "-RunList",
        help="Path to the Run List. If not provided, all runs in the DL3Path directory will be used.",
        type=str,
        required=False,
    )
    parser.add_argument(
        "-RunExcludeList",
        help="Path to a List of Runs to be Excluded. If not provided, all runs in the DL3Path directory will be used.",
        type=str,
        required=False,
    )
    parser.add_argument(
        "-FromDate",
        help="Only accept runs after a certain date. Use format yyyy-mm-ddThh:mm:ss. Also used to set start time of light curve. default= '2007-01-01'.",
        type=str,
        required=False,
        default="2007-01-01",
    )
    parser.add_argument(
        "-ToDate",
        help="Only accept runs before a certain date. Use format yyyy-mm-ddThh:mm:ss. Note that the LC will extend a partial bin beyond this.default= '2030-01-01'.",
        type=str,
        required=False,
        default="2030-01-01",
    )
    parser.add_argument(
        "-OnRegionRadius",
        help="Radius of the on region in degrees, default =0.07071068 to match VEGAS IRFs",
        type=float,
        required=False,
        default=0.07071068,
    )

    # Energy Axis Parameters
    parser.add_argument(
        "-EnergyAxisMin",
        help="Minimum value of energy axis (unit: TeV), default =0.1 TeV",
        type=float,
        required=False,
        default=0.1,
    )
    parser.add_argument(
        "-EnergyAxisMax",
        help="Maximum value of energy axis (unit: TeV), default =100 TeV",
        type=float,
        required=False,
        default=100,
    )
    parser.add_argument(
        "-EnergyAxisBins",
        help="Number of bins in energy axis, default =10",
        type=int,
        required=False,
        default=10,
    )
    
    # Spectral Model Parameters
    # Power Law Parameters
    subparsers = parser.add_subparsers(dest="SpectralModel", required=True, help="Choose a spectral model")
    powerlaw_parser = subparsers.add_parser(
        "PowerLaw", help="Use a Power Law Spectral Model with default parameters"
    )
    powerlaw_parser.add_argument(
        "-PowerLawIndex",
        help="Index of the Power Law Spectral Model, default =2.0",
        default=2.0,
        type=float,
        required=False,
    )
    powerlaw_parser.add_argument(
        "-PowerLawAmplitude",
        help="Amplitude of the Power Law Spectral Model in cm-2 s-1 TeV-1, default =1e-12",
        default=1e-12,
        type=float,
        required=False,
    )
    powerlaw_parser.add_argument(
        "-PowerLawReferenceEnergy",
        help="Reference Energy of the Power Law Spectral Model in TeV, default =1.0",
        default=1.0 ,
        type=float,
        required=False,
    )
    ## Power Law with Exponential Cut Off Parameters
    powerlaw_cutoff_parser = subparsers.add_parser(
        "PowerLawCutOff",
        help="Use a Power Law with Exponential Cut Off Spectral Model with default parameters",
    )
    powerlaw_cutoff_parser.add_argument(
        "-PowerLawCutOffIndex",
        help="Index of the Power Law with Exponential Cut Off Spectral Model, default =2.0",
        default=1.5,
        type=float,
        required=False,
    )
    powerlaw_cutoff_parser.add_argument(
        "-PowerLawCutOffAmplitude",
        help="Amplitude of the Power Law with Exponential Cut Off Spectral Model in cm-2 s-1 TeV-1, default =1e-12",
        default=1e-12,
        type=float,
        required=False,
    )
    powerlaw_cutoff_parser.add_argument(
        "-PowerLawCutOffReferenceEnergy",
        help="Reference Energy of the Power Law with Exponential Cut Off Spectral Model in TeV, default =1.0",
        default=1.0,
        type=float,
        required=False,
    )
    powerlaw_cutoff_parser.add_argument(
        "-PowerLawCutOffAlpha",
        help="Alpha of the Power Law with Exponential Cut Off Spectral Model, default =1.0",
        default=1.0,
        type=float,
        required=False,
    )
    powerlaw_cutoff_parser.add_argument(
        "-PowerLawCutOffLambda",
        help="Lambda of the Power Law with Exponential Cut Off Spectral Model in units of TeV-1, default =0.1",
        default=0.1,
        type=float,
        required=False,
    )
    # Broken PowerLaw
    broken_powerlaw_parser = subparsers.add_parser(
        "BrokenPowerLaw",
        help="Use a Broken Power Law Spectral Model with default parameters",
    )
    broken_powerlaw_parser.add_argument(
        "-BrokenPowerLawIndex1",
        help="Index of the first segment of the Broken Power Law Spectral Model, default =2.0",
        default=2.0,
        type=float,
        required=False,
    )
    broken_powerlaw_parser.add_argument(
        "-BrokenPowerLawIndex2",
        help="Index of the second segment of the Broken Power Law Spectral Model, default =2.0",
        default=2.0,
        type=float,
        required=False,
    )
    broken_powerlaw_parser.add_argument(
        "-BrokenPowerLawAmplitude",
        help="Amplitude of the Broken Power Law Spectral Model in cm-2 s-1 TeV-1, default =1e-12",
        default=1e-12,
        type=float,
        required=False,
    )
    broken_powerlaw_parser.add_argument(
        "-BrokenPowerLawEnergyBreak",
        help="Energy Break of the Broken Power Law Spectral Model in TeV, default =1.0",
        default=1.0,
        type=float,
        required=False,
    )

    log_parabola_parser = subparsers.add_parser(
        "LogParabola",
        help="Use a Log Parabola Spectral Model with default parameters",
    )
    log_parabola_parser.add_argument(
        "-LogParabolaAmplitude",
        help="Amplitude of the Log Parabola Spectral Model in cm-2 s-1 TeV-1, default =1e-12",
        default=1e-12,
        type=float,
        required=False,
    )
    log_parabola_parser.add_argument(
        "-LogParabolaReferenceEnergy",
        help="Reference Energy of the Log Parabola Spectral Model in TeV, default =10",
        default=10.0,
        type=float,
        required=False,
    )
    log_parabola_parser.add_argument(
        "-LogParabolaAlpha",
        help="Alpha of the Log Parabola Spectral Model, default = 2.0",
        default=2.0,
        type=float,
        required=False,
    )
    log_parabola_parser.add_argument(
        "-LogParabolaBeta",
        help="Beta of the Log Parabola Spectral Model, default = 1.0",
        default=1.0,
        type=float,
        required=False,
    )

    # Smooth Broken Power Law
    smooth_broken_powerlaw_parser = subparsers.add_parser(
        "SmoothBrokenPowerLaw",
        help="Use a Smooth Broken Power Law Spectral Model with default parameters",
    )
    smooth_broken_powerlaw_parser.add_argument(
        "-SmoothBrokenPowerLawIndex1",
        help="Index of the first segment of the Smooth Broken Power Law Spectral Model, default =2.0",
        default=2.0,
        type=float,
        required=False,
    )
    smooth_broken_powerlaw_parser.add_argument(
        "-SmoothBrokenPowerLawIndex2",
        help="Index of the second segment of the Smooth Broken Power Law Spectral Model, default =2.0",
        default=2.0,
        type=float,
        required=False,
    )
    smooth_broken_powerlaw_parser.add_argument(
        "-SmoothBrokenPowerLawAmplitude",
        help="Amplitude of the Smooth Broken Power Law Spectral Model in cm-2 s-1 TeV-1, default =1e-12",
        default=1e-12,
        type=float,
        required=False,
    )
    smooth_broken_powerlaw_parser.add_argument(
        "-SmoothBrokenPowerLawEnergyBreak",
        help="Energy Break of the Smooth Broken Power Law Spectral Model in TeV, default =1.0",
        default=1.0,
        type=float,
        required=False,
    )
    smooth_broken_powerlaw_parser.add_argument(
        "-SmoothBrokenPowerLawEnergyReference",
        help="Energy Reference of the Smooth Broken Power Law Spectral Model in TeV, default =1",
        default=1.0,
        type=float,
        required=False,
    )

    smooth_broken_powerlaw_parser.add_argument(
        "-SmoothBrokenPowerLawBeta",
        help="Beta of the Smooth Broken Power Law Spectral Model, default =1.0",
        default=1.0,
        type=float,
        required=False,
    )

    # SED Parameters
    parser.add_argument(
        "-VEGASLogFile",
        help="Path to VEGAS Stage 6 Log File. If provided, VEGAS flux points are plotted with gammapy flux points for comparison",
        type=str,
        required=False,
    )
    parser.add_argument(
        "-IntegralFluxMinEnergy",
        help="Minimum Energy value (in TeV) of the integral flux. Note Gammapy jumps to the nearest energy bin edge.",
        type=float,
        required=False,
        default=0.2,
    )
    parser.add_argument(
        "-SpectralVariabilityTimeBinFile",
        help="Path to the Spectral Variability time bin file. If provided, the Spectral Variability will be computed for each time bin to analyse spectral variability. \nIf not provided, Spectral Variability will be computed for entire time interval. \nThe time bins must be in the format: 'start_time end_time'.",
        type=str,
        required=False,
        default=None,
    )

    # Light Curve Parameters
    parser.add_argument(
        "-LightCurve",
        help="Find Light Curve points and plot. default= False. Set to False to reduce runtime",
        action="store_true",
    )
    parser.add_argument(
        "-LightCurveBinDuration",
        help="Duration of each bin in the light curve. default= 1 day",
        type=float,
        required=False,
        default=1,
    )
    parser.add_argument(
        "-LightCurveMinEnergy",
        help="Minimum Energy value (in TeV) of the light curve. If not provided EnergyAxisMin is used. Note Gammapy jumps to the nearest energy bin edge.",
        type=float,
        required=False,
    )
    parser.add_argument(
        "-LightCurveNSigma",
        help="Number of sigma to use for LightCurve asymmetric error computation. Default is 1. default= 1",
        type=float,
        required=False,
        default=1,
    )
    parser.add_argument(
        "-LightCurveNSigmaUL",
        help="Number of sigma to use for LightCurve upper limit computation. Default is 2. default= 2",
        type=float,
        required=False,
        default=2,
    )
    parser.add_argument(
        "-LightCurveSelectionOptional",
        help=f"Selection Optional for LightCurve. default= None. Options are Which steps to execute. Available options are: \n“all”: all the optional steps are executed. \n“errn-errp”: estimate asymmetric errors. \n“ul”: estimate upper limits. \n“scan”: estimate fit statistic profiles.",
        type=str,
        required=False,
        default=None,
    )
    parser.add_argument(
        "-LightCurveComparisonPoints",
        help="CSV of ED points for comparison of light curves. If provided, the light curves will both be plotted.",
        type=str,
        required=False,
        default=None,
    )

    parser.add_argument(
        "-LightCurveComparisonULs",
        help="CSV of ED upper limits for comparison of light curves. If provided, the light curves will both be plotted.",
        type=str,
        required=False,
        default=None,
    )
    return parser
