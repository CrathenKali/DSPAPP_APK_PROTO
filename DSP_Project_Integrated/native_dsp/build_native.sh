#!/usr/bin/env bash
set -e
: "${ANDROID_NDK_ROOT:=${HOME}/Android/Sdk/ndk/23.1.7779620}"
if [ ! -d "$ANDROID_NDK_ROOT" ]; then
  echo "ANDROID_NDK_ROOT not found: $ANDROID_NDK_ROOT"
  exit 1
fi
ABIS=("arm64-v8a" "armeabi-v7a")
OUTDIR="$(pwd)/output_jniLibs"
mkdir -p build-android && cd build-android
for ABI in "${ABIS[@]}"; do
  rm -rf ./*
  cmake -DCMAKE_TOOLCHAIN_FILE="$ANDROID_NDK_ROOT/build/cmake/android.toolchain.cmake" -DANDROID_ABI=$ABI -DANDROID_PLATFORM=android-21 ..
  cmake --build . --config Release
  # find built lib
  LIBPATH=$(find . -name "libnative_dsp.so" | head -n1)
  if [ -z "$LIBPATH" ]; then
    echo "Built lib not found for $ABI"; exit 1
  fi
  mkdir -p "${OUTDIR}/${ABI}"
  cp "$LIBPATH" "${OUTDIR}/${ABI}/libnative_dsp.so"
  echo "Copied lib for $ABI to ${OUTDIR}/${ABI}/libnative_dsp.so"
done
echo "Built all ABIs. Output in ${OUTDIR}"
