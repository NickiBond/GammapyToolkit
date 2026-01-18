#!/usr/bin/env python3
"""
Author: Nicki Bond
Date: 2025-Jan
TLDR: This script will take the VEGAS DL3 data files and use gammapy 2.0 to do various science things

Purpose:
- It takes a set of DL3 files and makes an energy spectrum using Gammapy.
- It also can plot the VEGAS spectrum on the same plot if a VEGAS Stage 6 log file is provided.
- It can also make a light curve. There are options for the user to change the parameters of gammapy's LightCurveEstimator.

Scope:
- This script has only been tested on point sources.
- Most of the testing has been done with VEGAS DL3 files.

To Run:
- Activate an environment with required packages installed. See EnvironmentPackages.txt for details.
- Run:
- - DL3toDL5.py
- - e.g. DL3toDL5.py -ObjectName Crab -DL3Path dl3 -ADir AnalysisDirectory  -LightCurveBinDuration 30 -FromDate 2001-01-01T00:00:00 -ToDate 2030-01-01T00:00:00 -LightCurveMinEnergy 0.35 -EnergyAxisMin 0.2 -EnergyAxisMax 10 -EnergyAxisBins 10
"""

########### Import Libraries ###########
######### Get Initial Arguments ########
import time
script_start_time = time.time()
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
from importer import *
from AddArguments import get_parser, CheckAllowedSpectralModelInputted
from WriteLogFile import (
    WritePackageVersionsToLog,
    WriteInputParametersToLog,
    WriteIntegralFluxToLog,
)
from SelectRuns import SelectRuns
from Diagnostics import (
    DiagnosticsTotalTimeStats,
    DiagnosticsDeadtimeDistribution,
    DiagnosticsPointingOffsetDistribution,
    DiagnosticsPeekAtIRFs,
    DiagnosticsPeekAtEvents,
    check_livetimes,
    SaveInfoTable,
    PlotOnOffEvents,
)
from EnergyAxes import EnergyAxes
from GetGeometry import (
    GetOnRegion,
    GetExclusionRegions,
    GetExclusionMask,
    GetOnRegionRadius,
)
from DataReduction import RunDataReductionChain
from SpectralVariabilityPlots import MakeSpectralVariabilityPlots
from LightCurve import MakeLightCurve
from Spectrum import SpectrumTimeBins

args = get_parser().parse_args()
CheckAllowedSpectralModelInputted(args)
cmd_line_args = " ".join(sys.argv)
########################################

############# Initial Steps #############
# Check if the Analysis Directory exists, if not create it
# Create a log file
# Write the packages used to the log file.
# Write the input parameters to the log file
os.makedirs(args.ADir, exist_ok=True)
os.makedirs(args.ADir + "/Diagnostics", exist_ok=True)
os.makedirs(args.ADir + "/Spectrum", exist_ok=True)
if args.LightCurve == True:
    os.makedirs(args.ADir + "/LightCurve", exist_ok=True)
if args.SpectralVariabilityTimeBinFile is not None:
    os.makedirs(args.ADir + "/SpectralVariability", exist_ok=True)
path_to_log = args.ADir + "/log.txt"
with open(path_to_log, "w") as f:
    f.write("Log file for DL3toDL5.py\n")
    f.write("Author: Nicki Bond\n")
    f.write("Date Run: " + str(datetime.now()) + "\n")
    f.write(f"Command line arguments: \n{cmd_line_args}\n")
    f.write("--------------------------------------------------\n")
WritePackageVersionsToLog(path_to_log)
WriteInputParametersToLog(path_to_log)
########################################

with open(path_to_log, "a") as f:
    f.write(
        f"Initial Steps Complete Time stamp: {((time.time() - script_start_time) / 60):.2f} minutes \n"
    )

############# Select Data #############
# Select data from the DL3Path directory
# Select data based on the run list, run exclude list, object name, and date range
# Select target position
obs_table, observations, target_position, obs_ids = SelectRuns(path_to_log, args)
########################################

with open(path_to_log, "a") as f:
    f.write(
        f"Select Data Complete Time stamp: {((time.time() - script_start_time) / 60):.2f} minutes \n"
    )

###### Initial Debugging Plots #######
DiagnosticsTotalTimeStats(path_to_log, obs_table, args)
DiagnosticsDeadtimeDistribution(path_to_log, obs_table, args)
DiagnosticsPointingOffsetDistribution(path_to_log, obs_table, args)
DiagnosticsPeekAtIRFs(path_to_log, observations, args)
DiagnosticsPeekAtEvents(path_to_log, observations, args)
########################################

with open(path_to_log, "a") as f:
    f.write(
        f"Initial Debugging Complete Time stamp: {((time.time() - script_start_time) / 60):.2f} minutes \n"
    )


########## Define Energy Axes  ##########
# Define energy axis
# Define true energy axis
energy_axis, energy_axis_true = EnergyAxes(args, path_to_log)
##########################################


########## Define Geometry #############
# Define the on region
# Define exclusion regions
on_region_radius = GetOnRegionRadius(args, path_to_log)
on_region, geom = GetOnRegion(
    target_position, args, energy_axis, path_to_log, on_region_radius
)
exclusion_regions = GetExclusionRegions(target_position, args, path_to_log)
exclusion_mask = GetExclusionMask(exclusion_regions, target_position, energy_axis)
##############################################

