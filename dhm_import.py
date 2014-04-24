#!/usr/bin/env python

#%module
#% description: Puntdata importeren en DHM aanmaken
#% keywords: AGIV DHM
#%end
#%option
#% key: dhm_file
#% type: string
#% gisprompt: old_file,file
#% description: Bronbestand
#% required: yes
#%end
#%option
#% key: mapset
#% type: string
#% Description: Mapset waarin gewerkt wordt
#% required: yes
#%end
#%option
#% key: map
#% type: string
#% Description: Basisnaam van de uitvoerbestanden
#% required: yes
#%end
#%option
#% key: north
#% type: integer
#% Description: Noordelijke begrenzing van het gebied
#% required: yes
#%end
#%option
#% key: south
#% type: integer
#% Description: Zuidelijke begrenzing van het gebied
#% required: yes
#%end
#%option
#% key: east
#% type: integer
#% Description: Oostelijke begrenzing van het gebied
#% required: yes
#%end
#%option
#% key: west
#% type: integer
#% Description: Zuidelijke begrenzing van het gebied
#% required: yes
#%end
#%option
#% key: res
#% type: integer
#% Description: Resolutie van het resultaat
#% required: yes
#%end

import sys
import os
import atexit
from glob import glob
import gzip
import grass.script as grass


def cleanup():
    grass.run_command('g.remove',
                      vect=options['map'])
    dhm_txt = os.path.join(os.path.dirname(options['dhm_file']), 'dhm.txt')
    if os.path.exists(dhm_txt):
        os.remove(dhm_txt)


def main():

    dhm_dir = os.path.dirname(options['dhm_file'])
    gzip_files = glob(os.path.join(dhm_dir, "*.grd.gz"))
    dhm_file = os.path.join(dhm_dir, 'dhm.txt')
    with open(dhm_file, 'a+b') as outputfile:
        for gzip_file in gzip_files:
            with gzip.open(gzip_file, 'rb') as inputfile:
                outputfile.write(inputfile.read())

    grass.run_command("g.mapset",
                      mapset=options['mapset'])

    grass.run_command("g.region",
                      n=options['north'],
                      s=options['south'],
                      e=options['east'],
                      w=options['west'],
                      nsres="2")

    grass.run_command("v.in.ascii",
                      input=dhm_file,
                      output=options['map'],
                      fs=" ")

    grass.run_command("v.surf.idw",
                      input=options['map'],
                      output=options['map'] + "_idw",
                      npoints=6,
                      power=2.0,
                      layer=1,
                      column='dbl_3')

    grass.run_command("r.slope.aspect",
                      elev=options['map'] + '_idw@' + options['mapset'],
                      slope=options['map'] + '_idw_slope',
                      aspect=options['map'] + '_idw_aspect',
                      pcurv=options['map'] + '_idw_pcurv',
                      tcurv=options['map'] + '_idw_tcurve',
                      dx=options['map'] + '_idw_dx',
                      dy=options['map'] + '_idw_dy',
                      dxx=options['map'] + '_idw_dxx',
                      dyy=options['map'] + '_idw_dyy',
                      dxy=options['map'] + '_idw_dxy')
    return 0

if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    sys.exit(main())
