#!/bin/bash
# Quick test run after MediaPipe fix

echo "Testing pipeline after MediaPipe API fix..."
python3 scripts/processing/run_pipeline.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ SUCCESS!"
    echo ""
    ls -lh data/output/
else
    echo ""
    echo "✗ Failed - check errors above"
    exit 1
fi
