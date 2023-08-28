import argparse
import utils
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import matplotlib.mlab as mlab
import numpy
import matplotlib.gridspec as gridspec

def parse_args():
    parser = argparse.ArgumentParser(description="Plots frequency magnitude of the given IQ sample file.")
    parser.add_argument("--sample-rate", default=2_048_000)
    parser.add_argument("--freq", help="Center frequency in Hz", type=int, required=True)
    parser.add_argument("sample_file", metavar='FILE', type=str,
                        help="Path to the sample file")

    parser.add_argument("--save-avg-fft", type=str, default=None,
                        help="Save average FFT to the specified CSV file. By default no CSV is created.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    data = utils.iq_file_to_signal(args.sample_file)

    gs = gridspec.GridSpec(2, 2)
    plt.figure()

    plt.subplot(gs[0, 0])

    # https://github.com/matplotlib/matplotlib/blob/v3.7.2/lib/matplotlib/axes/_axes.py#L7355-L7439
    spec, freqs = mlab.magnitude_spectrum(data, Fs=args.sample_rate, sides="onesided")
    freqs += args.freq
    Z = 20. * np.log10(spec) # energy units to dB
    plt.plot(freqs, Z)
    plt.title("Raw FFT")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")

    plt.subplot(gs[0, 1])
    spec, freqs, t, im = plt.specgram(data, Fs=args.sample_rate, Fc=args.freq)
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.title("Spectrogram")

    plt.subplot(gs[1, :])
    # plt.magnitude_spectrum(data, Fs=args.sample_rate, sides="onesided")
    avg_fft = np.mean(spec, axis=-1)
    plt.plot(freqs, avg_fft)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.title("Average FFT")

    if args.save_avg_fft is not None:
        with open(args.save_avg_fft, "w") as f:
            f.write("frequency,magnitude\n")
            for freq, mag in zip(freqs, avg_fft):
                f.write(f"{freq},{mag}\n")

    plt.suptitle(f"Sample file: {args.sample_file}")
    plt.tight_layout()
    plt.show()
