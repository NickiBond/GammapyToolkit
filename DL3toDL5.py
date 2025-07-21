#!/usr/bin/env python3
"""
Author: Nicki Bond
Date: 2025-Jan
Purpose:
- This script will take the VEGAS DL3 data files and convert them to DL5 data products.
- It takes a set of DL3 files and makes an energy spectrum using Gammapy.
- It also can plot the VEGAS spectrum on the same plot if a VEGAS Stage 6 log file is provided.
- It can also make a light curve. There are options for the user to change the parameters of gammapy's LightCurveEstimator.

Scope:
- This script only works on point sources.

To Run:
- Activate the environment:
- - source ~/NBvenv/bin/activate
- Run:
- - python DL3toDL5.py
- - e.g. python DL3toDL5.py -ObjectName M87 -DL3Path dl3 -ADir TestDirectory  -LightCurveBinDuration 30 -FromDate 2013-01-01T00:00:00 -ToDate 2023-01-01T00:00:00 -LightCurveMinEnergy 0.35 -EnergyAxisMin 0.2 -EnergyAxisMax 53.87787799835198 -EnergyAxisBins 30


"""

########### Import Libraries ###########
######### Get Initial Arguments ########
import time

script_start_time = time.time()
import sys

sys.path.append("/Users/nickibond/Documents/Research/Toolkit")
from importer import *
from AddArguments import get_parser
from WriteLogFile import WritePackageVersionsToLog, WriteInputParametersToLog, WriteIntegralFluxToLog
from SelectRuns import SelectRuns
from Diagnostics import (
    DiagnosticsTotalTimeStats,
    DiagnosticsDeadtimeDistribution,
    DiagnosticsPointingOffsetDistribution,
    DiagnosticsPeekAtIRFs,
    DiagnosticsPeekAtEvents,
)
from EnergyAxes import EnergyAxes
from GetGeometry import GetOnRegion, GetExclusionRegions, GetExclusionMask
from DataReduction import RunDataReductionChain
from SpectralVariabilityPlots import MakeSpectralVariabilityPlots
from LightCurve import MakeLightCurve, PlotLightCurve

args = get_parser().parse_args()
cmd_line_args = ' '.join(sys.argv)
########################################


############# Initial Steps #############
# Check if the Analysis Directory exists, if not create it
# Create a log file
# Write the packages used to the log file.
# Write the input parameters to the log file
os.makedirs(args.ADir, exist_ok=True)
os.makedirs(args.ADir + "/Diagnostics", exist_ok=True)
os.makedirs(args.ADir + "/Spectrum", exist_ok=True)
os.makedirs(args.ADir + "/LightCurve", exist_ok=True)
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


############# Select Data #############
# Select data from the DL3Path directory
# Select data based on the run list, run exclude list, object name, and date range
# Select target position
obs_table, observations, target_position, obs_ids = SelectRuns(path_to_log, args)
########################################


###### Initial Debugging Plots #######
DiagnosticsTotalTimeStats(path_to_log, obs_table, args)
DiagnosticsDeadtimeDistribution(path_to_log, obs_table, args)
DiagnosticsPointingOffsetDistribution(path_to_log, obs_table, args)
DiagnosticsPeekAtIRFs(path_to_log, observations, args)
DiagnosticsPeekAtEvents(path_to_log, observations, args)
########################################


########## Define Energy Axes  ##########
# Define energy axis
# Define true energy axis
energy_axis, energy_axis_true = EnergyAxes(args)
with open(path_to_log, "a") as f:
    f.write("--------------------------------------------------\n")
    f.write("Energy Axis: " + str(energy_axis) + "\n")
    f.write("True Energy Axis: " + str(energy_axis_true) + "\n")
    f.write("Energy Axis Bin Edges: \n")
    f.write(str(energy_axis.edges) + "\n")
    f.write("--------------------------------------------------\n")
##########################################


########## Define Geometry #############
# Define the on region
# Define exclusion regions
on_region, geom = GetOnRegion(target_position, args, energy_axis, path_to_log)
exclusion_regions = GetExclusionRegions(target_position, args, path_to_log)
exclusion_mask = GetExclusionMask(exclusion_regions, target_position, energy_axis)
##############################################

########### Data Reduction Chain: Significance and Spectrum ############
# Note this is done with whole dataset (i.e. before we remove areas with higher systematics)
fit_result, datasets = RunDataReductionChain(geom, energy_axis, energy_axis_true, exclusion_mask, observations, obs_ids, path_to_log, args)

