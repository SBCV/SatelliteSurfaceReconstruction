import collections
from enum import Enum
from osgeo import gdal

# https://gdal.org/python/index.html

BandStatistics = collections.namedtuple("BandStatistics", ["min", "max", "mean", "std"])


def get_image_statistics_per_band(ifp):

    # https://gdal.org/doxygen/classGDALDataset.html
    ds = gdal.Open(ifp)

    band_statistics_list = []
    for i in range(ds.RasterCount):
        #   https://gdal.org/doxygen/classGDALRasterBand.html#a6aa58b6f0a0c17722b9bf763a96ff069
        #   GetStatistics(Band self, int approx_ok, int force)
        #   Returns the minimum, maximum, mean and standard deviation of all
        #   pixel values in this band.
        stats = ds.GetRasterBand(i + 1).GetStatistics(True, True)
        band_statistics_list.append(BandStatistics(*stats))

    return band_statistics_list


def get_image_min_max(ifp):

    band_statistics_list = get_image_statistics_per_band(ifp)
    image_min = float("inf")
    image_max = float("-inf")

    for band_statistics in band_statistics_list:
        image_min = min(image_min, band_statistics.min)
        image_max = max(image_max, band_statistics.max)

    return image_min, image_max
