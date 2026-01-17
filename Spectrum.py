from importer import *


def SpectrumTimeBins(args):
    time_bins = []
    try:
        with open(args.SpectralVariabilityTimeBinFile, "r") as tbfile:
            for line in tbfile:
                line = line.split("#")[0].strip()
                if not line:  # skip empty/comment-only lines
                    continue
                parts = line.strip().split()
                if len(parts) == 2:
                    tmin, tmax = map(float, parts)
                    time_bins.append((tmin, tmax))
                else:
                    raise ValueError(f"Invalid line in time bin file: {line}")
    except Exception as e:
        print(f"Error reading time bin file: {e}")
        sys.exit(1)
    return time_bins
