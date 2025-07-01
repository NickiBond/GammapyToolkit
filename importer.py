#!/usr/bin/env python3

# Standard Library
import os
import argparse
import warnings
from datetime import datetime
import io
from contextlib import redirect_stdout


# Scientific / Numeric Libraries
import numpy as np
import pandas as pd
import scipy
from uncertainties import ufloat

# Plotting / Visualization
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.style as style
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from matplotlib.collections import PolyCollection

# Astropy
import astropy
import astropy.units as u
from astropy.table import Table
from astropy.time import Time
from astropy.coordinates import SkyCoord, angular_separation

# Regions & Sky
import regions
from regions import CircleSkyRegion, PointSkyRegion

# Astroquery
import astroquery
from astroquery.vizier import Vizier

# Gammapy
import gammapy
from gammapy import stats
from gammapy.data import DataStore
from gammapy.maps import MapAxis, RegionGeom, WcsGeom
from gammapy.datasets import SpectrumDataset, Datasets, FluxPointsDataset
from gammapy.makers import (
    SpectrumDatasetMaker,
    ReflectedRegionsBackgroundMaker,
    SafeMaskMaker,
)
from gammapy.modeling import Fit
from gammapy.modeling.models import PowerLawSpectralModel, SkyModel, Models
from gammapy.estimators import FluxPointsEstimator, LightCurveEstimator
from gammapy.visualization import plot_spectrum_datasets_off_regions

# My Scripts
from SpectralModels import (
    PowerLawFunction,
    DefiniteIntegralPowerLaw,
    CrabIntegralFluxPowerLaw,
)
from VEGASSpectrum import vegas_spectrum
from AddArguments import get_parser
from WriteLogFile import (
    WritePackageVersionsToLog,
    WriteInputParametersToLog,
    WriteIntegralFluxToLog,
    WriteSignificanceToLog,
)
from SelectRuns import SelectRuns
from Diagnostics import (
    DiagnosticsTotalTimeStats,
    DiagnosticsDeadtimeDistribution,
    DiagnosticsPointingOffsetDistribution,
    DiagnosticsOnOffCounts,
    DiagnosticsPlotOnOffCounts
)
from EnergyAxes import EnergyAxes
from GetGeometry import (
    GetOnRegion,
    GetExclusionRegions,
    GetExclusionMask,
)
from LiMaSignificance import *
from Spectrum import (
    SpectrumTimeBins,
    MakeSpectrumFluxPoints,
    PlotSpectrum,
)
from LightCurve import (
    MakeLightCurve,
    PlotLightCurve,
)
from SpectralVariabilityPlots import MakeSpectralVariabilityPlots
# Warnings
warnings.filterwarnings("ignore")

# Plot Style
style.use("tableau-colorblind10")


