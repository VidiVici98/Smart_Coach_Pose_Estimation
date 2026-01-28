#!/usr/bin/env python3
"""Quick syntax check for run_pipeline.py"""

import py_compile
import sys

try:
    py_compile.compile('scripts/processing/run_pipeline.py', doraise=True)
    print("✓ Syntax check PASSED - no errors found")
    sys.exit(0)
except py_compile.PyCompileError as e:
    print(f"✗ Syntax ERROR:")
    print(e)
    sys.exit(1)
