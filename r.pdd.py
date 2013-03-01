#!/usr/bin/env python

############################################################################
#
# MODULE:      r.in.pdd
#
# AUTHOR(S):   Julien Seguinot
#
# PURPOSE:     Positive Degree Day (PDD) model for glacier mass balance
#
# COPYRIGHT:   (c) 2013 Julien Seguinot
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################################

#%Module
#% description: Positive Degree Day (PDD) model for glacier mass balance
#% keywords: raster pdd
#%End

#%option
#% key: temp
#% type: string
#% gisprompt: old,cell,raster
#% description: Name of input temperature raster maps
#% required: yes
#% multiple: yes
#%end
#%option
#% key: prec
#% type: string
#% gisprompt: old,cell,raster
#% description: Name of input precipitation raster maps
#% required: yes
#% multiple: yes
#%end
#%option
#% key: smb
#% type: string
#% gisprompt: new,cell,raster
#% description: Name for output surface mass balance raster map
#% required: yes
#%end

import numpy as np                    # scientific module Numpy [1]
import grass.script as grass
import grass.script.array as garray
from pypdd import PDDModel

### Main function ###

def main():
    """main function, called at execution time"""

    # parse arguments
    temp_maps = options['temp'].split(',')
    prec_maps = options['prec'].split(',')
    smb_map   = options['smb']

    # read temperature maps
    grass.info('reading temperature maps...')
    temp = [grass.array.array()] * 12
    for i, m in enumerate(temp_maps):
      temp[i].read(m)
      grass.percent(i, 12, 1)

    # read precipitation maps
    grass.info('reading precipitation maps...')
    prec = [grass.array.array()] * 12
    for i, m in enumerate(prec_maps):
      prec[i].read(m)
      grass.percent(i, 12, 1)

    # run PDD model
    grass.info('running PDD model...')
    temp = np.array(temp)
    prec = np.array(prec)
    pdd = PDDModel()
    smb = garray.array()
    smb[:] = pdd(temp,prec)

    # write surface mass balance map
    grass.info('writing surface mass balance map...')
    smb.write(smb_map)

### Main program ###

if __name__ == "__main__":
    options, flags = grass.parser()
    main()

# Links
# [1] http://numpy.scipy.org
