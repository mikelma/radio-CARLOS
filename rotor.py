import socket
import time
import os
from datetime import datetime
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Record samples on a specified range of the sky. NOTE: This script is intended to be run in the machine that has the RTL-SDR dongle.")

    parser.add_argument("data_dir", type=str, default="iq_data",
                        help="Directory where samples will be saved.")
    parser.add_argument("--host", type=str, required=True, help="IP of the rotor controller.")
    parser.add_argument("--port", type=int, required=True, help="Port of the rotor controller.")

    parser.add_argument("--sample-rate", type=int, default=2_048_000)
    parser.add_argument("--freq", type=int, required=True, help="Center frequency in Hz.")
    parser.add_argument("--gain", type=int, required=True, help="From 0 to 48, where 0 is auto gain.")
    parser.add_argument("--rec-time", type=int, default=5, help="Time in seconds to record in every position.")
    parser.add_argument("--wait-time", type=int, default=5, help="Time in seconds to wait for the rotor to get into position.")

    parser.add_argument("-astart", type=int, required=True, help="Azimut start angle.")
    parser.add_argument("-aend", type=int, required=True, help="Azimut end angle.")
    parser.add_argument("-estart", type=int, required=True, help="Elevation start angle.")
    parser.add_argument("-eend", type=int, required=True, help="Elevation end angle.")

    return parser.parse_args()

def enable_biast():
    cmd = f"rtl_biast - b 1"
    print(f"Enabling bias T")
    ret = os.system(cmd)
    print(f" ==> returned: {ret}")

def record_data(fname, secs, freq, sr=2_048_000, gain=0): # gain=0 is for auto
    cmd = f"rtl_sdr -f {freq} -s {sr} -g {gain} -n {secs*sr} {fname}"
    print(f"Record data cmd: {cmd}", end="")
    ret = os.system(cmd)
    print(f" ==> returned: {ret}")

def set_rotor(azimut, elev, host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        cmd = f"P {float(azimut)} {float(elev)}\n"
        print(f"Sending command: {cmd}")
        s.sendall(cmd.encode("ascii"))

if __name__ == "__main__":
    args = parse_args()

    enable_biast()
    time.sleep(10)

    # move the rotor to start position
    print("Moving to initial position...")
    set_rotor(args.astart, args.estart, args.host, args.port)
    time.sleep(30)

    now = datetime.now() # current date and time
    prefix = args.data_dir + "/" + now.strftime("%Y-%m-%d_%H:%M:%S")
    counter = 0
    correct_every = 240 // (args.wait_time + args.rec_time)
    azimut = args.astart
    for fake_azim in range(args.astart, args.aend+1):
        for elev in range(args.estart, args.eend+1):
            set_rotor(azimut, elev, args.host, args.port)

            time.sleep(args.wait_time)

            record_data(fname=f"{prefix}_{fake_azim}_{elev}.bin", secs=args.rec_time, freq=args.freq, gain=args.gain)
            counter += 1

            # correct position to counteract earth's rotation
            if counter % correct_every == 0 :
                azimut += 1

        azimut += 1
