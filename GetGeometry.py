from importer import *

def GetOnRegion(target_position, args, energy_axis, path_to_log):
    on_region = CircleSkyRegion(center=target_position, radius=args.OnRegionRadius * u.deg)
    with open(path_to_log, "a") as f:
        f.write("On Region: " + str(on_region) + "\n")
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
        StarTable = Table(names=("RA_ICRS_", "DE_ICRS_", "BTmag"))
        for row in result[0]["RA_ICRS_", "DE_ICRS_", "BTmag"]:
            if row["BTmag"] < 6:
                StarTable.add_row(row)
                f.write(str(row) + "\n")
        f.write("--------------------------------------------------\n")

    exclusion_regions = []
    exclusion_regions.append(
        CircleSkyRegion(
            center=SkyCoord(target_position.ra, target_position.dec, unit="deg", frame ='icrs'),
            radius=0.3 * u.deg,
        )
    )
    for Star in StarTable:
        target_position_star = SkyCoord(Star["RA_ICRS_"], Star["DE_ICRS_"], unit="deg").icrs
        exclusion_regions.append(
            CircleSkyRegion(
                center=SkyCoord(
                    target_position_star.ra, target_position_star.dec, unit="deg", frame='icrs'
                ),
                radius=0.1 * u.deg,
            )
        )
    return exclusion_regions

def GetExclusionMask(exclusion_regions, target_position, energy_axis):
    exclusion_mask_geom = WcsGeom.create(
        binsz=0.01,  # in degrees
        width = (4, 4),
        skydir=target_position,
        proj="CAR",
        frame ="icrs",
        axes = [energy_axis]
    )
    exclusion_mask = ~exclusion_mask_geom.to_image().to_cube([energy_axis.squash()]).region_mask(exclusion_regions)
    return exclusion_mask