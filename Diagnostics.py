from importer import *


def DiagnosticsTotalTimeStats(path_to_log, obs_table, args):
    with open(path_to_log, "a") as f:
        f.write(f"Total Livetime: {obs_table['LIVETIME'].sum()} s \n")
        f.write(f"Total Ontime: {obs_table['ONTIME'].sum()} s \n")
        f.write(
            f"Livetime/Ontime Ratio: {obs_table['LIVETIME'].sum() / obs_table['ONTIME'].sum():.6f}\n"
        )
        f.write("--------------------------------------------------\n")

    return


def DiagnosticsDeadtimeDistribution(path_to_log, obs_table, args):
    with open(path_to_log, "a") as f:
        f.write("Making Deadtime distribution plot:\n")
        plt.hist(1 - obs_table["DEADC"])
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
    with open(args.ADir + "/Diagnostics/DeadtimeStats.txt", "w") as f:
        f.write("Deadtime Statistics:\n")
        f.write(f"Run Number, On Time (s), Livetime (s), Deadtime Fraction\n")
        for i, row in enumerate(obs_table):
            f.write(
                f"{row['OBS_ID']}, {row['ONTIME']:.4f}, {row['LIVETIME']:.4f}, {1 - row['DEADC']:.4f}\n"
            )
        f.write("--------------------------------------------------\n")
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
    with open(args.ADir + "/Diagnostics/PointingOffsetStats.txt", "w") as f:
        f.write("Pointing Offset Statistics:\n")
        f.write(f"Run Number, RA_OBJ, DEC_OBJ, RA_PNT, DEC_PNT, Angular Separation\n")
        for i, row in enumerate(obs_table):
            f.write(
                f"{row['OBS_ID']}, {row['RA_OBJ']}, {row['DEC_OBJ']}, {row['RA_PNT']}, {row['DEC_PNT']}, "
                f"{angular_separation(row['RA_OBJ'], row['DEC_OBJ'], row['RA_PNT'], row['DEC_PNT'])}\n"
            )
    return


def DiagnosticsPeekAtIRFs(path_to_log, observations, args):
    irf_dir = os.path.join(args.ADir, "Diagnostics", "IRF_Plots")
    os.makedirs(irf_dir, exist_ok=True)
    # Generate and save IRF plots
    with open(path_to_log, "a") as f:
        f.write(
            "Peek at IRFs for first 10 observations (or all observations if less than 10):\n"
        )
        for i, obs in enumerate(observations):
            if (
                i < 10 or args.Debug
            ):  # Limit to 10 datasets for plotting to save time unless Debug is set to True
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
        f.write(
            "Peek at Events for first 10 observations (or all observations if less than 10):\n"
        )
        for i, obs in enumerate(observations):
            if (
                i < 10 or args.Debug
            ):  # Limit to 10 datasets for plotting to save time unless Debug is set to True
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


def check_livetimes(obs_table, all_datasets, observations, path_to_log):
    obs_table_livetime_sum = 0
    info_table_livetime_sum = 0
    with open(path_to_log, "a") as f:
        f.write("--------------------------------------------------\n")
        f.write("Diagnostics: Check Livetime matches in obs_table and info_table\n")
    for i in range(len(observations)):
        obs_table_livetime = obs_table["LIVETIME"][i]
        obs_table_livetime_sum += obs_table_livetime
        info_table_livetime = all_datasets.info_table(cumulative=False)["livetime"][i]
        info_table_livetime_sum += info_table_livetime
        if (
            obs_table_livetime / info_table_livetime < 0.99
            or obs_table_livetime / info_table_livetime > 1.01
        ):
            print(
                f"WARNING!: Run: {observations[i].obs_id}: obs_table livetime: {obs_table_livetime} info_table livetime: {info_table_livetime}"
            )
            print(
                f"WARNING! obs_table livetime / info_table livetime: {obs_table_livetime/info_table_livetime:.2f}"
            )
            with open(path_to_log, "a") as f:
                f.write(
                    f"WARNING!: Run: {observations[i].obs_id}: obs_table livetime: {obs_table_livetime} info_table livetime: {info_table_livetime}\n"
                )
                f.write(
                    f"WARNING! obs_table livetime / info_table livetime: {obs_table_livetime/info_table_livetime:.2f}\n"
                )
    with open(path_to_log, "a") as f:
        f.write("--------------------------------------------------\n")
        f.write(f"Total Livetime from obs_table: {obs_table_livetime_sum}\n")
        f.write(f"Total Livetime from info_table: {info_table_livetime_sum}\n")
        f.write(
            f"Difference: {abs(obs_table_livetime_sum - info_table_livetime_sum)}\n"
        )
        if abs(obs_table_livetime_sum - info_table_livetime_sum) > 1:
            f.write(
                "WARNING! Total livetime from obs_table and info_table do not match!\n"
            )


def SaveInfoTable(datasets, args):
    info_table = datasets.info_table(cumulative=False)
    info_table.write(
        os.path.join(args.ADir, "Diagnostics/InfoTable.ecsv"), overwrite=True
    )
    return info_table


def PlotOnOffEvents(info_table_not_cumulative, args, path_to_log):
    on = info_table_not_cumulative["counts"]
    off = info_table_not_cumulative["counts_off"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 10))
    axes[0].hist(on.value, label="On")
    axes[1].hist(off.value, label="Off")
    axes[0].set_xlabel("On Events")
    axes[1].set_xlabel("Off Events")
    axes[0].set_ylabel("Counts")
    axes[1].set_ylabel("Counts")
    axes[0].set_title("On Counts")
    axes[1].set_title("Off Counts")
    axes[0].legend()
    plt.tight_layout()
    plt.savefig(os.path.join(args.ADir, "Diagnostics/OnOffCounts.pdf"))
    with open(path_to_log, "a") as f:
        f.write("Saved On/Off Counts figure to Diagnostics/OnOffCounts.pdf\n")
    plt.close(fig)

    plt.figure(figsize=(8, 6))
    plt.scatter(on.value, off.value, color="purple")
    plt.xlabel("On Counts")
    plt.ylabel("Off Counts")
    plt.title("On/Off Counts Scatter Plot")
    plt.savefig(os.path.join(args.ADir, "Diagnostics/OnOffCounts_Scatter.pdf"))
    with open(path_to_log, "a") as f:
        f.write(
            "Saved On/Off Counts Scatter figure to Diagnostics/OnOffCounts_Scatter.pdf\n"
        )
    plt.close()
