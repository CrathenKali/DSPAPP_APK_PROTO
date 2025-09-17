#!/bin/bash

# Car Audio DSP APK Build Script

# Automated build process for multiple environments

# Compatible with mobile development workflow

set -e  # Exit on any error

# Colors for output

RED=’\033[0;31m’
GREEN=’\033[0;32m’
YELLOW=’\033[1;33m’
BLUE=’\033[0;34m’
NC=’\033[0m’ # No Color

# Configuration

PROJECT_NAME=“Car Audio DSP Pro”
APK_NAME=“caraudiodsp”
BUILD_MODE=“debug”  # or “release”
BUILDOZER_SPEC=“buildozer.spec”

# Directories

PROJECT_DIR=”$(pwd)”
BUILD_DIR=”.buildozer”
DIST_DIR=“bin”
SRC_DIR=“src”

echo -e “${BLUE}=== $PROJECT_NAME Build Script ===${NC}”
echo -e “${BLUE}Starting APK build process…${NC}”

# Function to check if command exists

command_exists() {
command -v “$1” >/dev/null 2>&1
}

# Function to print status

print_status() {
echo -e “${GREEN}[INFO]${NC} $1”
}

print_warning() {
echo -e “${YELLOW}[WARNING]${NC} $1”
}

print_error() {
echo -e “${RED}[ERROR]${NC} $1”
}

# Check prerequisites

check_prerequisites() {
print_status “Checking prerequisites…”

```
# Check Python
if ! command_exists python3; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check Buildozer
if ! command_exists buildozer; then
    print_warning "Buildozer not found. Installing..."
    pip3 install --user buildozer
    
    # Add to PATH if not already there
    export PATH=$PATH:~/.local/bin
fi

# Check Java (for Android SDK)
if ! command_exists java; then
    print_warning "Java not found. Please install OpenJDK 11 or later"
fi

# Check Android SDK environment
if [ -z "$ANDROID_HOME" ] && [ -z "$ANDROID_SDK_ROOT" ]; then
    print_warning "Android SDK environment variables not set"
    print_warning "Buildozer will download SDK automatically"
fi

print_status "Prerequisites check completed"
```

}

# Setup project structure

setup_project() {
print_status “Setting up project structure…”

```
# Create necessary directories
mkdir -p "$SRC_DIR/android/java/org/dspproject/caraudiodsp"
mkdir -p "$SRC_DIR/android/res/drawable"
mkdir -p "$SRC_DIR/android/templates"
mkdir -p "data"
mkdir -p "$DIST_DIR"

# Copy Android Java files if they exist
if [ -f "AudioService.java" ]; then
    cp AudioService.java "$SRC_DIR/android/java/org/dspproject/caraudiodsp/"
    print_status "Copied AudioService.java"
fi

# Copy manifest template if it exists
if [ -f "AndroidManifest.tmpl.xml" ]; then
    cp AndroidManifest.tmpl.xml "$SRC_DIR/android/templates/"
    print_status "Copied AndroidManifest template"
fi

# Create default icon if it doesn't exist
if [ ! -f "data/icon.png" ]; then
    print_warning "No icon found. Please add data/icon.png (512x512 recommended)"
    # Create a simple placeholder icon using ImageMagick if available
    if command_exists convert; then
        convert -size 512x512 xc:blue -fill white -gravity center \
                -pointsize 48 -annotate 0 "DSP" "data/icon.png"
        print_status "Created placeholder icon"
    fi
fi

# Create presplash if it doesn't exist
if [ ! -f "data/presplash.png" ]; then
    if [ -f "data/icon.png" ]; then
        cp "data/icon.png" "data/presplash.png"
        print_status "Using icon as presplash"
    fi
fi

print_status "Project structure setup completed"
```

}

# Clean previous builds

clean_build() {
print_status “Cleaning previous builds…”

```
if [ "$1" == "--full" ]; then
    rm -rf "$BUILD_DIR"
    print_status "Full clean completed"
else
    print_error "Build failed! Check the output above for errors."
    exit 1
fi
```

}

# Deploy to device

deploy_apk() {
print_status “Deploying APK to device…”

```
if ! command_exists adb; then
    print_warning "ADB not found. Please install Android SDK tools."
    return 1
fi

# Check if device is connected
DEVICES=$(adb devices | grep -v "List of devices" | grep "device$" | wc -l)

if [ "$DEVICES" -eq 0 ]; then
    print_warning "No Android devices connected via ADB"
    print_warning "Please connect your headunit via USB and enable USB debugging"
    return 1
fi

# Find latest APK
APK_FILE=$(find "$DIST_DIR" -name "*.apk" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)

if [ -z "$APK_FILE" ]; then
    print_error "No APK file found. Build first."
    return 1
fi

print_status "Installing $APK_FILE to device..."

# Uninstall previous version first (ignore errors)
adb uninstall org.dspproject.caraudiodsp 2>/dev/null || true

# Install new APK
if adb install "$APK_FILE"; then
    print_status "APK installed successfully!"
    
    # Launch the app
    print_status "Launching Car Audio DSP Pro..."
    adb shell am start -n org.dspproject.caraudiodsp/org.kivy.android.PythonActivity
    
else
    print_error "APK installation failed!"
    return 1
fi
```

}

# Generate development environment info

dev_info() {
print_status “Development Environment Info:”
echo “”
echo “Project: $PROJECT_NAME”
echo “Package: org.dspproject.caraudiodsp”
echo “Build Mode: $BUILD_MODE”
echo “Python: $(python3 –version)”

```
if command_exists buildozer; then
    echo "Buildozer: $(buildozer --version)"
fi

if [ -n "$ANDROID_HOME" ]; then
    echo "Android SDK: $ANDROID_HOME"
elif [ -n "$ANDROID_SDK_ROOT" ]; then
    echo "Android SDK: $ANDROID_SDK_ROOT"
fi

if command_exists adb; then
    echo "ADB Devices:"
    adb devices
fi

if command_exists git && git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Git Commit: $(git rev-parse --short HEAD)"
    echo "Git Branch: $(git branch --show-current)"
fi

echo ""
```

}

# Show help

show_help() {
echo “Usage: $0 [OPTIONS] [COMMAND]”
echo “”
echo “Commands:”
echo “  build       Build APK (default)”
echo “  clean       Clean build artifacts”
echo “  deploy      Deploy APK to connected device”
echo “  full        Clean, build, and deploy”
echo “  info        Show development environment info”
echo “  help        Show this help message”
echo “”
echo “Options:”
echo “  –release   Build release APK (requires signing)”
echo “  –debug     Build debug APK (default)”
echo “  –clean     Clean before building”
echo “  –full-clean Clean everything including SDK downloads”
echo “”
echo “Examples:”
echo “  $0                  # Build debug APK”
echo “  $0 –release build  # Build release APK”
echo “  $0 deploy           # Deploy to device”
echo “  $0 full             # Clean, build, and deploy”
echo “”
}

# Parse command line arguments

parse_args() {
COMMAND=“build”
CLEAN_BUILD=false
FULL_CLEAN=false

```
while [[ $# -gt 0 ]]; do
    case $1 in
        --release)
            BUILD_MODE="release"
            shift
            ;;
        --debug)
            BUILD_MODE="debug"
            shift
            ;;
        --clean)
            CLEAN_BUILD=true
            shift
            ;;
        --full-clean)
            FULL_CLEAN=true
            shift
            ;;
        build|clean|deploy|full|info|help)
            COMMAND="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done
```

}

# Main execution

main() {
# Parse arguments
parse_args “$@”

```
# Show help if requested
if [ "$COMMAND" == "help" ]; then
    show_help
    exit 0
fi

# Show dev info if requested
if [ "$COMMAND" == "info" ]; then
    dev_info
    exit 0
fi

# Clean if requested
if [ "$COMMAND" == "clean" ] || [ "$CLEAN_BUILD" == true ] || [ "$FULL_CLEAN" == true ]; then
    if [ "$FULL_CLEAN" == true ]; then
        clean_build --full
    else
        clean_build
    fi
    
    if [ "$COMMAND" == "clean" ]; then
        exit 0
    fi
fi

# Execute main command
case $COMMAND in
    build)
        check_prerequisites
        setup_project
        update_buildozer_spec
        build_apk
        ;;
    deploy)
        deploy_apk
        ;;
    full)
        check_prerequisites
        setup_project
        clean_build
        update_buildozer_spec
        build_apk
        deploy_apk
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac
```

}

# Trap CTRL+C and cleanup

trap ‘echo -e “\n${YELLOW}Build interrupted by user${NC}”; exit 130’ INT

# Run main function with all arguments

main “$@”

echo -e “${GREEN}=== Build Script Completed ===${NC}”
# Clean only APK artifacts
rm -f “$DIST_DIR”/*.apk
rm -f “$DIST_DIR”/*.aab
print_status “APK clean completed”
fi
}

# Update buildozer.spec with current configuration

update_buildozer_spec() {
print_status “Updating buildozer.spec…”

```
# Backup original spec file
if [ -f "$BUILDOZER_SPEC" ]; then
    cp "$BUILDOZER_SPEC" "$BUILDOZER_SPEC.backup"
fi

# Update version based on git commit if available
if command_exists git && git rev-parse --git-dir > /dev/null 2>&1; then
    GIT_COMMIT=$(git rev-parse --short HEAD)
    GIT_VERSION=$(git rev-list --count HEAD)
    
    # Update version in spec file if it exists
    if [ -f "$BUILDOZER_SPEC" ]; then
        sed -i.tmp "s/^version = .*/version = 2.1.$GIT_VERSION/" "$BUILDOZER_SPEC"
        sed -i.tmp "s/^version.regex = .*/version.regex = __version__ = ['\"']([^'\"']*)['\"']/" "$BUILDOZER_SPEC"
        rm -f "$BUILDOZER_SPEC.tmp"
        print_status "Updated version to 2.1.$GIT_VERSION (commit: $GIT_COMMIT)"
    fi
fi
```

}

# Build APK

build_apk() {
print_status “Building APK…”

```
# Set build mode
if [ "$BUILD_MODE" == "release" ]; then
    print_status "Building RELEASE APK..."
    buildozer android release
else
    print_status "Building DEBUG APK..."
    buildozer android debug
fi

# Check if build was successful
if [ $? -eq 0 ]; then
    print_status "Build completed successfully!"
    
    # Find and display APK info
    APK_FILE=$(find "$DIST_DIR" -name "*.apk" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    
    if [ -n "$APK_FILE" ]; then
        APK_SIZE=$(du -h "$APK_FILE" | cut -f1)
        print_status "APK created: $APK_FILE ($APK_SIZE)"
        
        # Generate installation commands
        echo ""
        echo -e "${YELLOW}=== Installation Commands ===${NC}"
        echo "ADB Install: adb install \"$APK_FILE\""
        echo "ADB Install (force): adb install -r \"$APK_FILE\""
        echo ""
    fi
    
else
```