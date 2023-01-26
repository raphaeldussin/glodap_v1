#!/usr/bin/env python

import requests
import pandas as pd
import numpy as np
import xarray as xr


urlroot = "https://www.ncei.noaa.gov/data/oceans/ncei/ocads/data/0001644/GLODAP_gridded.data/"
lon_file = "Long.centers.txt"
lat_file = "Lat.centers.txt"
depth_file = "Depth.centers.txt"
depth_bnds_file = "DepthEdges.txt"


def download_file(glodap_url, folder=None, urlroot=None):
    ''' download file from glodap data wbsite '''

    with open(glodap_url, "wb") as f:
        response = requests.get(f"{urlroot}/{glodap_url}")
        f.write(response.content)
    return None


def create_coords_dataset(flon, flat, fdepth, fdepth_bnds):
    """ create coordinates file """

    lon = pd.read_csv(flon, sep=",", header=None).to_numpy().squeeze().astype("f")
    lat = pd.read_csv(flat, sep=",", header=None).to_numpy().squeeze().astype("f")
    depth = pd.read_csv(fdepth, sep=",", header=None).to_numpy().squeeze().astype("f")
    depth_bnds = pd.read_csv(fdepth_bnds, sep=",", header=None).to_numpy().squeeze().astype("f")

    ds = xr.Dataset()
    ds["lon"] = xr.DataArray(lon, dims=("lon"))
    ds["lat"] = xr.DataArray(lat, dims=("lat"))
    ds["depth"] = xr.DataArray(depth, dims=("depth"))
    ds["depth_bnds"] = xr.DataArray(depth_bnds, dims=("depth_bnds"))

    return ds


if __name__ == "__main__":

    for f in [lon_file, lat_file, depth_file, depth_bnds_file]:
        download_file(f, urlroot=urlroot)

    ds = create_coords_dataset(lon_file, lat_file, depth_file, depth_bnds_file)

    encoding = {"lon": {"_FillValue": 1e+20},
                "lat": {"_FillValue": 1e+20},
                "depth": {"_FillValue": 1e+20},
                "depth_bnds": {"_FillValue": 1e+20},
               }

    ds.to_netcdf("glodap_coords.nc", encoding=encoding)
