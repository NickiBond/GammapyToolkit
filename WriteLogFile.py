import sys

sys.path.append("/Users/nickibond/Documents/Research/Toolkit")
from importer import *
from AddArguments import get_parser
args = get_parser().parse_args()


def WritePackageVersionsToLog(path_to_log):
    with open(path_to_log, "a") as f:
        f.write("Packages used:\n")
        f.write("Python version: " + sys.version + "\n")
        f.write("Numpy version: " + np.__version__ + "\n")
        f.write("Scipy version: " + scipy.__version__ + "\n")
        f.write("Astropy version: " + astropy.__version__ + "\n")
        f.write("Regions version: " + regions.__version__ + "\n")
        f.write("Gammapy version: " + gammapy.__version__ + "\n")
        f.write("Astroquery version: " + astroquery.__version__ + "\n")
        f.write("Argparse version: " + argparse.__version__ + "\n")
        f.write("Matplotlib version: " + matplotlib.__version__ + "\n")
        f.write("Pandas version: " + pd.__version__ + "\n")
        f.write("--------------------------------------------------\n")


def WriteInputParametersToLog(path_to_log):
    with open(path_to_log, "a") as f:
        f.write("Input Parameters:\n")
        for arg_name, arg_value in vars(args).items():
            f.write(f"{arg_name}: {arg_value}\n")
        f.write("--------------------------------------------------\n")

def WriteIntegralFluxToLog(fit_result, args, path_to_log, tmin= None, tmax=None):
    if tmin != None and tmax != None:
        with open(path_to_log, "a") as f:
            f.write("Integral Flux for time bin " + str(tmin) + " to " + str(tmax) + ":  \n")
    else:
        with open(path_to_log, "a") as f:
            f.write("-----------------------------------\n")
            f.write("Integral Flux: \n")
            flux,flux_err = fit_result.models[args.ObjectName].spectral_model.integral_error(args.IntegralFluxMinEnergy *u.TeV, 5000*u.TeV)
            f.write(f"Integral flux > {args.IntegralFluxMinEnergy}: {flux.value:.2} +/- {flux_err.value:.2} {flux.unit} \n")
    # IntegralFluxResult = DefiniteIntegralPowerLaw(
    #     E_l=ufloat(args.IntegralFluxMinEnergy, 0),
    #     E_r=ufloat(10000000, 0),
    #     Gamma=ufloat(fit_result.parameters["index"].value, fit_result.parameters["index"].error),
    #     Phi_0=ufloat(
    #         fit_result.parameters["amplitude"].value, fit_result.parameters["amplitude"].error
    #     ),
    #     E_0=ufloat(
    #         fit_result.parameters["reference"].value, fit_result.parameters["reference"].error
    #     ),
    # )
    
    # CrabFlux=CrabIntegralFluxPowerLaw(E_l=ufloat(args.IntegralFluxMinEnergy, 0),E_r=ufloat(10000000, 0))
    # with open(path_to_log, "a") as f:
    #     f.write(
    #         "Minimum Energy for Integral Flux: " + str(args.IntegralFluxMinEnergy) + " TeV \n"
    #     )
    #     f.write("Integral Flux: " + str(IntegralFluxResult) + "\n")
    #     f.write(str(IntegralFluxResult / CrabFlux * 100) + "% Crab" + "\n")
    #     f.write("---------------------------------------------------\n")
    return 
"""
def WriteSignificanceToLog(stacked, path_to_log, tmin=None, tmax=None):
    info_table = stacked.info_table(cumulative = True)
    print(f"Tutorial version Significance: {info_table['sqrt_ts'][-1]:.2f} sigma")
    # n_on = stacked.counts.data.sum()
    # n_off = stacked.counts_off.data.sum()
    # alpha = stacked.alpha.data.mean()
    with open(path_to_log, "a") as f:
        f.write("--------------------------------------------------\n")
        if tmin != None and tmax != None:
            f.write(f"Significance for observations from {tmin} to {tmax}\n")
        else:
            f.write(f"Significance\n")
        
        # f.write("On Counts: " + str(n_on) + "\n")
        # f.write("Off Counts: " + str(n_off) + "\n")
        # f.write("Alpha: " + str(alpha) + "\n")
        # from LiMaSignificance import LMS
        # LiMa = LMS(n_on=n_on, n_off=n_off, alpha=alpha)
        # f.write(f"Significance: {LiMa}\n")
        # print(f"My version: {LiMa}")
    return
"""
