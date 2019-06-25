#!/usr/bin/env python
""" Generates GLANCE project grids
"""
from pathlib import Path
import subprocess
import warnings

import click
import fiona
import geopandas as gpd
import rasterio
from rasterio.crs import CRS
from rasterio.warp import transform_bounds, transform
from shapely.geometry import shape
from shapely.strtree import STRtree
import yaml


#: str: Version of grid
VERSION = 'V01'


#: str: Template WKT string for Lambert's Azimuthal Equal Area
WKT_LAEA_TEMPLATE = """
PROJCS["BU MEaSUREs Lambert Azimuthal Equal Area - {continent} - {version}",
    GEOGCS["GCS_WGS_1984",
        DATUM["D_WGS_1984",
            SPHEROID["WGS_1984",6378137.0,298.257223563]],
        PRIMEM["Greenwich",0.0],
        UNIT["degree",0.0174532925199433]],
    PROJECTION["Lambert_Azimuthal_Equal_Area"],
    PARAMETER["false_easting",0.0],
    PARAMETER["false_northing",0.0],
    PARAMETER["longitude_of_center",{lon_of_center}],
    PARAMETER["latitude_of_center",{lat_of_center}],
    UNIT["meter",1.0]]
"""


#: dict: Project parameters for Lambert's Azimuthal Equal Area for each
#        continent
PROJ_PARAMS_STEINWAND = {
    'AF': {
        'lat_of_center': 5,
        'lon_of_center': 20,
    },
    'AN': {
        'lat_of_center': -90,
        'lon_of_center': 0,
    },
    'AS': {
        'lat_of_center': 45,
        'lon_of_center': 100,
    },
    'EU': {
        'lat_of_center': 55,
        'lon_of_center': 20,
    },
    'OC': {
        'lat_of_center': -15,
        'lon_of_center': 135,
    },
    'NA': {
        'lat_of_center': 50,
        'lon_of_center': -100,
    },
    'SA': {
        'lat_of_center': -15,
        'lon_of_center': -60,
    },
}
CONTINENTS = list(PROJ_PARAMS_STEINWAND.keys())


#: dict[str, str]: Continent to continent's projection as WKT
GLANCE_GRID_CRS_WKT = {
    continent: WKT_LAEA_TEMPLATE.format(continent=continent,
                                        version=VERSION,
                                        **params)
    for continent, params in PROJ_PARAMS_STEINWAND.items()
}


#: dict[str, tuple[float, float]]: Upper left points of each grid
GLANCE_GRIDS_UL_XY = {
    'AF': (-5312270.00, 3707205.0),
    'AN': (-3662210.00, 5169375.0),
    'AS': (-4805840.00, 5190735.0),
    'EU': (-5505560.00, 3346245.0),
    'OC': (-6961010.00, 4078425.0),
    'NA': (-7633670.00, 5076465.0),
    'SA': (-6918770.00, 4899705.0),
}


#: dict[str, list]: Range of vertical (rows) and horizonal (column) tiles
GLANCE_GRIDS_LIMITS = {
    'AF': [(0, 60), (0, 74)],
    'AN': [(0, 56), (0, 62)],
    'AS': [(0, 66), (0, 77)],
    'EU': [(0, 38), (0, 54)],
    'OC': [(0, 78), (0, 113)],
    'NA': [(0, 64), (0, 84)],
    'SA': [(0, 68), (0, 74)]
}

#: dict[str, str]: Name of grids
GLANCE_GRIDS_NAME = {
    continent: f'BU MeaSUREs GLANCE Grids {VERSION} - {continent}'
    for continent in CONTINENTS
}


#: list[float, float]: Pixel resolutions (X/Y)
GLANCE_GRIDS_RESOLUTION = [30, 30]
#: list[int, int]: Number of columns and rows
GLANCE_GRIDS_SIZE = [5000, 5000]


#: str: Repository for the Equi7 grid information
REPO_EQUI7 = 'https://github.com/TUW-GEO/Equi7Grid.git'


def clone_equi7(dest=None):
    """ Clones the Equi7 repo using subprocess
    """
    cmd = ['git', 'clone', REPO_EQUI7]
    if dest:
        cmd.append(dest)

    try:
        run = subprocess.run(cmd, shell=False, capture_output=True)
        run.check_returncode()
    except Exception as e:
        raise RuntimeError('Could not clone the Equi7 repo') from e
    else:
        return Path(dest or 'Equi7Grid')


