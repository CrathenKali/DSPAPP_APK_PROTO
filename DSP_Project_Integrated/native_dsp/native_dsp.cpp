#include <jni.h>
#include <string>
#include <thread>
#include <atomic>
#include <fstream>
#include <vector>
#include <cmath>
#include <android/log.h>

#define LOG_TAG "native_dsp"
#define ALOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define ALOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

static std::atomic<bool> spectrum_running(false);
static std::thread spectrum_thread;

extern "C" JNIEXPORT void JNICALL
Java_org_dspproject_caraudiodsp_AudioService_nativeInit(JNIEnv *env, jobject thiz) {
    ALOGI("nativeInit called");
    // Initialize DSP engine state here (alloc buffers, init filters)
}

extern "C" JNIEXPORT void JNICALL
Java_org_dspproject_caraudiodsp_AudioService_nativeDestroy(JNIEnv *env, jobject thiz) {
    ALOGI("nativeDestroy called");
    // Clean up
    if (spectrum_running.load()) {
        spectrum_running.store(false);
        if (spectrum_thread.joinable()) spectrum_thread.join();
    }
}

extern "C" JNIEXPORT void JNICALL
Java_org_dspproject_caraudiodsp_AudioService_nativeSetEQ(JNIEnv *env, jobject thiz, jint band, jdouble value) {
    ALOGI("nativeSetEQ band=%d value=%f", band, value);
    // TODO: apply to DSP EQ state
}

extern "C" JNIEXPORT void JNICALL
Java_org_dspproject_caraudiodsp_AudioService_nativeSetGain(JNIEnv *env, jobject thiz, jdouble value) {
    ALOGI("nativeSetGain value=%f", value);
    // TODO: apply gain
}

extern "C" JNIEXPORT void JNICALL
Java_org_dspproject_caraudiodsp_AudioService_nativeSetInputMode(JNIEnv *env, jobject thiz, jstring mode) {
    const char *m = env->GetStringUTFChars(mode, NULL);
    ALOGI("nativeSetInputMode mode=%s", m);
    env->ReleaseStringUTFChars(mode, m);
    // TODO: switch input routing in native layer if needed
}

static void write_spectrum_json(const std::string &path, const std::vector<double> &spectrum) {
    std::ofstream ofs(path);
    if (!ofs) {
        ALOGE("Failed to open spectrum output: %s", path.c_str());
        return;
    }
    ofs << "{ \"spectrum\": [";
    for (size_t i = 0; i < spectrum.size(); ++i) {
        if (i) ofs << ", ";
        ofs << spectrum[i];
    }
    ofs << "] }\n";
    ofs.close();
}

extern "C" JNIEXPORT void JNICALL
Java_org_dspproject_caraudiodsp_AudioService_nativeStartSpectrum(JNIEnv *env, jobject thiz, jstring jpath) {
    const char *path_c = env->GetStringUTFChars(jpath, NULL);
    std::string path(path_c);
    env->ReleaseStringUTFChars(jpath, path_c);
    if (spectrum_running.load()) {
        ALOGI("Spectrum already running");
        return;
    }
    spectrum_running.store(true);
    spectrum_thread = std::thread([path]() {
        ALOGI("Spectrum thread started, output=%s", path.c_str());
        // Placeholder: write fake spectrum data every second until stopped.
        while (spectrum_running.load()) {
            std::vector<double> spec(128, 0.0);
            // fake data: rising slope
            for (size_t i = 0; i < spec.size(); ++i) spec[i] = sin(i*0.1) * 0.5 + 0.5;
            write_spectrum_json(path, spec);
            std::this_thread::sleep_for(std::chrono::milliseconds(1000));
        }
        ALOGI("Spectrum thread exiting");
    });
}

extern "C" JNIEXPORT void JNICALL
Java_org_dspproject_caraudiodsp_AudioService_nativeStopSpectrum(JNIEnv *env, jobject thiz) {
    if (!spectrum_running.load()) return;
    spectrum_running.store(false);
    if (spectrum_thread.joinable()) spectrum_thread.join();
    ALOGI("Spectrum stopped");
}

extern "C" JNIEXPORT void JNICALL
Java_org_dspproject_caraudiodsp_AudioService_nativeLoadPresetFile(JNIEnv *env, jobject thiz, jstring jpath) {
    const char *path_c = env->GetStringUTFChars(jpath, NULL);
    std::string path(path_c);
    env->ReleaseStringUTFChars(jpath, path_c);
    ALOGI("nativeLoadPresetFile path=%s", path.c_str());
    // TODO: parse JSON preset and apply to DSP state
}
