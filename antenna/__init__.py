import os

from .rotor import Rotor

def enable_biast():
    cmd = f"rtl_biast - b 1"
    ret = os.system(cmd)
    if ret != 0:
        raise Exception(f"Failed to activate bias T. Command: {cmd}")

def record_data(fname, secs, freq, sr=2_048_000, gain=0): # gain=0 is for auto
    cmd = f"rtl_sdr -f {freq} -s {sr} -g {gain} -n {secs*sr} {fname}"
    ret = os.system(cmd)
    if ret != 0:
        raise Exception(f"Failed to record radio data with rtl_sdr. Command was: {cmd}")
