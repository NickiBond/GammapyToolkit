from importer import *
"""
def LMS(n_on, n_off, alpha):
    #Calculate the Li & Ma significance https://www.mpe.mpg.de/~ste/data/aa0839.pdf (Eq4)
    #If using gammapy this should give same result as stats.WStatCountsStatistic(n_on=n_on, n_off=n_off, alpha=alpha).sqrt_ts
    S = np.sqrt(2) * (
        (n_on * np.log(((1 + alpha) * n_on) / (alpha * (n_on + n_off))))
        + n_off * np.log(((1 + alpha) * n_off) / (n_on + n_off))
    ) ** (1 / 2)
    return S
"""


"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate the Li & Ma significance.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--n_on", type=float, help="Number of on-source events.", required=True
    )
    parser.add_argument(
        "--n_off", type=float, help="Number of off-source events.", required=True
    )
    parser.add_argument(
        "--alpha",
        type=float,
        help="Ratio of the sizes of the on and off regions. ",
        required=True,
    )
    args = parser.parse_args()
    result = li_ma_significance(args.n_on, args.n_off, args.alpha)
    print(f"Li & Ma significance: {result:.2f}")
"""
