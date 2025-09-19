plugins {
    id("com.android.application")
    kotlin("android")
}

android {
    namespace = "com.example.dspa"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.dspa"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "0.1.0"

        externalNativeBuild { cmake { arguments += listOf("-DANDROID_STL=c++_shared") } }
        ndk { abiFilters += listOf("armeabi-v7a", "arm64-v8a") }
    }

    buildTypes {
        release { isMinifyEnabled = false }
        debug { }
    }

    externalNativeBuild {
        cmake { path = file("src/main/cpp/CMakeLists.txt"); version = "3.22.1" }
    }
}

dependencies {
    implementation("org.jetbrains.kotlin:kotlin-stdlib:1.8.21")
    implementation("androidx.core:core-ktx:1.10.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
}
