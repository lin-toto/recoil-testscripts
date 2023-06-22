#!/bin/bash

MAKEFLAGS="-j1"

AVX2=$(lscpu|grep avx2)
if [ -z "$AVX2" ]; then
  echo "No AVX2 support detected, cannot build! \n"
  exit 1
fi

cmake -DFLAGS="-DPROB_BITS=11" -S ./recoil -B ./recoil-bin-n11-avx2 -DCMAKE_BUILD_TYPE=Release
make -C ./recoil-bin-n11-avx2 "$MAKEFLAGS"

cmake -DFLAGS="-DPROB_BITS=16" -S ./recoil -B ./recoil-bin-n16-avx2 -DCMAKE_BUILD_TYPE=Release
make -C ./recoil-bin-n16-avx2 "$MAKEFLAGS"

AVX512=$(lscpu|grep avx512f)
if [ -z "$AVX512" ]; then
  echo "No AVX512 support detected, will only be able to run AVX2 tests!\n"
else
  cmake -DFLAGS="-DPROB_BITS=11 -DAVX512" -S ./recoil -B ./recoil-bin-n11-avx512 -DCMAKE_BUILD_TYPE=Release
  make -C ./recoil-bin-n11-avx512 "$MAKEFLAGS"

  cmake -DFLAGS="-DPROB_BITS=16 -DAVX512" -S ./recoil -B ./recoil-bin-n16-avx512 -DCMAKE_BUILD_TYPE=Release
  make -C ./recoil-bin-n16-avx512 "$MAKEFLAGS"
fi

make NUM_STATES=1024 -C ./multians "$MAKEFLAGS"
cp ./multians/bin/multians ./multians-n11
make NUM_STATES=32768 -C ./multians "$MAKEFLAGS"
cp ./multians/bin/multians ./multians-n16
