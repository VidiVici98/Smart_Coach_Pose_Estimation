# COPY-PASTE THIS INTO YOUR TERMINAL - ALL COMMANDS IN ONE BLOCK

# Fix OpenGL library issue
sudo apt-get update && sudo apt-get install -y libgl1-mesa-glx libglib2.0-0

# Install Python packages
pip install -q -r requirements.txt

# Download YOLO models
cd data/models
wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8m-pose.pt
wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt
mv yolov8n.pt yolov8n-face.pt
cd ../..

# Verify all files present
echo "Checking files..."
ls -lh data/models/
ls -lh data/input/test_video.mp4

# Run the pipeline
echo ""
echo "Starting pipeline..."
python3 scripts/processing/run_pipeline.py

# Check output
echo ""
echo "Checking output..."
ls -lh data/output/