def create_grids():
    """ Create ``stems.gis.grids.TileGrid``s
    """
    try:
        from stems.gis import grids
    except ImportError as ie:
        msg = 'You must install `stems` library before continuing'
        raise ImportError(msg) from ie
    else:
        glance_grids = {}
        for continent in CONTINENTS:
            grid = grids.TileGrid(
                GLANCE_GRIDS_UL_XY[continent],
                GLANCE_GRID_CRS_WKT[continent],
                GLANCE_GRIDS_RESOLUTION,
                GLANCE_GRIDS_SIZE,
                GLANCE_GRIDS_LIMITS[continent],
                GLANCE_GRIDS_NAME[continent]
            )
            glance_grids[continent] = grid

        return glance_grids


def find_equi7(repo=None):
    """ Load Equi7 data
    """
    # Find or clone the Equi7 data
    repo = Path(repo or 'Equi7Grid')
    if not repo.exists():
        warnings.warn('You should clone the Equi7 repo yourself, but will try '
                      'to do it for you.')
        repo = Path(clone_equi7())

    # Find / load data
    data = {}
    for continent in CONTINENTS:
        for crs_type in ('GEOG', 'PROJ', ):
            for data_type in ('ZONE', 'LAND', ):
                key = (continent, crs_type, data_type, )
                filename = repo.joinpath(
                    'equi7grid', 'grids', continent, crs_type,
                    f'EQUI7_V13_{continent}_{crs_type}_{data_type}.shp'
                )
                data[key] = filename
    return data


def prepare_crs_wkt(wkt):
    return wkt.replace('\n', '').replace('\t', '').replace(' ' * 4, '')


def run_ogr2ogr(src, dst, dst_crs=None, dst_format='ESRI Shapefile',
                overwrite=True):
    """ Run ogr2ogr on a vector file
    """
    cmd = [
        'ogr2ogr', '-f', dst_format,
        '-nlt', 'MultiPolygon',
    ]
    if overwrite:
        cmd.append('-overwrite')
    if dst_crs:
        cmd.extend(['-t_srs', prepare_crs_wkt(dst_crs.wkt)])
    cmd.extend([str(dst), str(src)])

    # ogr2ogr won't overwrite with geojson
    if dst.exists() and dst.suffix.lower() == '.geojson' and overwrite:
        dst.unlink()

    try:
        run = subprocess.run(cmd, shell=False, capture_output=True)
        run.check_returncode()
    except Exception as e:
        raise RuntimeError('Could not run ogr2ogr') from e
    else:
        return dst


def write_grid_specs(grids, dest):
    """ Write grid definitions to a filename
    """
    grid_info = {continent: grids[continent].to_dict() for continent in grids}

    Path(dest).parent.mkdir(exist_ok=True, parents=True)
    with open(str(dest), 'w') as dst:
        yaml.safe_dump(grid_info, stream=dst)
    return dest


def write_crs_wkt(grids, dest_dir):
    """ Write out grid CRS as WKT
    """
    dest_files = {}
    dest_dir.mkdir(parents=True, exist_ok=True)
    for continent in grids:
        dest = dest_dir.joinpath(
            f'GLANCE_GRIDS_{VERSION}_{continent}_CRS.wkt')
        with open(str(dest), 'w') as dst:
            dst.write(grids[continent].crs.wkt)
        dest_files[continent] = dest
    return dest_files


def switch_crs_type(crs_type, grid):
    if crs_type == 'GEOG':
        dst_crs = CRS.from_epsg(4326)
        dst_format = 'GeoJSON'
        extension = 'geojson'
    else:
        dst_crs = grid.crs
        dst_format = 'ESRI Shapefile'
        extension = 'shp'
    return dst_crs, dst_format, extension


def safe_unary_union(obj, max_tries=5):
    tries = 0
    buffer_ = 0.
    while tries < max_tries:
        if not obj.is_valid.all():
            obj = obj.buffer(buffer_)
        try:
            obj_union = obj.unary_union
        except Exception as e:
            tries += 1
            buffer_ += 0.001 * tries
            click.echo(f'    Error running `unary_union` (#{tries - 1}). '
                       f'Trying with larger buffer ({buffer_})')
            obj = obj.buffer(buffer_)
        else:
            return obj_union