# Run Data Reduction Chain for each time bin if specified
fit_results = []
if args.SpectralVariabilityTimeBinFile is not None:   
    time_bins = SpectrumTimeBins(args)
    for i, (tmin, tmax) in enumerate(time_bins):
        with open(path_to_log, "a") as f:
            f.write(f"Making SED for observations from {tmin} to {tmax}\n")
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
                f.write(f"Skipping {label}: no observations in MJD range {tmin}-{tmax}\n")
            continue
        fit_result = RunDataReductionChain(geom, energy_axis, energy_axis_true, exclusion_mask, selected_obs, selected_obs_ids, path_to_log, args, tmin=tmin, tmax=tmax)[0]
        fit_results.append(fit_result)
    ######### Look for Spectral Variability ##########
    MakeSpectralVariabilityPlots(fit_results, time_bins, path_to_log, args)
    # flux_points_dataset, stacked, info_table, fit_result, datasets =MakeSpectrumFluxPoints(observations = observations, geom=geom, energy_axis=energy_axis, energy_axis_true=energy_axis_true, on_region=on_region, exclusion_mask=exclusion_mask, args = args, path_to_log=path_to_log)
    # PlotSpectrum(flux_points_dataset, args= args, path_to_log=path_to_log)
    # DiagnosticsOnOffCounts(path_to_log, datasets, args)
    # DiagnosticsPlotOnOffCounts(path_to_on_off_counts = args.ADir+'/OnOffCounts.csv', args=args)
"""
fit_results = []
stackeds = []
if args.SpectralVariabilityTimeBinFile is not None:   
    time_bins = SpectrumTimeBins(args)
    for i, (tmin, tmax) in enumerate(time_bins):
        with open(path_to_log, "a") as f:
            f.write(f"Making SED for observations from {tmin} to {tmax}\n")
        label = f"timebin_{i}"
        selected_obs = [
            obs
            for obs in observations
            if obs.tstart.mjd >= tmin and obs.tstop.mjd <= tmax
        ]
        if len(selected_obs) == 0:
            with open(path_to_log, "a") as f:
                f.write(f"Skipping {label}: no observations in MJD range {tmin}-{tmax}\n")
            continue
        flux_points_dataset, stacked, info_table, fit_result, datasets = MakeSpectrumFluxPoints(observations = selected_obs, tmin=tmin, tmax=tmax, geom=geom, energy_axis = energy_axis, energy_axis_true=energy_axis_true, on_region=on_region, exclusion_mask=exclusion_mask, args= args, path_to_log=path_to_log)
        PlotSpectrum(flux_points_dataset, path_to_log= path_to_log, tmin=tmin, tmax=tmax, args=args)
        fit_results.append(fit_result)
        stackeds.append(stacked)
else:
    flux_points_dataset, stacked, info_table, fit_result, datasets =MakeSpectrumFluxPoints(observations = observations, geom=geom, energy_axis=energy_axis, energy_axis_true=energy_axis_true, on_region=on_region, exclusion_mask=exclusion_mask, args = args, path_to_log=path_to_log)
    PlotSpectrum(flux_points_dataset, args= args, path_to_log=path_to_log)
    DiagnosticsOnOffCounts(path_to_log, datasets, args)
    DiagnosticsPlotOnOffCounts(path_to_on_off_counts = args.ADir+'/OnOffCounts.csv', args=args)
"""
##########################################


######### Integral Flux ############
# Find integral flux for the source
# Find integral flux for the Crab
# Find what % Crab the source is
# Write these to log file
# Note that this is handled for both the case where there are multiple time bins and where there is only one time bin
WriteIntegralFluxToLog(fit_result, args, path_to_log)
if fit_results != []:
    for fit_result, (tmin,tmax) in zip(fit_results, time_bins):
        WriteIntegralFluxToLog(fit_result, args, path_to_log, tmin=tmin, tmax=tmax)
############################################


######### Make Light Curve ############
# Need non-stacked Observations for Light Curve
# Make light curve
# Plot light curve
# Also plot LC with ED points if provided
if args.LightCurve == True:
    lc = MakeLightCurve(path_to_log=path_to_log, datasets=datasets, args=args)
    #PlotLightCurve(lc, path_to_log=path_to_log, args=args)
##############################################


######### Write End of Log File ##########
with open(path_to_log, "a") as f:
    f.write("--------------------------------------------------\n")
    f.write(f"Script Runtime: {((time.time() - script_start_time) / 60):.2f} minutes \n")
    f.write("--------------------------------------------------\n")
#################################################