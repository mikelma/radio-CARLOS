import argparse
import antenna
from antenna import Rotor
import time
import datetime
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

    parser.add_argument("-astart", type=int, required=True,
            help="Azimut start angle.")
    parser.add_argument("-aend", type=int, required=True,
            help="Azimut end angle.")
    parser.add_argument("-estart", type=int, required=True,
            help="Elevation start angle.")
    parser.add_argument("-eend", type=int, required=True,
            help="Elevation end angle.")
    # fmt: on
    return parser.parse_args()

if __name__ == "__main__":
    ################
    # antenna coordinates: 43.31668236491581, -1.9758713544004018
    # loc = coord.EarthLocation.from_geodetic(lat=43.32668, lon=-1.975871, height=20.0)
    loc = coord.EarthLocation.of_address("Donostia-San Sebastian")
    now = Time.now()

    altaz = coord.AltAz(location=loc, obstime=now)
    sun = coord.get_sun(now)

    print(sun.transform_to(altaz).alt)
    quit()
    ################

    args = parse_args()

    rotor = Rotor(args.host, args.port)

    antenna.enable_biast()
    time.sleep(10)

    # move the rotor to start position
    print("Moving to initial position...")
    rotor.set_pos(azim=args.astart, elev=args.estart)
    time.sleep(30)

    # create the directory where data will be stored
    now = datetime.now()
    data_dir = "iq_data_" + now.strftime("%Y-%m-%d_%H:%M:%S")
    os.mkdir(data_dir)
