#!/usr/bin/env python3
import os
import argparse
import numpy as np
from astropy.io import fits


def compare_fits_files(file1, file2, filelength):
    """
    This was written to be a subfunction of compare_fits_folders.
    It was not intended to be used on its own.
    See ``help(compare_fits_folders)`` for more details

    Example Code:

    if compare_fits_files(file1, file2, 0):
       print("FITS files are identical. (Up to hdul[i] anyway)")
               else:
        print("The FITS files are not identical.")
    """
    # Open the two FITS files
    with fits.open(file1) as hdul1, fits.open(file2) as hdul2:
        for i in range(0, filelength + 1, 1):
            # Compare the headers
            if hdul1[i].header != hdul2[i].header:
                print(f"Headers of {file1} and {file2} are different.")
                print(hdul1[i].header)
                print(hdul2[i].header)
                return False
            # Compare the image data
            # Changed this to [0,1,2, 3, 4] because that's where the numbers are
            data1 = hdul1[i].data
            data2 = hdul2[i].data

            # Check if the shape and data are identical
            if not np.array_equal(data1, data2):
                print(f"Data of {file1} and {file2} are different.")
                return False
    return True


def compare_fits_folders(folder1, folder2, filelength):
    """
    Returns TRUE if Identical and FALSE if any differences are found.
    If a difference is found it will detail what the difference was.
    Insert filenames as path e.g. "/Users/nickibond/Downloads/89884_s5_geo_itm_med.fits"
    Insert filelength. Filelength indexes hdul[i].
    As a basic test use 0. If it returns False for 0 the folders are not identical.
    HOWEVER, if it returns true for this basic test, the files may not be identical.
    i.e. if hdul[2] did not match for example.

    Example Code:

    if compare_fits_folders(folder1, folder2, 0):
       print("FITS files are identical. (Up to hdul[i] anyway)")
    else:
        print("The FITS files are not identical.")

    """

    # Get lists of all FITS files in the folders
    files1 = [f for f in os.listdir(folder1) if f.endswith(".fits")]
    files2 = [f for f in os.listdir(folder2) if f.endswith(".fits")]

    # If the number of FITS files is different, they cannot be identical
    if len(files1) != len(files2):
        print(
            f"The folders have a different number of FITS files. \n"
            f"{folder1} has {len(files1)} files. \n"
            f"{folder2} has {len(files2)} files. \n"
        )
        return False

    # Sort files to ensure correct pairing
    files1.sort()
    files2.sort()

    # Compare each pair of files
    for file1, file2 in zip(files1, files2):
        file1_path = os.path.join(folder1, file1)
        file2_path = os.path.join(folder2, file2)

        if not compare_fits_files(file1_path, file2_path, filelength):
            return False

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare two folders of FITS files.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--f1", type=str, help="Path to the first folder containing FITS files."
    )
    parser.add_argument(
        "--f2", type=str, help="Path to the second folder containing FITS files."
    )
    parser.add_argument(
        "--l",
        default=0,
        type=int,
        help="Length of the fits file to compare. (hdul[i]), default = 0",
    )
    args = parser.parse_args()
    compare_fits_folders(args.f1, args.f2, args.l)
