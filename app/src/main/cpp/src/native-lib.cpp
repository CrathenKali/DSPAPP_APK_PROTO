#include <jni.h>
#include "dsp_api.h"
#include <android/log.h>
#define LOG_TAG "dsp_native"
#define ALOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)

extern "C" JNIEXPORT jboolean JNICALL
Java_com_example_dspa_DSPController_dsp_1start(JNIEnv* env, jobject thiz, jint sampleRate, jint channels) {
    bool ok = dsp_start((int)sampleRate, (int)channels);
    return ok ? JNI_TRUE : JNI_FALSE;
}

extern "C" JNIEXPORT jboolean JNICALL
Java_com_example_dspa_DSPController_dsp_1stop(JNIEnv* env, jobject thiz) {
    bool ok = dsp_stop();
    return ok ? JNI_TRUE : JNI_FALSE;
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_dspa_DSPController_dsp_1apply_1state_1json(JNIEnv* env, jobject thiz, jstring json) {
    if (json == nullptr) return;
    const char* s = env->GetStringUTFChars(json, nullptr);
    dsp_apply_state_json(s);
    env->ReleaseStringUTFChars(json, s);
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_dspa_DSPController_dsp_1get_1meters(JNIEnv* env, jobject thiz, jfloatArray outArr) {
    if (outArr == nullptr) return;
    jsize len = env->GetArrayLength(outArr);
    std::vector<float> buf(len);
    dsp_get_meters(buf.data());
    env->SetFloatArrayRegion(outArr, 0, len, buf.data());
}
