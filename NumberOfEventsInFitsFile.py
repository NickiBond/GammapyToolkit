from astropy.io import fits


def NumberOfEventsInAFitsFile(file):
    """
    Input the path to a fits file.
    Outputs the hdul[1].header

    Example usage:

    folder_path = "/Users/nickibond/Documents/M87/dl3/"
    NumberOfEventsInFileList=[]
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        NumberOfEventsInFileList.append(NumberOfEventsInADL3File(file_path))
    plt.hist(NumberOfEventsInFileList)
    plt.xlabel("Number Of Events in DL3 File")

    Note this usage has a known issue of also looking at `hdu-index.fits` and `obs-index.fits`
    """
    hdul = fits.open(file)
    NumberOfEvents = hdul[1].header["NAXIS2"]
    hdul.close()
    return NumberOfEvents
