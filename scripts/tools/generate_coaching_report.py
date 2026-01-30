#!/usr/bin/env python3
"""
Generate Coaching Report from Analytics CSV

This tool takes the analytics CSV output from the Smart Coach pipeline
and generates actionable coaching feedback based on predefined rules.

Usage:
    python scripts/tools/generate_coaching_report.py [input_csv] [--format text|markdown|html] [--output report.txt]

Examples:
    # Generate text report to console
    python scripts/tools/generate_coaching_report.py data/output/analytics.csv

    # Generate HTML report to file
    python scripts/tools/generate_coaching_report.py data/output/analytics.csv --format html --output coaching_report.html

    # Generate markdown report
    python scripts/tools/generate_coaching_report.py data/output/analytics.csv --format markdown --output report.md
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from smart_coach.analysis.coaching_engine import CoachingEngine


def main():
    parser = argparse.ArgumentParser(
        description="Generate coaching feedback report from Smart Coach analytics CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data/output/analytics.csv
  %(prog)s data/output/analytics.csv --format html --output report.html
  %(prog)s data/output/analytics.csv --format markdown --output report.md
        """
    )
    
    parser.add_argument(
        'input_csv',
        nargs='?',
        default='data/output/analytics.csv',
        help='Path to analytics CSV file (default: data/output/analytics.csv)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['text', 'markdown', 'html'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file path (default: print to console)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print verbose analysis information'
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    csv_path = Path(args.input_csv)
    if not csv_path.exists():
        print(f"❌ Error: Input file not found: {csv_path}", file=sys.stderr)
        print(f"\nMake sure you've run the pipeline first:", file=sys.stderr)
        print(f"  python scripts/processing/run_pipeline.py", file=sys.stderr)
        sys.exit(1)
    
    # Load CSV
    if args.verbose:
        print(f"📊 Loading analytics from: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
        
        # Validate dataframe is not empty
        if len(df) == 0:
            print(f"⚠️  Warning: CSV file is empty", file=sys.stderr)
            print(f"   No data to analyze. Exiting.", file=sys.stderr)
            sys.exit(0)
        
        if args.verbose:
            print(f"   ✓ Loaded {len(df)} frames with {len(df.columns)} metrics")
            
            # Check for common issues
            if df.isnull().all().any():
                null_cols = df.columns[df.isnull().all()].tolist()
                print(f"   ⚠️  Warning: {len(null_cols)} columns are entirely null")
                
            nan_percent = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            if nan_percent > 50:
                print(f"   ⚠️  Warning: {nan_percent:.1f}% of data is missing")
            
    except FileNotFoundError:
        print(f"❌ Error: Input file not found: {csv_path}", file=sys.stderr)
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"❌ Error: CSV file is empty or corrupted", file=sys.stderr)
        sys.exit(1)
    except pd.errors.ParserError as e:
        print(f"❌ Error: Could not parse CSV file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    # Create coaching engine
    engine = CoachingEngine()
    
    # Generate report
    if args.verbose:
        print(f"🎯 Generating {args.format} coaching report...")
    
    try:
        report = engine.generate_report(df, output_format=args.format)
    except Exception as e:
        print(f"❌ Error generating report: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    # Output report
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(report)
        
        print(f"✅ Report saved to: {output_path}")
        
        # Show preview if text format
        if args.format == 'text' and args.verbose:
            print("\n" + "=" * 80)
            print("REPORT PREVIEW:")
            print("=" * 80)
            preview_lines = report.split('\n')[:30]
            print('\n'.join(preview_lines))
            if len(report.split('\n')) > 30:
                print(f"\n... ({len(report.split('\n')) - 30} more lines)")
    else:
        # Print to console
        print(report)
    
    # Print summary statistics if verbose
    if args.verbose:
        violations = engine.evaluate_all_rules(df)
        print("\n" + "=" * 80)
        print("ANALYSIS SUMMARY:")
        print("=" * 80)
        print(f"Total frames analyzed: {len(df)}")
        print(f"Issues detected: {len(violations)}")
        
        if violations:
            from smart_coach.analysis.coaching_engine import Severity
            critical = sum(1 for v in violations if v['severity'] == Severity.CRITICAL)
            high = sum(1 for v in violations if v['severity'] == Severity.HIGH)
            medium = sum(1 for v in violations if v['severity'] == Severity.MEDIUM)
            low = sum(1 for v in violations if v['severity'] == Severity.LOW)
            
            print(f"  - Critical: {critical}")
            print(f"  - High:     {high}")
            print(f"  - Medium:   {medium}")
            print(f"  - Low:      {low}")
        print("=" * 80)


if __name__ == '__main__':
    main()
