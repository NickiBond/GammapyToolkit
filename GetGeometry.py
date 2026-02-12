from importer import *

from astropy.io import fits
import astropy.units as u
from regions import CircleSkyRegion
from gammapy.maps import RegionGeom
from astropy.coordinates import SkyCoord
from astropy.table import Table


def GetOnRegionRadius(args, path_to_log):
    radius = None
    # Try reading RAD_MAX from IRF in header of first fits file (alphabetically)
    try:
        files = sorted(os.listdir(args.DL3Path))
        fits_files = [f for f in files if f.lower().endswith(".fits")]
        if not fits_files:
            raise FileNotFoundError("No FITS files found in the given path.")
        first_file = os.path.join(args.DL3Path, fits_files[0])
        with fits.open(first_file) as hdul:
            if "EFFECTIVE AREA" in hdul and "RAD_MAX" in hdul["EFFECTIVE AREA"].header:
                radius = hdul["EFFECTIVE AREA"].header["RAD_MAX"] * u.deg
                with open(path_to_log, "a") as f:
                    f.write(
                        f"Using IRF-defined RAD_MAX = {radius.value} deg for On Region\n"
                    )
    except Exception as irf_error:
        print(f"[WARNING] Could not read RAD_MAX from IRF: {irf_error}")
        with open(path_to_log, "a") as f:
            f.write(f"WARNING: Could not read RAD_MAX from IRF: {irf_error}\n")

    if args.OnRegionRadius is not None:
        radius = args.OnRegionRadius * u.deg
        print(f"Using user-defined OnRegionRadius = {radius.value} deg")

    if radius is None:
        print("[ERROR] No valid radius found (neither IRF nor user-defined). Exiting.")
        sys.exit(1)
    return radius


def GetOnRegion(target_position, args, energy_axis, path_to_log, on_region_radius):
    # Build region
    on_region = CircleSkyRegion(center=target_position, radius=on_region_radius)
    # Log
    with open(path_to_log, "a") as f:
        f.write(f"On Region: {on_region}\n")
    geom = RegionGeom.create(region=on_region, axes=[energy_axis])
    return on_region, geom


def GetExclusionRegions(target_position, args, path_to_log):
    vizier = Vizier(catalog="Tycho2")
    vizier.ROW_LIMIT = 100000
    vizier.COL_LIMIT = -1
    result = vizier.query_region(args.ObjectName, radius=4 * u.deg)
    with open(path_to_log, "a") as f:
        f.write("Stars to be excluded based on VEGAS' definition of a bright star:\n")
        f.write(" - Using Tycho2 catalog\n")
        f.write(" - Bright stars are defined as those with BTmag < 6\n")
        f.write(" - Stars are excluded if they are within 4 degrees of the target\n")
        f.write(" - A 0.1 degree exclusion region is used for the stars\n")
        f.write(" - A 0.3 degree exclusion region is used for the target\n")
        f.write("\n Bright Stars That Are Excluded: \n")
        StarTable = Table(
            names=("RA(ICRS)", "DE(ICRS)", "BTmag", "TYC1", "TYC2", "TYC3", "HIP")
        )
        for row in result[0][
            ["RA(ICRS)", "DE(ICRS)", "BTmag", "TYC1", "TYC2", "TYC3", "HIP"]
        ]:
            if row["BTmag"] < 6:
                StarTable.add_row(row)
                f.write(str(row) + "\n")
        f.write("--------------------------------------------------\n")

    # exclusion region at source
    exclusion_regions = []
    exclusion_regions.append(
        CircleSkyRegion(
            center=SkyCoord(
                target_position.ra, target_position.dec, unit="deg", frame="icrs"
            ),
            radius=0.3 * u.deg,
        )
    )

    # exclusion regions for bright stars
    for Star in StarTable:
        target_position_star = SkyCoord(
            Star["RA(ICRS)"], Star["DE(ICRS)"], unit="deg"
        ).icrs
        exclusion_regions.append(
            CircleSkyRegion(
                center=SkyCoord(
                    target_position_star.ra,
                    target_position_star.dec,
                    unit="deg",
                    frame="icrs",
                ),
                radius=0.1 * u.deg,
            )
        )

    # User supplies exclusion regions.
    if args.exclusion_csv is not None:
        user_regions, _ = read_exclusion_csv(args.exclusion_csv)
        exclusion_regions.extend(user_regions)

        with open(path_to_log, "a") as f:
            f.write(f"Added {len(user_regions)} user-defined exclusion regions\n")

    return exclusion_regions


def GetExclusionMask(exclusion_regions, target_position, energy_axis):
    exclusion_mask_geom = WcsGeom.create(
        binsz=0.01,  # in degrees
        width=(6, 6),
        skydir=target_position,
        proj="CAR",
        frame="icrs",
        axes=[energy_axis],
    )
    exclusion_mask = (
        ~exclusion_mask_geom.to_image()
        .to_cube([energy_axis.squash()])
        .region_mask(exclusion_regions)
    )
    return exclusion_mask


def read_exclusion_csv(csv_path):
    """
    Read csv of exclusion regions.
    Return list of CircleSkyRegion objects.

    Expected columns:
      - ra  (deg, ICRS)
      - dec (deg, ICRS)
      - radius (deg by default, or astropy unit string)
      - name (if region is to be labelled in On/Off/Exclusion regions plot, or nothing if not)
    """
    table = Table.read(
        csv_path,
        format="csv",
        names=("ra", "dec", "radius", "name"),
    )
    regions = []

    for row in table:
        # get RA and DEC
        coord = SkyCoord(
            ra=row["ra"] * u.deg,
            dec=row["dec"] * u.deg,
            frame="icrs",
        )

        # get radius
        radius_val = row["radius"]

        if isinstance(radius_val, str):
            # e.g. "5 arcmin"
            radius = u.Quantity(radius_val)
        else:
            # e.g. 0.2 → assume degrees
            radius = radius_val * u.deg

        regions.append(CircleSkyRegion(center=coord, radius=radius))

    return regions, table
