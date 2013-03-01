#!/usr/bin/env python

"""A Python Positive Degree Day (PDD) model for glacier surface mass balance"""

import numpy as np

# Defatult model parameters

default_pdd_factor_snow = 0.003
default_pdd_factor_ice  = 0.008
default_pdd_refreeze    = 0.6
default_pdd_std_dev     = 5.
default_temp_snow       = 0.
default_temp_rain       = 2.

# PDD model class

class PDDModel():
  """A positive degree-day model for glacier surface mass balance"""

  def __init__(self,
    pdd_factor_snow = default_pdd_factor_snow,
    pdd_factor_ice  = default_pdd_factor_ice,
    pdd_refreeze    = default_pdd_refreeze,
    pdd_std_dev     = default_pdd_std_dev,
    temp_snow       = default_temp_snow,
    temp_rain       = default_temp_rain):
    """Initiate PDD model with given parameters"""
    
    # set pdd model parameters
    self.pdd_factor_snow = pdd_factor_snow
    self.pdd_factor_ice  = pdd_factor_ice
    self.pdd_refreeze    = pdd_refreeze
    self.pdd_std_dev     = pdd_std_dev
    self.temp_snow       = temp_snow
    self.temp_rain       = temp_rain

  def __call__(self, temp, prec):
    """Compute surface mass balance from temperature and precipitation"""
    pdd  = self.pdd(temp)
    snow = self.snow(temp, prec)
    smb  = self.smb(snow, pdd)
    return smb

  def pdd(self, temp):
    """Compute positive degree days from temperature time series"""
    return sum(np.greater(temp,0)*temp)*365.242198781/12

  def snow(self, temp, prec):
    """Compute snow precipitation from temperature and precipitation"""

    # compute snow fraction as a function of temperature
    reduced_temp = (self.temp_rain-temp) / (self.temp_rain-self.temp_snow)
    snowfrac     = np.clip(reduced_temp, 0, 1)

    # return total snow precipitation
    return sum(self.snowfrac(temp)*prec)

  def smb(self, snow, pdd):
    """Compute surface mass balance from snow precipitation and pdd sum"""

    # compute snow accumulation after melt
    snow_acc = snow - pdd * self.pdd_factor_snow

    # if positive, return accumulated snow
    # if negative, compute refreezing and ice melt
    return np.where(snow_acc > 0, snow_acc, snow*self.pdd_refreeze
      + snow_acc*self.pdd_factor_ice/self.pdd_factor_snow)

  def nc(self, i_file, o_file):
    """NetCDF interface"""

    from netCDF4 import Dataset as NC

    # open netcdf files
    i = NC(i_file, 'r')
    o = NC(o_file, 'w')

    # read input data
    temp = i.variables['air_temp'][:]
    prec = i.variables['precipitation'][:]

    # convert to degC
    # TODO: handle unit conversion better
    if i.variables['air_temp'].units == 'K': temp = temp - 273.15

    # create dimensions
    o.createDimension('x', len(i.dimensions['x']))
    o.createDimension('y', len(i.dimensions['y']))

    # create variables
    smbvar = o.createVariable('smb', 'f4', ('x', 'y'))
    smbvar[:] = self(temp, prec)

    # close netcdf files
    i.close()
    o.close()

# netCDF climate initializer

def make_fake_climate(filename):
    """Create an artificial temperature and precipitation file"""

    from math import cos, pi
    from netCDF4 import Dataset as NC

    # open netcdf file
    nc = NC(filename, 'w')

    # create dimensions
    tdim = nc.createDimension('time', 12)
    xdim = nc.createDimension('x', 8)
    ydim = nc.createDimension('y', 8)

    # prepare coordinate arrays
    x = range(len(xdim))
    y = range(len(ydim))
    t = range(len(tdim))
    (xx, yy) = np.meshgrid(x, y)

    # create air temperature variable
    temp = nc.createVariable('air_temp', 'f4', ('time', 'x', 'y'))
    temp.units = 'degC'

    # create precipitation variable
    prec = nc.createVariable('precipitation', 'f4', ('time', 'x', 'y'))
    prec.units = "m yr-1"

    # assign temperature and precipitation values
    for i in t:
      temp[i] = xx - 10 * cos(i*2*pi/12)
      prec[i] = yy * (1 - cos(i*2*pi/12))/4

    # close netcdf file
    nc.close()

# Called at execution

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='A Python Positive Degree Day (PDD) model for glacier surface mass balance')
    parser.add_argument('-i', '--input',
      help='input file')
    parser.add_argument('-o', '--output',
      help='output file',
      default='smb.nc')
    parser.add_argument('--pdd-factor-snow', type=float,
      help='PDD factor for snow',
      default=default_pdd_factor_snow)
    parser.add_argument('--pdd-factor-ice', type=float,
      help='PDD factor for ice',
      default=default_pdd_factor_ice)
    parser.add_argument('--pdd-refreeze', type=float,
      help='PDD refreezing fraction',
      default=default_pdd_refreeze)
    parser.add_argument('--pdd-std-dev', type=float,
      help='Unimplemented yet',
      default=default_pdd_std_dev)
    parser.add_argument('--temp-snow', type=float,
      help='Temperature at which all precip is snow',
      default=default_temp_snow)
    parser.add_argument('--temp-rain', type=float,
      help='Temperature at which all precip is rain',
      default=default_temp_rain)
    args = parser.parse_args()

    # prepare dummy input dataset
    if not args.i:
      make_fake_climate('atm.nc')

    # initiate PDD model
    pdd=PDDModel(
      pdd_factor_snow = args.pdd_factor_snow,
      pdd_factor_ice  = args.pdd_factor_ice,
      pdd_refreeze    = args.pdd_refreeze,
      pdd_std_dev     = args.pdd_std_dev,
      temp_snow       = args.temp_snow,
      temp_rain       = args.temp_rain)

    # compute surface mass balance
    pdd.nc(args.i or 'atm.nc', args.o)
