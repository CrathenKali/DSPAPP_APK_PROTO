package com.example.dspa

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import android.os.Handler
import android.os.Looper

class MainActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val layout = LinearLayout(this)
        layout.orientation = LinearLayout.VERTICAL
        val btn = Button(this)
        btn.text = "Start DSP"
        val status = TextView(this)
        btn.setOnClickListener {
            val started = DSPController.start(48000, 2)
            status.text = "dsp_start -> $started"
        }
        val metersBtn = Button(this)
        metersBtn.text = "Get Meters"
        metersBtn.setOnClickListener {
            val m = DSPController.getMeters(2)
            status.text = "meters: ${m.joinToString(",")}"
        }
        layout.addView(btn)
        layout.addView(metersBtn)
        layout.addView(status)
        setContentView(layout)
    }
}