def write_grid_geom(grid, land, dst, dst_format):
    """ Create grid geometry with land/water bool -- ONLY USE PROJ LAYER
    """
    gj = grid.geojson(crs=None)
    crs = grid.crs

    gdf_grid = gpd.GeoDataFrame.from_features(gj, crs=crs.to_dict())
    if not gdf_grid.is_valid.all():
        gdf_grid.geometry = gdf_grid.buffer(0.)
        click.echo('    Fixed (?) tile geometry...')

    click.echo('    Reading & creating union of land area')
    gdf_land = gpd.read_file(land)
    gdf_land_all = safe_unary_union(gdf_land)

    click.echo('    Calculating intersection')
    is_land = gdf_grid.intersects(gdf_land_all)

    click.echo(f'    Found {is_land.sum()} intersecting tiles')

    gdf_grid = gdf_grid.assign(land=is_land.values)
    gdf_grid.to_file(dst, driver=dst_format)

    return dst


@click.command()
@click.argument('dest', type=click.Path(resolve_path=True, file_okay=False))
@click.option('--equi7_repo', type=click.Path(resolve_path=True),
              default='Equi7Grid', show_default=True,
              help='Equi7Grid repo location (will try to clone if needed)')
def make_grids(dest, equi7_repo):
    """ Create BU MEaSUREs project tile grid
    """
    # Locate Equi7 data
    equi7_data = find_equi7(equi7_repo)
    glance_grids = create_grids()

    # Create output location
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    # Generate grid specification file
    file_grid_specs = dest.joinpath(f'GLANCE_GRID_{VERSION}_PARAMETERS.yml')
    file_grid_specs_ = write_grid_specs(glance_grids, file_grid_specs)
    click.echo(f'Wrote grid specifications to "{file_grid_specs_}"')

    # Generate CRS WKT files
    dir_crs_wkt = dest.joinpath('crs_wkt')
    files_crs_wkt = write_crs_wkt(glance_grids, dir_crs_wkt)

    dest_spatial = dest.joinpath('spatial')

    # Generate zones & land layers
    glance_data = {}
    for key, src_filename in equi7_data.items():
        continent, crs_type, data_type = key

        # Get CRS/format/file extension by CRS type (proj/geog)
        dst_crs, dst_format, extension = switch_crs_type(
            crs_type, glance_grids[continent])

        # Determine output filename
        dst_filename = dest_spatial.joinpath(
            continent, crs_type,
            f'GLANCE_{VERSION}_{continent}_{crs_type}_{data_type}.{extension}')
        dst_filename.parent.mkdir(exist_ok=True, parents=True)

        # Convert/reproject/etc to create our own versions
        click.echo(f'Generating {data_type} - {crs_type} - {continent} - '
                   f'"{dst_filename}"')
        dst_filename_ = run_ogr2ogr(src_filename, dst_filename,
                                    dst_crs=dst_crs, dst_format=dst_format)
        glance_data[key] = dst_filename_

    # Generate tiles
    click.echo('Creating tiles')
    for continent, grid in glance_grids.items():
        # Need to do the intersection math on projected data
        crs_type = 'PROJ'

        # Generate filename
        dst_crs, dst_format, extension = switch_crs_type(crs_type, grid)
        dst_filename = dest_spatial.joinpath(
            continent, crs_type,
            f'GLANCE_{VERSION}_{continent}_{crs_type}_TILE.{extension}')
        dst_filename.parent.mkdir(exist_ok=True, parents=True)

        # Need land layer in same CRS type
        land = glance_data[(continent, crs_type, 'LAND')]

        # Create new column "land" for intersecting tiles, and write
        click.echo(f'Generating TILE - {crs_type} - {continent} - '
                   f'"{dst_filename}"')
        dst_filename_ = write_grid_geom(grid, land, dst_filename, dst_format)

        glance_data[(continent, crs_type, 'TILE')] = dst_filename

        # Create GEOG version
        crs_type = 'GEOG'
        dst_crs, dst_format, extension = switch_crs_type('GEOG', grid)

        dst_filename_geog = dest_spatial.joinpath(
            continent, 'GEOG',
            f'GLANCE_{VERSION}_{continent}_GEOG_TILE.{extension}')
        dst_filename_geog.parent.mkdir(exist_ok=True, parents=True)

        click.echo('    Writing GEOG version of tiles')
        dst_filename_geog = run_ogr2ogr(dst_filename, dst_filename_geog,
                                        dst_crs=dst_crs, dst_format=dst_format)

    click.echo('Complete')


if __name__ == '__main__':
    make_grids()
