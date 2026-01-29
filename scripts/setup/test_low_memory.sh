#!/bin/bash
# Quick test run with memory monitoring

echo "================================"
echo "  MEMORY STATUS BEFORE RUN"
echo "================================"
free -h
echo ""

echo "================================"
echo "  RUNNING PIPELINE (LOW MEMORY MODE)"
echo "================================"
python3 scripts/processing/run_pipeline.py &
PID=$!

# Monitor memory while running
echo "Pipeline PID: $PID"
echo "Monitoring memory usage (Ctrl+C to stop)..."
echo ""

while kill -0 $PID 2>/dev/null; do
    MEM=$(ps -p $PID -o %mem= 2>/dev/null | xargs)
    RSS=$(ps -p $PID -o rss= 2>/dev/null | awk '{printf "%.1f", $1/1024}')
    echo "Pipeline memory: ${MEM}% (${RSS} MB)"
    sleep 2
done

wait $PID
EXIT_CODE=$?

echo ""
echo "================================"
echo "  PIPELINE FINISHED"
echo "  Exit code: $EXIT_CODE"
echo "================================"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ SUCCESS!"
    echo ""
    echo "Output files:"
    ls -lh data/output/output_full.mp4 data/output/analytics.csv 2>/dev/null || echo "  (files not found)"
elif [ $EXIT_CODE -eq 143 ]; then
    echo "✗ FAILED: Exit 143 (SIGTERM / OOM)"
    echo ""
    echo "Memory issue detected. Solutions:"
    echo "  1. Already using LOW_MEMORY_MODE - may need larger codespace"
    echo "  2. See MEMORY_FIX_GUIDE.md for upgrade instructions"
    echo "  3. Try shorter video or process in chunks"
else
    echo "✗ FAILED: Exit code $EXIT_CODE"
fi

echo ""
echo "================================"
echo "  MEMORY STATUS AFTER RUN"
echo "================================"
free -h
