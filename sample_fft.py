import argparse
import utils
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import matplotlib.mlab as mlab
import numpy

def parse_args():
    parser = argparse.ArgumentParser(description="Plots frequency magnitude of the given IQ sample file.")
    parser.add_argument("--sample-rate", default=2_048_000)
    parser.add_argument("--freq", help="Center frequency in Hz", type=int, required=True)
    parser.add_argument("sample_file", metavar='FILE', type=str,
                        help="Path to the sample file")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    data = utils.iq_file_to_signal(args.sample_file)

    # https://github.com/matplotlib/matplotlib/blob/v3.7.2/lib/matplotlib/axes/_axes.py#L7355-L7439
    spec, freqs = mlab.magnitude_spectrum(data, Fs=args.sample_rate, sides="onesided")
    freqs += args.freq
    Z = 20. * np.log10(spec) # energy units to dB
    plt.plot(freqs, Z)
    print("Frequency range:", np.min(freqs), np.max(freqs))
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")
    plt.show()

    s, f, t, im = plt.specgram(data, Fs=args.sample_rate)
    plt.show()

    plt.magnitude_spectrum(data, Fs=args.sample_rate, sides="onesided")
    plt.show()
