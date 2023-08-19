import argparse
import antenna
from antenna import Rotor
import time
import numpy as np
from datetime import datetime
import os
import astropy.coordinates as coord
from astropy.time import Time
import astropy.units as u

def parse_args():
    # fmt: off
    parser = argparse.ArgumentParser(
        description="Record samples on a specified range of the sky. \
        NOTE: This script is intended to be run in the machine that has the RTL-SDR dongle.")

    parser.add_argument("--host", type=str, required=True,
            help="IP of the rotor controller.")
    parser.add_argument("--port", type=int, required=True,
            help="Port of the rotor controller.")
    parser.add_argument("--sample-rate", type=int, default=2_048_000)
    parser.add_argument("--freq", type=int, required=True,
            help="Center frequency in Hz.")
    parser.add_argument("--gain", type=int, required=True,
            help="From 0 to 48, where 0 is auto gain.")
    parser.add_argument("--rec-time", type=int, default=5,
            help="Time in seconds to record in every position.")
    parser.add_argument("--wait-time", type=int, default=5,
            help="Time in seconds to wait for the rotor to get into position.")

    #parser.add_argument("-astart", type=int, required=True,
    #        help="Azimut start angle.")
    #parser.add_argument("-aend", type=int, required=True,
    #        help="Azimut end angle.")
    #parser.add_argument("-estart", type=int, required=True,
    #        help="Elevation start angle.")
    #parser.add_argument("-eend", type=int, required=True,
    #        help="Elevation end angle.")

    parser.add_argument("--azim-range", type=int, default=0,
            help="Azimut scan range.")
    parser.add_argument("--elev-range", type=int, default=0,
            help="Elevation scan range.")
    parser.add_argument("--azim-step", type=int, default=1,
            help="Azimut range step size in degrees.")
    parser.add_argument("--elev-step", type=int, default=1,
            help="Elevation range step size in degrees.")

    # fmt: on
    return parser.parse_args()

def target_location(loc):
    now = Time.now()
    altaz = coord.AltAz(location=loc, obstime=now)
    sun = coord.get_sun(now)

    azim = sun.transform_to(altaz).az.dms # (degree, min, sec)
    elev = sun.transform_to(altaz).alt.dms

    return azim, elev

if __name__ == "__main__":
    args = parse_args()
    
    # antenna coordinates: 43.31668236491581, -1.9758713544004018
    loc = coord.EarthLocation.from_geodetic(lat=43.31627, lon=-1.975755, height=20.0)
    
    azim_range = np.arange(-args.azim_range, args.azim_range+1, step=args.azim_step)
    elev_range = np.arange(-args.elev_range, args.elev_range+1, step=args.elev_step)

    rotor = Rotor(args.host, args.port)

    antenna.enable_biast()
    time.sleep(5)

    # move the rotor to start position
    print("Moving to initial position...")
    init_az, init_el = target_location(loc)
    rotor.set_pos(azim=init_az[0] + azim_range[0], elev=init_el[0] + elev_range[0])
    time.sleep(30)

    # create the directory where data will be stored
    now = datetime.now()
    prefix = "/var/www/html/iqdata/"
    dirname = f"iq_data_{int(init_az[0])}_{int(init_el[0])}_" + now.strftime("%Y-%m-%d_%H_%M_%S")
    data_dir = prefix + dirname
    os.mkdir(data_dir)

    counter = 0
    for elev_offset in elev_range:
        for azim_offset in azim_range:
            azim, elev = target_location(loc)
            rec_azim = azim[0] + azim_offset
            rec_elev = elev[0] + elev_offset

            print(f"{counter+1}/{len(elev_range)*len(azim_range)} Moving antenna to\
 azim={rec_azim}, elev={rec_elev} (offsets: {azim_offset}, {elev_offset})")
            rotor.set_pos(azim=rec_azim, elev=rec_elev)
            time.sleep(args.wait_time)

            antenna.record_data(fname=f"{data_dir}/{counter}__{azim_offset}_{elev_offset}.bin",
                                secs=args.rec_time, freq=args.freq, gain=args.gain)

            counter += 1

    os.chdir(prefix)
    os.system(f"tar -czvf '{dirname}.tar.gz' '{dirname}'")
    os.system(f"rm -r '{dirname}'")

