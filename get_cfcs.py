#!/usr/bin/env python

import requests
import pandas as pd
import numpy as np
import xarray as xr
import os


urlroot = "https://www.ncei.noaa.gov/data/oceans/ncei/ocads/data/0001644/GLODAP_gridded.data/"
folder = "CFC.data"
cfc11_file = "CFC-11.data.txt"
cfc12_file = "CFC-12.data.txt"


def download_file(glodap_url, folder=None, urlroot=None):
    """ download file from glodap data wbsite """

    with open(glodap_url, "wb") as f:
        response = requests.get(f"{urlroot}/{folder}/{glodap_url}")
        f.write(response.content)
    return None


def convert_to_netcdf(glodap_data, fillvalue=-999., min_depth=0, max_depth=None):
    """ convert a glodap text file to netcdf """

    df = pd.read_csv(glodap_data, sep=",", header=None)
    raw_data = np.reshape( df.to_numpy(), [-1, 360, 180])
    # replace missing values by NaN
    raw_data[np.where(raw_data == fillvalue)] = np.nan

    da = xr.DataArray(raw_data, dims=("depth", "lon", "lat"))
    da = da.transpose(*("depth", "lat", "lon"))
    return da.isel(depth=slice(min_depth, max_depth))

if __name__ == "__main__":

    for f in [cfc11_file, cfc12_file]:
        download_file(f, folder=folder, urlroot=urlroot)

    if not os.path.exists("glodap_coords.nc"):
        raise ValueError("please run get_coords.py first to create coords file")

    ds = xr.open_dataset("glodap_coords.nc")

    ds["CFC11"] = convert_to_netcdf(cfc11_file)
    ds["CFC12"] = convert_to_netcdf(cfc12_file, min_depth=33)

    encoding = {"lon": {"_FillValue": 1e+20},
                "lat": {"_FillValue": 1e+20},
                "depth": {"_FillValue": 1e+20},
                "depth_bnds": {"_FillValue": 1e+20},
                "CFC11": {"_FillValue": 1e+20},
                "CFC12": {"_FillValue": 1e+20},
               }

    ds.to_netcdf("glodap_cfc.nc", encoding=encoding)

