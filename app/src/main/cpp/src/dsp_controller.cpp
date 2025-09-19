#include "dsp_api.h"
#include <android/log.h>
#define LOG_TAG_DC "dsp_controller"
#define ALOGI_DC(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG_DC, __VA_ARGS__)
// Thin wrappers; actual DSP/Oboe code lives in native/ module
