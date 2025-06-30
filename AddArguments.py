import argparse


def get_parser():
    parser = argparse.ArgumentParser(
        description="DL3 to Dl5 in Gammapy\narguments are as follows: \n",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Data Selection Parameters
    parser.add_argument(
        "-ObjectName",
        help="Only accept runs with this object name. Also used to determine source co-ordinates. Required.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-DL3Path",
        help="Path to the DL3 data folder. default= './DL3'",
        type=str,
        required=False,
        default="./DL3,
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
        "-SEDTimeBinFile",
        help="Path to the SED time bin file. If provided, the SED will be computed for each time bin to analyse spectral variability. \nIf not provided, SED will be computed for entire time interval. \nThe time bins must be in the format: 'start_time end_time'.",
        type=str,
        required=False,
        default=None,
    )

    # Light Curve Parameters
    parser.add_argument(
        "-LightCurve",
        help="Find Light Curve points and plot. default= False. Set to False to reduce runtime",
        type=bool,
        required=False,
        default=False,
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
