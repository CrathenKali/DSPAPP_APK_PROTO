#ifndef DSP_API_H
#define DSP_API_H
#ifdef __cplusplus
extern "C" {
#endif
#include <stdbool.h>
bool dsp_start(int sampleRate, int channels);
bool dsp_stop();
void dsp_apply_state_json(const char* jsonState);
void dsp_get_meters(float* outPeaks);
#ifdef __cplusplus
}
#endif
#endif
