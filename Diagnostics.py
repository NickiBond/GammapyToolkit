from importer import *


def DiagnosticsTotalTimeStats(path_to_log, obs_table, args):
    with open(path_to_log, "a") as f:
        f.write("Total Livetime: " + str(obs_table["LIVETIME"].sum() / 3600) + " hrs\n")
        f.write("Total Ontime: " + str(obs_table["ONTIME"].sum() / 3600) + " hrs\n")
        f.write(
            "Livetime/Ontime Ratio: "
            + str(obs_table["LIVETIME"].sum() / obs_table["ONTIME"].sum())
            + "\n"
        )
        f.write("--------------------------------------------------\n")

    return


def DiagnosticsDeadtimeDistribution(path_to_log, obs_table, args):
    with open(path_to_log, "a") as f:
        f.write("Making Deadtime distribution plot:\n")
        plt.hist(obs_table["DEADC"])
        plt.xlabel("Deadtime")
        plt.ylabel("Number of Observations")
        plt.title(f'obstable["DEADC"] Distribution')
        plt.savefig(args.ADir + "/DeadtimeDistribution.pdf")
        plt.close()
        f.write(
            "Deadtime Distribution saved to "
            + args.ADir
            + "/DeadtimeDistribution.pdf\n"
        )
    return


def DiagnosticsPointingOffsetDistribution(path_to_log, obs_table, args):
    with open(path_to_log, "a") as f:
        f.write("Making Pointing Offset distribution plot:\n")

        plt.hist(
            angular_separation(
                obs_table["RA_OBJ"],
                obs_table["DEC_OBJ"],
                obs_table["RA_PNT"],
                obs_table["DEC_PNT"],
            )
        )
        plt.xlabel(f"Angular Separation (deg)")
        plt.title(f"Pointing Offset Distribution")
        plt.ylabel("Number of Observations")
        plt.savefig(args.ADir + "/PointingOffsetHistogram.pdf")
        plt.close()
        f.write(
            "Pointing Offset Distribution saved to "
            + args.ADir
            + "/PointingOffsetHistogram.pdf\n"
        )
        f.write(
            "Mean Pointing Offset: "
            + str(
                np.mean(
                    angular_separation(
                        obs_table["RA_OBJ"],
                        obs_table["DEC_OBJ"],
                        obs_table["RA_PNT"],
                        obs_table["DEC_PNT"],
                    )
                )
            )
            + "\n"
        )
        f.write(
            "Standard Deviation Pointing Offset: "
            + str(
                np.std(
                    angular_separation(
                        obs_table["RA_OBJ"],
                        obs_table["DEC_OBJ"],
                        obs_table["RA_PNT"],
                        obs_table["DEC_PNT"],
                    )
                )
            )
            + "\n"
        )
        f.write("--------------------------------------------------\n")
    return

def DiagnosticsOnOffCounts(path_to_log, datasets, args):
    with open(path_to_log, "a") as f:
        f.write('Finding on and off counts per run')
        f.write('Saving on and off counts to'+ args.ADir+'/OnOffCounts')
        f.write("--------------------------------------------------\n")
    with open(args.ADir+'/OnOffCounts.csv', 'w') as f:
        for dataset in datasets:
            f.write(str(dataset.name) + ", " + str(dataset.counts.data.sum()) + ", " +  str(dataset.counts_off.data.sum())+','+ str(dataset.alpha.data[0,0,:][0])+'\n')   
    return 1


def DiagnosticsPlotOnOffCounts(path_to_on_off_counts, args):
    df = pd.read_csv(path_to_on_off_counts, header=None)
    file = df[0]
    on = df[1]
    off = df[2]
    plt.figure()
    plt.hist(on)    
    plt.xlabel("On counts per run")
    plt.savefig(args.ADir + '/OnCountsPerRunHistogram')
    plt.figure()
    plt.hist(off)    
    plt.xlabel("Off counts per run")
    plt.savefig(args.ADir + '/OffCountsPerRunHistogram')