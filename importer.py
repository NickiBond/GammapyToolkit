#!/usr/bin/env python3

# Standard Library
import os
import argparse
import re
import warnings
from datetime import datetime
import io
from contextlib import redirect_stdout
import operator


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
from matplotlib.collections import PolyCollection

# Astropy
import astropy
import astropy.units as u
from astropy.table import Table
from astropy.time import Time, TimeDelta
from astropy.coordinates import SkyCoord, angular_separation

# Regions & Sky
import regions
from regions import CircleSkyRegion

# Astroquery
import astroquery
from astroquery.vizier import Vizier

# Gammapy
import gammapy
from gammapy.data import DataStore
from gammapy.maps import MapAxis, RegionGeom, WcsGeom, TimeMapAxis
from gammapy.datasets import SpectrumDataset, Datasets, FluxPointsDataset
from gammapy.makers import (
    SpectrumDatasetMaker,
    ReflectedRegionsBackgroundMaker,
    RingBackgroundMaker,
    SafeMaskMaker,
)
from gammapy.modeling import Fit
from gammapy.modeling.models import PowerLawSpectralModel, SkyModel, Models, LogParabolaSpectralModel, BrokenPowerLawSpectralModel, SmoothBrokenPowerLawSpectralModel, ConstantTemporalModel, CompoundSpectralModel
from gammapy.estimators import FluxPointsEstimator, LightCurveEstimator
from gammapy.visualization import plot_spectrum_datasets_off_regions

# Warnings
warnings.filterwarnings("ignore")

# Plot Style
style.use("tableau-colorblind10")

