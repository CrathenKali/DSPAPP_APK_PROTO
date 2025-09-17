#include "kiss_fft.h"
#include <math.h>
#include <stdlib.h>
// very small DFT fallback implementation (not optimized) for prototyping
void kiss_fft(const kiss_fft_cpx *fin, kiss_fft_cpx *fout, int n) {
    const double PI = 3.14159265358979323846;
    for (int k=0;k<n;k++) {
        double sr = 0.0, si = 0.0;
        for (int t=0;t<n;t++) {
            double angle = -2.0*PI*k*t / n;
            double cr = cos(angle), ci = sin(angle);
            sr += fin[t].r * cr - fin[t].i * ci;
            si += fin[t].r * ci + fin[t].i * cr;
        }
        fout[k].r = (float)sr;
        fout[k].i = (float)si;
    }
}
