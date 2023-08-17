with import <nixpkgs> {};
let
  pythonEnv = python311.withPackages (ps: [
    ps.numpy
    ps.toolz
    ps.scipy
    ps.matplotlib
  ]);
in
  mkShell rec {
    buildInputs = [
      pythonEnv
      gnuradio
      rtl-sdr
      sdrpp
      sdrangel
    ];

    # RUST_BACKTRACE = 1;
  }
