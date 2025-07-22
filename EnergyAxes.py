from importer import *


def EnergyAxes(args, path_to_log):
    energy_axis = MapAxis.from_energy_bounds(
        args.EnergyAxisMin,
        args.EnergyAxisMax,
        nbin=args.EnergyAxisBins,
        unit="TeV",
        name="energy",
    )
    energy_axis_true = MapAxis.from_energy_bounds(
        0.5 * args.EnergyAxisMin,
        2 * args.EnergyAxisMax,
        nbin=2 * args.EnergyAxisBins,
        unit="TeV",
        name="energy_true",
    )
    with open(path_to_log, "a") as f:
        f.write("--------------------------------------------------\n")
        f.write("Energy Axis: " + str(energy_axis) + "\n")
        f.write("True Energy Axis: " + str(energy_axis_true) + "\n")
        f.write("Energy Axis Bin Edges: \n")
        f.write(str(energy_axis.edges) + "\n")
        f.write("--------------------------------------------------\n")
    return energy_axis, energy_axis_true
