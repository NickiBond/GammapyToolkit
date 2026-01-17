from uncertainties import ufloat
import numpy as np


def DefiniteIntegralPowerLaw(
    # Use ufloats to get uncertainties on the parameters
    E_l,
    E_r,
    Gamma,
    Phi_0,
    E_0,
):
    """
    Use ufloats to get uncertainties on the integral power law
    Note that ufloat does not handle covariance
    """
    return (Phi_0 / ((Gamma + 1) * (E_0**Gamma))) * (
        E_r ** (Gamma + 1) - E_l ** (Gamma + 1)
    )


### Note: This function is used to find the uncertainty on the integral power law.
### HOWEVER, you can just use ufloat from the uncertainties package to find the uncertainty on the integral power law
### Note: ufloat does not handle covariance

"""
def DefiniteIntegralPowerLawError(
    E_l, 
    E_r,
    Gamma,
    Phi_0,
    E_0,
    Gamma_err,
    Phi_0_err
):
    I = DefiniteIntegralPowerLaw(E_l, E_r, Gamma, Phi_0, E_0)
    dIdPhi_0 = I / Phi_0
    dIdGamma = (-np.log(E_0)* I) + (-I/(Gamma + 1)) + (Phi_0/((E_0**Gamma)*(Gamma + 1)) * (E_r**(Gamma+1)*np.log(E_r) - E_l**(Gamma+1)*np.log(E_l)))
    return np.sqrt((dIdPhi_0*Phi_0_err)**2+(dIdGamma*Gamma_err)**2) # Plus covariance term
"""


# Define Power Law Function
def PowerLawFunction(E, index, normalisation):
    """
    Assumes reference energy is 1 TeV
    Input E in TeV
    Accepts Index and Normalisation as ufloats
    Assumes Index has negative in it already (as it has in VEGAS output)
    """
    E_ref = ufloat(1.0, 0.0)
    res = normalisation * (E / E_ref) ** index
    return res


def CrabIntegralFluxPowerLaw(E_l, E_r):
    return DefiniteIntegralPowerLaw(
        E_l=E_l,
        E_r=E_r,
        Gamma=ufloat(2.64, 0),
        Phi_0=ufloat(3.19e-11, 0),
        E_0=ufloat(1, 0),
    )
