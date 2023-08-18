with import <nixpkgs> {};
let
  pythonEnv = python311.withPackages (ps: [
    ps.numpy
    ps.toolz
    ps.scipy
    ps.matplotlib
    ps.astropy
  ]);
in
  mkShell rec {
    buildInputs = [
      # Python
      pythonEnv
      black

      # sdr-rlt
      gnuradio
      rtl-sdr
      sdrpp
      sdrangel
    ];
  }