with open(path_to_log, "a") as f:
    f.write(
        f"Energy Axis and Define Geometry Complete Time stamp: {((time.time() - script_start_time) / 60):.2f} minutes \n"
    )

########### Data Reduction Chain: Significance and Spectrum ############
# Note this is done with whole dataset (i.e. before we remove areas with higher systematics)
fit_results_full_dataset, all_datasets = RunDataReductionChain(
    geom,
    energy_axis,
    energy_axis_true,
    exclusion_mask,
    observations,
    obs_ids,
    path_to_log,
    args,
    on_region_radius,
)
#########################################################

with open(path_to_log, "a") as f:
    f.write(
        f"Data Reduction Chain Complete Time stamp: {((time.time() - script_start_time) / 60):.2f} minutes \n"
    )

####### Check Livetimes between obs_table and info_table
check_livetimes(obs_table, all_datasets, observations, path_to_log)
###### Check info_table
info_table_not_cumulative = SaveInfoTable(all_datasets, args)
PlotOnOffEvents(info_table_not_cumulative, args, path_to_log)
########################################################

with open(path_to_log, "a") as f:
    f.write(
        f"Check Livetimes between obs_table and info_table Complete Time stamp: {((time.time() - script_start_time) / 60):.2f} minutes \n"
    )

# Run Data Reduction Chain for each time bin if specified
fit_results = []
if args.SpectralVariabilityTimeBinFile is not None:
    with open(path_to_log, "a") as f:
        f.write("--------------------------------------------------\n")
        time_bins = SpectrumTimeBins(args)
        for i, (tmin, tmax) in enumerate(time_bins):
            f.write(
                f"Running Data Reduction Chain for observations from {tmin} to {tmax}\n"
            )
            label = f"timebin_{i}"
            selected_obs = [
                obs
                for obs in observations
                if obs.tstart.mjd >= tmin and obs.tstart.mjd <= tmax
                # if an observation crosses the time bin edge we include it in first time bin (i.e. we look at tstart not tstop)
            ]
            selected_obs_ids = [obs.obs_id for obs in selected_obs]
            if len(selected_obs) == 0:
                with open(path_to_log, "a") as f:
                    f.write(
                        f"Skipping {label}: no observations in MJD range {tmin}-{tmax}\n"
                    )
                continue
            fit_result, dataset = RunDataReductionChain(
                geom,
                energy_axis,
                energy_axis_true,
                exclusion_mask,
                selected_obs,
                selected_obs_ids,
                path_to_log,
                args,
                on_region_radius,
                tmin=tmin,
                tmax=tmax,
            )[0]
            fit_results.append(fit_result)
    ######### Look for Spectral Variability ##########
    MakeSpectralVariabilityPlots(fit_results, time_bins, path_to_log, args)
    # flux_points_dataset, stacked, info_table, fit_result, datasets =MakeSpectrumFluxPoints(observations = observations, geom=geom, energy_axis=energy_axis, energy_axis_true=energy_axis_true, on_region=on_region, exclusion_mask=exclusion_mask, args = args, path_to_log=path_to_log)
    # PlotSpectrum(flux_points_dataset, args= args, path_to_log=path_to_log)

with open(path_to_log, "a") as f:
    f.write(
        f"Data Reduction Chain for Individual Time Bins Complete Time stamp: {((time.time() - script_start_time) / 60):.2f} minutes \n"
    )

######### Integral Flux ############
# Find integral flux for the source
# Find integral flux for the Crab
# Find what % Crab the source is
# Write these to log file
# Note that this is handled for both the case where there are multiple time bins and where there is only one time bin
WriteIntegralFluxToLog(fit_results_full_dataset, args, path_to_log)
if fit_results != []:
    for fit_result, (tmin, tmax) in zip(fit_results, time_bins):
        WriteIntegralFluxToLog(fit_result, args, path_to_log, tmin=tmin, tmax=tmax)
############################################

with open(path_to_log, "a") as f:
    f.write(
        f"Find Integral Flux Complete Time stamp: {((time.time() - script_start_time) / 60):.2f} minutes \n"
    )


######### Make Light Curve ############
# Need non-stacked Observations for Light Curve
# Make light curve
# Plot light curve
# Also plot LC with ED points if provided
if args.LightCurve == True:
    lc = MakeLightCurve(path_to_log=path_to_log, datasets=all_datasets, args=args)
##############################################

with open(path_to_log, "a") as f:
    f.write(
        f"Make Light Curve Complete Time stamp: {((time.time() - script_start_time) / 60):.2f} minutes \n"
    )


######### Write End of Log File ##########
with open(path_to_log, "a") as f:
    f.write("--------------------------------------------------\n")
    f.write(
        f"Script Runtime: {((time.time() - script_start_time) / 60):.2f} minutes \n"
    )
    f.write("--------------------------------------------------\n")
print("\nAnalysis complete. Log file written to: " + path_to_log + "\n")
print(f"Script Runtime: {((time.time() - script_start_time) / 60):.2f} minutes \n")
#################################################
