from importer import *


def DiagnosticsTotalTimeStats(path_to_log, obs_table, args):
    with open(path_to_log, "a") as f:
        f.write(f"Total Livetime: {obs_table['LIVETIME'].sum() / 3600:.2f} hrs\n")
        f.write(f"Total Ontime: {obs_table['ONTIME'].sum() / 3600:.2f} hrs\n")
        f.write(
            f"Livetime/Ontime Ratio: {obs_table['LIVETIME'].sum() / obs_table['ONTIME'].sum():.2f}\n"
        )
        f.write("--------------------------------------------------\n")

    return


def DiagnosticsDeadtimeDistribution(path_to_log, obs_table, args):
    with open(path_to_log, "a") as f:
        f.write("Making Deadtime distribution plot:\n")
        plt.hist(1-obs_table["DEADC"])
        plt.xlabel("Deadtime")
        plt.ylabel("Number of Observations")
        plt.title(f'1 - obstable["DEADC"] Distribution')
        plt.savefig(args.ADir + "/Diagnostics/DeadtimeDistribution.pdf")
        plt.close()
        f.write(
            "Deadtime Distribution saved to "
            + args.ADir
            + "/Diagnostics/DeadtimeDistribution.pdf\n"
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
        plt.savefig(args.ADir + "/Diagnostics/PointingOffsetHistogram.pdf")
        plt.close()
        f.write(
            "Pointing Offset Distribution saved to "
            + args.ADir
            + "/Diagnostics/PointingOffsetHistogram.pdf\n"
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


def DiagnosticsPeekAtIRFs(path_to_log, observations, args):
    irf_dir = os.path.join(args.ADir, "Diagnostics", "IRF_Plots")
    os.makedirs(irf_dir, exist_ok=True)
    # Generate and save IRF plots
    with open(path_to_log, "a") as f:
        f.write("Peek at IRFs for first 10 observations (or all observations if less than 10):\n")
        for i, obs in enumerate(observations):
            if i < 10 or args.Debug:  # Limit to 10 datasets for plotting to save time unless Debug is set to True
                obs.peek(figsize=(25, 5))
                fig = plt.gcf()  # Get the current figure
                obs_id = obs.obs_id
                filename = f"irf_obs_{obs_id}.png"
                filepath = os.path.join(irf_dir, filename)
                fig.savefig(filepath, bbox_inches="tight")
                f.write(f"Saved IRF figure for Obs ID {obs_id} to {filepath}\n")
                plt.close(fig)

def DiagnosticsPeekAtEvents(path_to_log, observations, args):
    event_dir = os.path.join(args.ADir, "Diagnostics/Event_Plots")
    os.makedirs(event_dir, exist_ok=True)
    # Generate and save event plots
    with open(path_to_log, "a") as f:
        f.write("--------------------------------------------------\n")
        f.write("Peek at Events for first 10 observations (or all observations if less than 10):\n")
        for i, obs in enumerate(observations):
            if i < 10 or args.Debug:  # Limit to 10 datasets for plotting to save time unless Debug is set to True
                obs.events.peek()
                fig = plt.gcf()  # Get the current figure
                obs_id = obs.obs_id
                filename = f"event_obs_{obs_id}.png"
                filepath = os.path.join(event_dir, filename)
                fig.savefig(filepath, bbox_inches="tight")
                f.write(f"Saved Event figure for Obs ID {obs_id} to {filepath}\n")
                plt.close(fig)
                i += 1
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
    plt.savefig(args.ADir + "/Diagnostics/OnCountsPerRunHistogram.pdf")
    plt.figure()
    plt.hist(off)    
    plt.xlabel("Off counts per run")
    plt.savefig(args.ADir + "/Diagnostics/OffCountsPerRunHistogram.pdf")