from importer import *


def SelectRuns(path_to_log, args):
    f = open(path_to_log, "a")
    data_store = DataStore.from_dir(f"{args.DL3Path}")
    # Write the data store info to the log file
    # Capture stdout into a string buffer
    buf = io.StringIO()
    with redirect_stdout(buf):
        data_store.info()   
    # Write the captured output to the log file
    f.write(buf.getvalue() + "\n")
    f.write("Data Selection:\n")
    obs_table = data_store.obs_table
    obs_table.sort('OBS_ID')
    f.write(f"Initial length of obs table: {len(obs_table)} \n")
    # Exclude runs that are not in the run list if run list is provided
    if args.RunList == None:
        f.write("No Run List given. All observations kept.\n")
    else:
        run_list = np.loadtxt(args.RunList, dtype=int)
        mask = np.isin(obs_table["OBS_ID"], run_list)
        obs_table = obs_table[mask]
        f.write(
            f"Run List given. Length of obs table after selection: {len(obs_table)} \n"
        )

    # Exclude runs in the run exclude list
    if args.RunExcludeList == None:
        f.write("No Runs to Exclude given. All observations kept.\n")
    else:
        runs_exclude_list = np.loadtxt(args.RunExcludeList, dtype=int)
        mask = np.isin(obs_table["OBS_ID"], runs_exclude_list)
        obs_table = obs_table[~mask]
        f.write(
            "Runs to Exclude given. Length of obs table after selection: "
            + str(len(obs_table))
            + "\n"
        )
    #  Only accept runs with a certain object name
    if args.ObjectName != None:
        mask = obs_table["OBJECT"] == args.ObjectName
        obs_table = obs_table[mask]
        f.write(
            "Only observations with OBJECT name "
            + args.ObjectName
            + " kept. Length of obs table after selection: "
            + str(len(obs_table))
            + "\n"
        )

    #  Only accept runs after a certain date
    if args.FromDate != None:
        FromDate = Time(args.FromDate).mjd
        mask = Time(obs_table["DATE-OBS"]).mjd >= FromDate
        obs_table = obs_table[mask]
        f.write(
            "Only observations after "
            + args.FromDate
            + " kept. Length of obs table after selection: "
            + str(len(obs_table))
            + "\n"
        )

    #  Only accept runs before a certain date
    if args.ToDate != None:
        ToDate = Time(args.ToDate).mjd
        mask = Time(obs_table["DATE-OBS"]).mjd <= ToDate
        obs_table = obs_table[mask]
        f.write(
            "Only observations before "
            + args.ToDate
            + " kept. Length of obs table after selection: "
            + str(len(obs_table))
            + "\n"
        )

    observations = data_store.get_observations(
        obs_table["OBS_ID"], required_irf="point-like"
    )
    f.write("--------------------------------------------------\n")
    f.write("Observations kept: \n" + str(np.array(obs_table["OBS_ID"])) + "\n")
    f.write("--------------------------------------------------\n")
    f.close()
    return obs_table, observations
