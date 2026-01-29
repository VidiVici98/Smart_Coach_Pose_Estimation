#!/bin/bash
# Complete setup and run script for Smart Coach pipeline

echo "======================================================================"
echo "  Smart Coach Pipeline - Complete Setup & Run"
echo "======================================================================"
echo ""

# Check if face landmarker model exists and is valid
MODEL_PATH="data/models/face_landmarker.task"
if [ -f "$MODEL_PATH" ]; then
    SIZE=$(stat -f%z "$MODEL_PATH" 2>/dev/null || stat -c%s "$MODEL_PATH" 2>/dev/null)
    SIZE_MB=$((SIZE / 1024 / 1024))
    echo "Face landmarker model found: ${SIZE_MB} MB"
    
    if [ $SIZE_MB -lt 25 ] || [ $SIZE_MB -gt 28 ]; then
        echo "  ⚠ File size incorrect (expected 25-28 MB)"
        echo "  Removing corrupted file..."
        rm -f "$MODEL_PATH"
    else
        echo "  ✓ Model is valid"
    fi
else
    echo "Face landmarker model not found"
fi

# Download if missing
if [ ! -f "$MODEL_PATH" ]; then
    echo ""
    echo "Downloading face landmarker model..."
    echo "This may take 60-120 seconds depending on network speed..."
    echo ""
    
    # Use wget if available (better for large files)
    if command -v wget &> /dev/null; then
        wget -O "$MODEL_PATH" --timeout=180 --tries=3 \
            "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    # Fall back to curl
    elif command -v curl &> /dev/null; then
        curl -L --max-time 180 --retry 3 -o "$MODEL_PATH" \
            "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    # Fall back to Python script
    else
        echo "Using Python downloader..."
        python3 download_face_landmarker.py
    fi
    
    # Verify download
    if [ -f "$MODEL_PATH" ]; then
        SIZE=$(stat -f%z "$MODEL_PATH" 2>/dev/null || stat -c%s "$MODEL_PATH" 2>/dev/null)
        SIZE_MB=$((SIZE / 1024 / 1024))
        echo ""
        echo "Download complete: ${SIZE_MB} MB"
        
        if [ $SIZE_MB -lt 25 ] || [ $SIZE_MB -gt 28 ]; then
            echo "  ✗ Download appears incomplete or corrupted"
            echo "  Expected 25-28 MB, got ${SIZE_MB} MB"
            echo "  Pipeline will run without gaze detection"
        else
            echo "  ✓ Model downloaded successfully!"
        fi
    else
        echo "  ✗ Download failed"
        echo "  Pipeline will run without gaze detection"
    fi
fi

echo ""
echo "======================================================================"
echo "  Starting Pipeline"
echo "======================================================================"
echo ""

# Run the pipeline
python3 scripts/processing/run_pipeline.py

exit_code=$?

echo ""
echo "======================================================================"
if [ $exit_code -eq 0 ]; then
    echo "  ✓ Pipeline completed successfully!"
else
    echo "  ✗ Pipeline exited with code: $exit_code"
    if [ $exit_code -eq 143 ]; then
        echo "  Note: Exit code 143 typically indicates:"
        echo "    - Process was terminated (SIGTERM)"
        echo "    - Possible out-of-memory condition"
        echo "    - Or codespace resource limit reached"
    fi
fi
echo "======================================================================"
