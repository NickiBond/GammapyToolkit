import argparse
import re
from astropy.time import Time


def get_parser():
    parser = argparse.ArgumentParser(
        description="DL3 to Dl5 in Gammapy\narguments are as follows: \n",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-Debug",
        help="Make all the debugging plots (i.e. for some plots 1 per run rather than the max of 10). Note: this slows down analysis.Default is False.",
        action="store_true",
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
        help="Radius of the on region in degrees, default = None, in which case the radius from the IRF will be used (point-like)",
        type=float,
        required=False,
        default=None,
    )
    parser.add_argument(
        "-BackgroundMaker",
        help="Background maker to use. Currently only options is 'ReflectedRegions'. Default is 'ReflectedRegions'.",
        type=str,
        required=False,
        default="ReflectedRegions",
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
    parser.add_argument(
        "-SpectralModel",
        required=False,
        default="PowerLaw",
        help="Spectral model or expression of 2 models (e.g., PowerLaw, PowerLawCutOff, BrokenPowerLaw, LogParabola, SmoothBrokenPowerLaw, PowerLaw+ExpCutoff, PowerLaw+LogParabola) \n e.g. PowerLaw+ExpCutoff or PowerLaw+LogParabola and quotes around the expression. \n Default is PowerLaw.",
    )

    # --- PowerLaw group ---
    pl_group = parser.add_argument_group("PowerLaw Spectral Model")
    pl_group.add_argument(
        "-PowerLawIndex",
        type=float,
        default=2.0,
        help="Index of Power Law, default = 2.0",
    )
    pl_group.add_argument(
        "-PowerLawAmplitude",
        type=float,
        default=1e-12,
        help="Amplitude in cm-2 s-1 TeV-1, default = 1e-12",
    )
    pl_group.add_argument(
        "-PowerLawReferenceEnergy",
        type=float,
        default=1.0,
        help="Reference energy in TeV, default = 1.0",
    )

    # --- PowerLawCutOff group ---
    plco_group = parser.add_argument_group("PowerLaw with Exponential Cut Off")
    plco_group.add_argument(
        "-PowerLawCutOffIndex", type=float, default=1.5, help="Index, default = 1.5"
    )
    plco_group.add_argument(
        "-PowerLawCutOffAmplitude",
        type=float,
        default=1e-12,
        help="Amplitude in cm-2 s-1 TeV-1, default = 1e-12",
    )
    plco_group.add_argument(
        "-PowerLawCutOffReferenceEnergy",
        type=float,
        default=1.0,
        help="Reference Energy in TeV, default = 1.0",
    )
    plco_group.add_argument(
        "-PowerLawCutOffAlpha", type=float, default=1.0, help="Alpha, default = 1.0"
    )
    plco_group.add_argument(
        "-PowerLawCutOffLambda",
        type=float,
        default=0.1,
        help="Lambda in TeV^-1, default = 0.1",
    )

    # --- BrokenPowerLaw group ---
    bpl_group = parser.add_argument_group("Broken Power Law")
    bpl_group.add_argument(
        "-BrokenPowerLawIndex1", type=float, default=2.0, help="Index 1, default = 2.0"
    )
    bpl_group.add_argument(
        "-BrokenPowerLawIndex2", type=float, default=2.0, help="Index 2, default = 2.0"
    )
    bpl_group.add_argument(
        "-BrokenPowerLawAmplitude",
        type=float,
        default=1e-12,
        help="Amplitude in cm-2 s-1 TeV-1, default = 1e-12",
    )
    bpl_group.add_argument(
        "-BrokenPowerLawEnergyBreak",
        type=float,
        default=1.0,
        help="Energy Break in TeV, default = 1.0",
    )

    # --- LogParabola group ---
    lp_group = parser.add_argument_group("Log Parabola")
    lp_group.add_argument(
        "-LogParabolaAmplitude",
        type=float,
        default=1e-12,
        help="Amplitude in cm-2 s-1 TeV-1, default = 1e-12",
    )
    lp_group.add_argument(
        "-LogParabolaReferenceEnergy",
        type=float,
        default=10.0,
        help="Reference energy in TeV, default = 10.0",
    )
    lp_group.add_argument(
        "-LogParabolaAlpha", type=float, default=2.0, help="Alpha, default = 2.0"
    )
    lp_group.add_argument(
        "-LogParabolaBeta", type=float, default=1.0, help="Beta, default = 1.0"
    )

    # --- SmoothBrokenPowerLaw group ---
    sbpl_group = parser.add_argument_group("Smooth Broken Power Law")
    sbpl_group.add_argument(
        "-SmoothBrokenPowerLawIndex1",
        type=float,
        default=2.0,
        help="Index 1, default = 2.0",
    )
    sbpl_group.add_argument(
        "-SmoothBrokenPowerLawIndex2",
        type=float,
        default=2.0,
        help="Index 2, default = 2.0",
    )
    sbpl_group.add_argument(
        "-SmoothBrokenPowerLawAmplitude",
        type=float,
        default=1e-12,
        help="Amplitude in cm-2 s-1 TeV-1, default = 1e-12",
    )
    sbpl_group.add_argument(
        "-SmoothBrokenPowerLawEnergyBreak",
        type=float,
        default=1.0,
        help="Energy Break in TeV, default = 1.0",
    )
    sbpl_group.add_argument(
        "-SmoothBrokenPowerLawReferenceEnergy",
        type=float,
        default=1.0,
        help="Reference Energy in TeV, default = 1.0",
    )
    sbpl_group.add_argument(
        "-SmoothBrokenPowerLawBeta", type=float, default=1.0, help="Beta, default = 1.0"
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
        help="Find Light Curve points and plot. default= False.,
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

    parser.add_argument(
        "-LightCurveStartTime", 
        type=parse_time,
        help = "Start time for first bin of light curve. Accepts multiple unit options e.g. mjd:59000, jd:2459000.5, unix:1640995200, or ISO (2022-01-01). Only used if -LightCurveBinDuration is also provided",
        required = False,
        default = None,
    )

    # Exclusion Regions
    parser.add_argument(
        "-exclusion_csv",
        help="Path to a CSV file containing user-defined exclusion regions."
        " The CSV should have columns: ra (deg), dec (deg), radius (deg or with astropy unit).",
        type=str,
        required=False,
        default=None,
    )
    return parser


def CheckAllowedSpectralModelInputted(args):
    AllowedModels = [
        "PowerLaw",
        "PowerLawCutOff",
        "BrokenPowerLaw",
        "LogParabola",
        "SmoothBrokenPowerLaw",
    ]
    parts = re.split(r"([*+])", args.SpectralModel)
    if len(parts) == 1:
        if parts[0] not in AllowedModels:
            raise ValueError(
                f"Unsupported spectral model: {parts[0]}. Allowed models are: {', '.join(AllowedModels)}"
            )
    elif len(parts) == 3:
        model1, operator, model2 = parts
        if operator not in ["*", "+"]:
            raise ValueError(f"Unsupported operator: {operator}")
        if model1 not in AllowedModels:
            raise ValueError(
                f"Unsupported spectral model: {model1}. Allowed models are: {', '.join(AllowedModels)}"
            )
        if model2 not in AllowedModels:
            raise ValueError(
                f"Unsupported spectral model: {model2}. Allowed models are: {', '.join(AllowedModels)}"
            )
    else:
        raise ValueError("Only binary compound models are supported.")

def parse_time(value):
    try:
        if ":" in value:
            fmt, timestr = value.split(":", 1)
            fmt = fmt.lower()
            return Time(timestr, format=fmt, scale="utc")

        # Fallback if no `:` in name.
        return Time(value, scale="utc")

    except Exception as e:
        raise argparse.ArgumentTypeError(
            f"Invalid time '{value}'. "
            "Use e.g. mjd:59000, jd:2459000.5, unix:1640995200, "
            "or ISO (2022-01-01)."
        )