from importer import *

def MakeSpectralVariabilityPlots(fit_results, time_bins, path_to_log, args):
    MeanTimes = []
    Index = []
    IndexErr = []
    Norm = []
    NormErr = []
    with open(path_to_log, "a") as f:
        f.write("--------------------------------------------------\n")
        f.write("Spectral Variability: \n")
        f.write("Plots saved to: " + args.ADir + "/SpectralVariabilityNorm.pdf and " + args.ADir + "/SpectralVariabilityIndex.pdf\n")
        for (tmin, tmax), fit_result in zip(time_bins, fit_results):
            MeanTimes.append((tmax+tmin)/2)
            Index.append(fit_result.parameters["index"].value)
            IndexErr.append(fit_result.parameters["index"].error)
            Norm.append(fit_result.parameters["amplitude"].value)
            NormErr.append(fit_result.parameters["amplitude"].error)
        plt.figure()
        plt.errorbar(MeanTimes, Norm, yerr=NormErr, fmt="o", color="blue")
        plt.xlabel("Time (MJD)")
        plt.ylabel(r"Norm [TeV$^{-1}$ s$^{-1}$ cm$^{-2}$]")
        plt.savefig(args.ADir + f"/SpectralVariabilityNorm.pdf")
        plt.close()
        plt.figure()
        plt.errorbar(MeanTimes, Index, yerr=IndexErr, fmt="o", color="blue")
        plt.xlabel("Time (MJD)")
        plt.ylabel("Index")
        plt.savefig(args.ADir + f"/SpectralVariabilityIndex.pdf")
        plt.close()
        plt.figure()
        plt.errorbar(Index, Norm, xerr=IndexErr, yerr=NormErr, fmt="o", color="blue")
        plt.xlabel("Index")
        plt.ylabel(r"Norm [TeV$^{-1}$ s$^{-1}$ cm$^{-2}$]")
        plt.savefig(args.ADir + f"/SpectralVariabilityIndexNorm.pdf")
        plt.close()
        f.write("--------------------------------------------------\n")