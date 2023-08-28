import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import scipy.signal as signal
import sys
import glob
import argparse
from scipy.stats import rankdata

def parse_args():
    parser = argparse.ArgumentParser(description="Generate a frequency magnitude matrix from IQ samples.")

    parser.add_argument("--freq", type=int, required=True, help="Center frequency.")
    parser.add_argument("--sample-rate", type=int, default=2_048_000)
    parser.add_argument("--window-start", type=int, required=True, help="Start of the window to analyze in Hz.")
    parser.add_argument("--window-end", type=int, required=True, help="End of the window to analyze in Hz.")

    # parser.add_argument("-astart", type=int, required=True, help="Azimut start angle.")
    # parser.add_argument("-aend", type=int, required=True, help="Azimut end angle.")
    # parser.add_argument("-estart", type=int, required=True, help="Elevation start angle.")
    # parser.add_argument("-eend", type=int, required=True, help="Elevation end angle.")

    parser.add_argument("--save-matrix", type=str, default=None,
                        help="If provided, the magnitude matrix will be saved into the specified path.")

    parser.add_argument("data_dir", type=str, default="iq_data",
                        help="Directory where the IQ samples have been recorded.")

    return parser.parse_args()

def magnitude_of_peak(data, sample_rate, center_freq, window_start, window_end):
    spec, freqs = mlab.magnitude_spectrum(data, Fs=sample_rate, sides="onesided")
    freqs += center_freq
    Z = 20. * np.log10(spec) # energy units to dB

    # reduce range
    idx = np.where((freqs >= window_start) & (freqs <= window_end))[0]
    freqs = freqs[idx]
    Z = Z[idx]

    # detect peaks
    peaks, _ = signal.find_peaks(Z, distance=len(Z))
    return Z[peaks[0]], freqs[peaks[0]], len(peaks)

    # detect peaks
    # peaks = np.argsort(Z)[::-1][:5]
    # plt.plot(freqs, Z)
    # plt.plot(freqs[peaks], Z[peaks], "bo")
    # plt.show()
    # quit()
    # pass

    # sample_len = len(data)
    # fft = np.fft.fft(data)[:sample_len//2]
    # freq_mag = np.abs(fft)
    #
    # freq_x = np.fft.fftfreq(n=data.size, d=1/sample_rate) + center_freq
    # freq_x = freq_x[:sample_len//2]
    #
    # # idx = np.where((freq_x >= 1_420_200_000) & (freq_x <= 1_420_400_000))[0]
    # idx = np.where((freq_x >= window_start) & (freq_x <= window_end))[0]
    # freq_mag = freq_mag[idx]
    # freq_x = freq_x[idx]
    #
    # peaks, _ = signal.find_peaks(freq_mag, distance=len(freq_mag))
    # return freq_mag[peaks[0]], freq_x[peaks[0]], len(peaks)

def file_to_signal(fname):
    with open(fname, mode='rb') as file:
        data = file.read()

    data = np.array(list(data), dtype=np.float32)
    data -= 127.5
    data = data[0::2] + 1j*data[1::2]
    return data

if __name__ == "__main__":
    args = parse_args()

    lst_azim = []
    lst_elev = []
    lst_mag = []
    for fname in glob.glob(f"{args.data_dir}/*.bin"):
        suf = fname.split("/")[-1]
        off_az = int(suf.split("_")[-2])
        off_el = int(suf.split("_")[-1].split(".")[0])

        data = file_to_signal(fname)
        mag, freq, num = magnitude_of_peak(data, args.sample_rate, args.freq,
                                           args.window_start, args.window_end)

        lst_azim.append(off_az)
        lst_elev.append(off_el)
        lst_mag.append(mag)

        print("\nfile: ", fname)
        print("magnitude of the peak:", mag)
        print("frequency of the peak:", freq)
        print("number of peaks:", num)

    mat = np.zeros((len(np.unique(lst_elev)), len(np.unique(lst_azim))))
    print(lst_azim, lst_elev, lst_mag)

    elev_idx = rankdata(lst_elev, method="dense") - 1
    azim_idx = rankdata(lst_azim, method="dense") - 1
    for idx, (i, j) in enumerate(zip(elev_idx, azim_idx)):
        mat[i][j] = lst_mag[idx]

    print(mat)

    plt.imshow(mat, cmap="gray")
    plt.colorbar(label="dB")
    plt.xlabel("Azimut")
    plt.ylabel("Elevation")

    x_labels = np.sort(np.unique(lst_azim))
    y_labels = np.sort(np.unique(lst_elev))

    plt.yticks(range(len(y_labels)), y_labels)
    plt.xticks(range(len(x_labels)), x_labels)
    wa, we = args.window_start / 1e9, args.window_end / 1e9
    plt.title(f"Magnitude of the peaks in the {wa}-{we} Hz range")
    plt.tight_layout()
    plt.show()

    if args.save_matrix is not None:
        print("* Saving magnitude matrix to current directory")
        np.save(args.save_matrix, mat)
