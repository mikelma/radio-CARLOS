import numpy as np

def iq_file_to_signal(fname):
    """Given the path to a uint8 IQ data file, returns the signal as a numpy array.
    """
    with open(fname, mode='rb') as file:
        data = file.read()

    data = np.array(list(data), dtype=np.float32)
    data -= 127.5
    data = data[0::2] + 1j*data[1::2]
    return data
