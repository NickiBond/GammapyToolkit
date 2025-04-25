from importer import *


def EnergyAxes(args):
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
    return energy_axis, energy_axis_true
