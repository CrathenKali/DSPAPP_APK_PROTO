package com.example.dspa

object DSPController {
    init { System.loadLibrary("native-lib") }

    external fun dsp_start(sampleRate: Int, channels: Int): Boolean
    external fun dsp_stop(): Boolean
    external fun dsp_apply_state_json(jsonState: String)
    external fun dsp_get_meters(outPeaks: FloatArray)

    fun start(sr: Int, ch: Int): Boolean = dsp_start(sr, ch)
    fun stop(): Boolean = dsp_stop()
    fun applyState(json: String) = dsp_apply_state_json(json)
    fun getMeters(count: Int): FloatArray {
        val out = FloatArray(count)
        dsp_get_meters(out)
        return out
    }
}
