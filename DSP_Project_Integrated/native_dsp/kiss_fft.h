#ifndef KISS_FFT_H
#define KISS_FFT_H
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef struct { float r,i; } kiss_fft_cpx;
void kiss_fft(const kiss_fft_cpx *fin, kiss_fft_cpx *fout, int n);
#ifdef __cplusplus
}
#endif
#endif
