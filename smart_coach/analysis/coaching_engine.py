"""
Coaching Insights Engine for Smart Coach

Provides rule-based coaching feedback generation from pose metrics.
Converts raw CSV analytics into actionable coaching recommendations.

Design Principles:
- Rules are based on biomechanical principles and firearm safety
- Thresholds are conservative (better false negatives than false positives)
- All feedback is constructive and actionable
- Metrics are normalized to be camera-distance invariant
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Severity level for coaching feedback."""
    CRITICAL = "critical"  # Safety issues
    HIGH = "high"         # Major form problems
    MEDIUM = "medium"     # Moderate improvements
    LOW = "low"           # Minor refinements


class MetricComparison(Enum):
    """Comparison operators for rule evaluation."""
    GREATER = ">"
    LESS = "<"
    ABS_GREATER = "abs>"
    ABS_LESS = "abs<"
    BETWEEN = "between"
    OUTSIDE = "outside"


@dataclass
class CoachingRule:
    """
    A single coaching rule that evaluates a metric against a threshold.
    
    Attributes:
        name: Short rule identifier (e.g., "stance_too_narrow")
        title: Human-readable title for feedback
        description: Detailed coaching advice
        metric: Column name in analytics CSV
        threshold: Threshold value(s) for comparison
        comparison: How to compare metric to threshold
        severity: Importance level
        min_frames: Minimum frames to trigger (avoid false positives from noise)
        frame_percentage: Minimum percentage of frames to trigger (e.g., 0.1 = 10%)
    """
    name: str
    title: str
    description: str
    metric: str
    threshold: float | Tuple[float, float]
    comparison: MetricComparison
    severity: Severity
    min_frames: int = 5
    frame_percentage: float = 0.05  # 5% of frames by default
    
    def evaluate(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Evaluate this rule against a dataframe of metrics.
        
        Returns:
            Dict with violation details if rule triggers, None otherwise.
            Dict contains: frames, percentage, example_frames, severity
        """
        if self.metric not in df.columns:
            return None
        
        # Get metric values, skip NaN but keep indices aligned
        values = df[self.metric]
        valid_mask = ~values.isna()
        values_clean = values[valid_mask]
        
        if len(values_clean) == 0:
            return None
        
        # Apply comparison logic
        if self.comparison == MetricComparison.GREATER:
            violations = values_clean > self.threshold
        elif self.comparison == MetricComparison.LESS:
            violations = values_clean < self.threshold
        elif self.comparison == MetricComparison.ABS_GREATER:
            violations = np.abs(values_clean) > self.threshold
        elif self.comparison == MetricComparison.ABS_LESS:
            violations = np.abs(values_clean) < self.threshold
        elif self.comparison == MetricComparison.BETWEEN:
            low, high = self.threshold
            violations = (values_clean >= low) & (values_clean <= high)
        elif self.comparison == MetricComparison.OUTSIDE:
            low, high = self.threshold
            violations = (values_clean < low) | (values_clean > high)
        else:
            return None
        
        violation_indices = values_clean[violations].index.tolist()
        num_violations = len(violation_indices)
        
        # Check thresholds
        percentage = num_violations / len(df)
        if num_violations < self.min_frames or percentage < self.frame_percentage:
            return None
        
        # Calculate statistics - use values_clean with violations as boolean mask
        violation_values = values_clean[violations]
        
        return {
            'rule_name': self.name,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'num_frames': num_violations,
            'total_frames': len(df),
            'percentage': percentage * 100,
            'example_frames': violation_indices[:5],  # First 5 examples
            'metric_mean': float(violation_values.mean()),
            'metric_std': float(violation_values.std()),
            'metric_min': float(violation_values.min()),
            'metric_max': float(violation_values.max())
        }


class CoachingEngine:
    """
    Main coaching insights engine.
    
    Evaluates pose metrics against predefined rules and generates
    comprehensive coaching feedback reports.
    """
    
    def __init__(self, rules: Optional[List[CoachingRule]] = None):
        """
        Initialize coaching engine with rules.
        
        Args:
            rules: List of CoachingRule objects. If None, uses default rules.
        """
        self.rules = rules if rules is not None else self._get_default_rules()
    
    @staticmethod
    def _get_default_rules() -> List[CoachingRule]:
        """
        Define default coaching rules based on shooting fundamentals.
        
        Rules are organized by category:
        - Safety (muzzle discipline, trigger finger)
        - Stance (width, balance, lean)
        - Grip (hand position, symmetry)
        - Presentation (arm extension, alignment)
        - Head position (consistency, alignment)
        """
        return [
            # === SAFETY RULES (CRITICAL) ===
            
            CoachingRule(
                name="muzzle_sweeping_body",
                title="🔴 CRITICAL: Muzzle Sweeping Body",
                description="Your firearm muzzle is pointing at or near your body. "
                            "This is a CRITICAL safety violation. "
                            "Always keep muzzle pointed in a safe direction (downrange or at the ground). "
                            "Review your draw and holster technique with a certified instructor IMMEDIATELY. "
                            "Never allow the muzzle to cross any part of your body.",
                metric="muzzle_on_body",
                threshold=0.5,  # Any value > 0.5 indicates intersection
                comparison=MetricComparison.GREATER,
                severity=Severity.CRITICAL,
                min_frames=1,  # Even ONE frame is critical
                frame_percentage=0.001  # 0.1% - any occurrence is serious
            ),
            
            CoachingRule(
                name="firearm_detection_inconsistent",
                title="Firearm Detection Inconsistent",
                description="The system is having difficulty consistently detecting your firearm. "
                            "This may affect muzzle direction tracking accuracy. "
                            "Ensure good lighting, avoid excessive motion blur, and keep the firearm clearly visible. "
                            "Consider using a firearm with more distinct visual features or better camera positioning.",
                metric="firearm_confidence",
                threshold=0.4,  # Low average confidence
                comparison=MetricComparison.LESS,
                severity=Severity.MEDIUM,
                min_frames=30,
                frame_percentage=0.30  # 30% of frames with low confidence
            ),
            
            # === STANCE RULES ===
            
            CoachingRule(
                name="stance_too_narrow",
                title="Stance Too Narrow",
                description="Your stance is narrower than recommended. "
                            "Widen your feet to approximately shoulder-width for better stability and recoil management. "
                            "A wider stance provides better balance and allows for more effective weight transfer.",
                metric="stance_width",
                threshold=0.8,  # Relative to shoulder width
                comparison=MetricComparison.LESS,
                severity=Severity.MEDIUM,
                min_frames=10,
                frame_percentage=0.15
            ),
            
            CoachingRule(
                name="stance_too_wide",
                title="Stance Too Wide",
                description="Your stance is wider than optimal. "
                            "An overly wide stance can restrict mobility and make weight transfer difficult. "
                            "Aim for approximately shoulder-width spacing.",
                metric="stance_width",
                threshold=2.0,  # Relative to shoulder width
                comparison=MetricComparison.GREATER,
                severity=Severity.LOW,
                min_frames=10,
                frame_percentage=0.15
            ),
            
            CoachingRule(
                name="excessive_body_lean",
                title="Excessive Body Lean",
                description="You're leaning significantly forward or backward. "
                            "Maintain a slight forward lean (5-10 degrees) for recoil management, "
                            "but avoid excessive lean that compromises balance. "
                            "Keep your weight centered over your feet.",
                metric="body_lean_angle",
                threshold=15.0,  # degrees
                comparison=MetricComparison.ABS_GREATER,
                severity=Severity.MEDIUM,
                min_frames=10,
                frame_percentage=0.10
            ),
            
            # === ARM EXTENSION & PRESENTATION ===
            
            CoachingRule(
                name="incomplete_arm_extension",
                title="Incomplete Arm Extension",
                description="Your arms are not fully extended during presentation. "
                            "Full extension provides better control, reduces muzzle rise, and improves sight alignment. "
                            "Focus on pushing the gun out to full extension before breaking the first shot.",
                metric="L_arm_extension",  # Check left arm (most shooters are right-handed)
                threshold=0.7,  # Should be close to 1.0 for full extension
                comparison=MetricComparison.LESS,
                severity=Severity.HIGH,
                min_frames=15,
                frame_percentage=0.20
            ),
            
            CoachingRule(
                name="arm_extension_asymmetry",
                title="Asymmetric Arm Extension",
                description="Your arms are extending unevenly. Both arms should reach approximately the same extension. "
                            "Asymmetry can indicate grip problems or inconsistent presentation. "
                            "Focus on driving both hands forward together during the draw.",
                metric="arm_extension_diff",  # Need to calculate this from L and R
                threshold=0.15,  # 15% difference
                comparison=MetricComparison.ABS_GREATER,
                severity=Severity.MEDIUM,
                min_frames=10,
                frame_percentage=0.15
            ),
            
            # === HEAD POSITION ===
            
            CoachingRule(
                name="head_position_inconsistent",
                title="Inconsistent Head Position",
                description="Your head position varies significantly between shots/presentations. "
                            "Consistent head position is critical for sight alignment and target acquisition. "
                            "Focus on bringing the gun up to your eye level rather than dropping your head down to the sights.",
                metric="head_pitch",
                threshold=12.0,  # degrees of variation
                comparison=MetricComparison.ABS_GREATER,
                severity=Severity.HIGH,
                min_frames=10,
                frame_percentage=0.15
            ),
            
            # === JOINT ANGLES ===
            
            CoachingRule(
                name="elbow_not_locked",
                title="Elbows Not Locked",
                description="Your elbows are significantly bent during presentation. "
                            "While a slight bend is natural, excessive bending reduces control and increases felt recoil. "
                            "Work on achieving near-full extension (160-175 degrees) for better recoil management.",
                metric="L_elbow_angle",
                threshold=140.0,  # degrees
                comparison=MetricComparison.LESS,
                severity=Severity.MEDIUM,
                min_frames=15,
                frame_percentage=0.20
            ),
            
            # === CENTER OF MASS ===
            
            CoachingRule(
                name="com_drift",
                title="Center of Mass Drift",
                description="Your center of mass is shifting significantly during the drill. "
                            "Excessive movement indicates instability or weight transfer issues. "
                            "Focus on maintaining a stable platform and smooth weight distribution.",
                metric="com_velocity",  # Magnitude of COM movement
                threshold=5.0,  # pixels per frame (normalized)
                comparison=MetricComparison.GREATER,
                severity=Severity.LOW,
                min_frames=20,
                frame_percentage=0.10
            ),
            
            # === FIREARM HANDLING ===
            
            CoachingRule(
                name="muzzle_elevation_excessive",
                title="Excessive Muzzle Elevation",
                description="Your muzzle is frequently elevated too high during presentation. "
                            "While some elevation during draw is natural, excessive upward pointing "
                            "can slow your presentation and increase the risk of flagging. "
                            "Practice a more direct path from holster to target. "
                            "Ideal elevation at full extension should be 0-5 degrees.",
                metric="L_muzzle_elevation",  # Using left side as primary
                threshold=25.0,  # degrees above horizontal
                comparison=MetricComparison.GREATER,
                severity=Severity.MEDIUM,
                min_frames=15,
                frame_percentage=0.20
            ),
            
            CoachingRule(
                name="muzzle_depression_excessive",
                title="Excessive Muzzle Depression",
                description="Your muzzle is frequently depressed too low during presentation. "
                            "While safety requires downward muzzle during draw, excessive depression "
                            "can indicate an inefficient draw stroke or hesitation. "
                            "Work on a smooth, confident presentation with minimal vertical deviation.",
                metric="L_muzzle_elevation",  # Using left side as primary
                threshold=-15.0,  # degrees below horizontal
                comparison=MetricComparison.LESS,
                severity=Severity.LOW,
                min_frames=15,
                frame_percentage=0.15
            ),
            
            CoachingRule(
                name="firearm_not_detected",
                title="⚠️ Firearm Not Detected",
                description="The firearm was not detected in a significant portion of frames. "
                            "This may affect the accuracy of muzzle direction and firearm-specific metrics. "
                            "Possible causes: poor lighting, excessive motion blur, obstructed camera view, "
                            "or firearm color blending with background. "
                            "Consider: better lighting, slower movements for analysis, or camera repositioning.",
                metric="firearm_detected",
                threshold=0.5,  # Less than 50% detection is concerning
                comparison=MetricComparison.LESS,
                severity=Severity.MEDIUM,
                min_frames=50,
                frame_percentage=0.50  # If >50% of frames have no detection
            ),
        ]
    
    def add_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived metrics needed for rule evaluation.
        
        Some rules require metrics that aren't directly in the CSV
        but can be calculated from existing columns.
        
        Args:
            df: DataFrame with raw analytics
            
        Returns:
            DataFrame with additional derived columns
        """
        df = df.copy()
        
        # Arm extension difference (asymmetry)
        if 'L_arm_extension' in df.columns and 'R_arm_extension' in df.columns:
            df['arm_extension_diff'] = np.abs(df['L_arm_extension'] - df['R_arm_extension'])
        
        # Center of mass velocity (frame-to-frame movement)
        if 'center_of_mass_x' in df.columns and 'center_of_mass_y' in df.columns:
            com_x_diff = df['center_of_mass_x'].diff().fillna(0)
            com_y_diff = df['center_of_mass_y'].diff().fillna(0)
            df['com_velocity'] = np.sqrt(com_x_diff**2 + com_y_diff**2)
        
        return df
    
    def evaluate_all_rules(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Evaluate all rules against the provided metrics.
        
        Args:
            df: DataFrame with analytics metrics (from analytics.csv)
            
        Returns:
            List of violation dictionaries for rules that triggered
        """
        # Add derived metrics
        df = self.add_derived_metrics(df)
        
        violations = []
        for rule in self.rules:
            result = rule.evaluate(df)
            if result is not None:
                violations.append(result)
        
        # Sort by severity, then by percentage
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3
        }
        violations.sort(key=lambda x: (severity_order[x['severity']], -x['percentage']))
        
        return violations
    
    def generate_report(
        self, 
        df: pd.DataFrame, 
        output_format: str = "text"
    ) -> str:
        """
        Generate a comprehensive coaching report.
        
        Args:
            df: DataFrame with analytics metrics
            output_format: "text", "markdown", or "html"
            
        Returns:
            Formatted coaching report string
        """
        violations = self.evaluate_all_rules(df)
        
        if output_format == "text":
            return self._generate_text_report(df, violations)
        elif output_format == "markdown":
            return self._generate_markdown_report(df, violations)
        elif output_format == "html":
            return self._generate_html_report(df, violations)
        else:
            raise ValueError(f"Unknown format: {output_format}")
    
    def _generate_text_report(self, df: pd.DataFrame, violations: List[Dict]) -> str:
        """Generate plain text report."""
        lines = []
        lines.append("=" * 80)
        lines.append("SMART COACH - COACHING INSIGHTS REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        lines.append(f"Video: {len(df)} frames analyzed")
        lines.append(f"Issues Found: {len(violations)}")
        lines.append("")
        
        if len(violations) == 0:
            lines.append("✓ No significant issues detected!")
            lines.append("  Keep up the excellent form and continue practicing fundamentals.")
        else:
            # Group by severity
            critical = [v for v in violations if v['severity'] == Severity.CRITICAL]
            high = [v for v in violations if v['severity'] == Severity.HIGH]
            medium = [v for v in violations if v['severity'] == Severity.MEDIUM]
            low = [v for v in violations if v['severity'] == Severity.LOW]
            
            # CRITICAL SAFETY ALERTS - Show prominently first
            if critical:
                lines.append("🚨" * 40)
                lines.append("⚠️  CRITICAL SAFETY ISSUES DETECTED: {len(critical)}")
                lines.append("🚨" * 40)
                lines.append("")
                lines.append("IMMEDIATE ACTION REQUIRED!")
                lines.append("These issues represent serious safety violations that must be addressed")
                lines.append("before continuing live-fire training. Review with a certified instructor.")
                lines.append("")
                
                for v in critical:
                    lines.append(f"🔴 {v['title']}")
                    lines.append(f"   Occurred in {v['percentage']:.1f}% of frames ({v['num_frames']} frames)")
                    lines.append(f"   Example frames: {v['example_frames'][:5]}")
                    lines.append("")
                
                lines.append("🚨" * 40)
                lines.append("")
            
            # Standard priority summary
            if high:
                lines.append(f"🔴 HIGH PRIORITY: {len(high)}")
            if medium:
                lines.append(f"🟡 MEDIUM PRIORITY: {len(medium)}")
            if low:
                lines.append(f"🟢 LOW PRIORITY: {len(low)}")
            lines.append("")
            
            # Detail each violation
            for i, v in enumerate(violations, 1):
                severity_icon = {
                    Severity.CRITICAL: "⚠️ ",
                    Severity.HIGH: "🔴",
                    Severity.MEDIUM: "🟡",
                    Severity.LOW: "🟢"
                }[v['severity']]
                
                lines.append("-" * 80)
                lines.append(f"{i}. {severity_icon} {v['title']}")
                lines.append("")
                lines.append(f"   {v['description']}")
                lines.append("")
                lines.append(f"   Frequency: {v['percentage']:.1f}% of frames ({v['num_frames']}/{v['total_frames']})")
                lines.append(f"   Example frames: {v['example_frames'][:3]}")
                lines.append("")
        
        lines.append("=" * 80)
        lines.append("NEXT STEPS:")
        lines.append("")
        
        # Customize next steps based on critical issues
        if any(v['severity'] == Severity.CRITICAL for v in violations):
            lines.append("⚠️  CRITICAL: Address all safety violations before live-fire training")
            lines.append("1. Review flagged frames with a certified firearms instructor")
            lines.append("2. Practice draw and presentation with empty firearm")
            lines.append("3. Record dry-fire session to verify safety improvements")
            lines.append("4. Only return to live-fire after instructor approval")
        else:
            lines.append("1. Review flagged frames in the annotated video output")
            lines.append("2. Focus on the highest priority issues first")
            lines.append("3. Practice drills targeting specific weaknesses")
            lines.append("4. Record follow-up session to track improvement")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _generate_markdown_report(self, df: pd.DataFrame, violations: List[Dict]) -> str:
        """Generate Markdown report."""
        lines = []
        lines.append("# Smart Coach - Coaching Insights Report")
        lines.append("")
        lines.append(f"**Video Analysis:** {len(df)} frames")
        lines.append(f"**Issues Found:** {len(violations)}")
        lines.append("")
        
        if len(violations) == 0:
            lines.append("✅ **No significant issues detected!**")
            lines.append("")
            lines.append("Keep up the excellent form and continue practicing fundamentals.")
        else:
            lines.append("## Issues Summary")
            lines.append("")
            
            # Group by severity
            for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
                severity_violations = [v for v in violations if v['severity'] == severity]
                if severity_violations:
                    icon = {"critical": "⚠️", "high": "🔴", "medium": "🟡", "low": "🟢"}[severity.value]
                    lines.append(f"- {icon} **{severity.value.upper()}**: {len(severity_violations)} issues")
            
            lines.append("")
            lines.append("## Detailed Feedback")
            lines.append("")
            
            for i, v in enumerate(violations, 1):
                severity_icon = {
                    Severity.CRITICAL: "⚠️",
                    Severity.HIGH: "🔴",
                    Severity.MEDIUM: "🟡",
                    Severity.LOW: "🟢"
                }[v['severity']]
                
                lines.append(f"### {i}. {severity_icon} {v['title']}")
                lines.append("")
                lines.append(v['description'])
                lines.append("")
                lines.append(f"**Frequency:** {v['percentage']:.1f}% of frames ({v['num_frames']}/{v['total_frames']})")
                lines.append("")
                lines.append(f"**Example Frames:** {', '.join(map(str, v['example_frames'][:5]))}")
                lines.append("")
        
        lines.append("---")
        lines.append("")
        lines.append("## Next Steps")
        lines.append("")
        lines.append("1. Review flagged frames in the annotated video output")
        lines.append("2. Focus on the highest priority issues first")
        lines.append("3. Practice drills targeting specific weaknesses")
        lines.append("4. Record follow-up session to track improvement")
        
        return "\n".join(lines)
    
    def _generate_html_report(self, df: pd.DataFrame, violations: List[Dict]) -> str:
        """Generate HTML report with styling."""
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html>")
        html.append("<head>")
        html.append("<title>Smart Coach - Coaching Report</title>")
        html.append("<style>")
        html.append("""
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }
            h2 { color: #555; margin-top: 30px; }
            .summary { background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .safety-alert { background: #ffebee; border: 3px solid #f44336; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .safety-alert h2 { color: #c62828; margin-top: 0; }
            .safety-alert-item { background: white; padding: 10px; margin: 10px 0; border-left: 4px solid #f44336; }
            .issue { border-left: 4px solid #ddd; padding: 15px; margin: 20px 0; background: #fafafa; }
            .critical { border-left-color: #f44336; background: #ffebee; }
            .high { border-left-color: #ff9800; background: #fff3e0; }
            .medium { border-left-color: #ffc107; background: #fffde7; }
            .low { border-left-color: #4CAF50; background: #f1f8e9; }
            .severity-badge { display: inline-block; padding: 5px 10px; border-radius: 3px; font-size: 12px; font-weight: bold; margin-right: 10px; }
            .badge-critical { background: #f44336; color: white; }
            .badge-high { background: #ff9800; color: white; }
            .badge-medium { background: #ffc107; color: black; }
            .badge-low { background: #4CAF50; color: white; }
            .stats { color: #666; font-size: 14px; margin-top: 10px; }
            .next-steps { background: #e3f2fd; padding: 20px; border-radius: 5px; margin-top: 30px; }
            .critical-next-steps { background: #ffebee; padding: 20px; border-radius: 5px; margin-top: 30px; border: 2px solid #f44336; }
            .no-issues { text-align: center; padding: 40px; color: #4CAF50; font-size: 18px; }
        """)
        html.append("</style>")
        html.append("</head>")
        html.append("<body>")
        html.append("<div class='container'>")
        
        html.append("<h1>🎯 Smart Coach - Coaching Insights Report</h1>")
        
        html.append("<div class='summary'>")
        html.append(f"<strong>Video Analysis:</strong> {len(df)} frames<br>")
        html.append(f"<strong>Issues Found:</strong> {len(violations)}")
        html.append("</div>")
        
        if len(violations) == 0:
            html.append("<div class='no-issues'>")
            html.append("✅ <strong>No significant issues detected!</strong><br><br>")
            html.append("Keep up the excellent form and continue practicing fundamentals.")
            html.append("</div>")
        else:
            # Critical safety alerts section
            critical_violations = [v for v in violations if v['severity'] == Severity.CRITICAL]
            if critical_violations:
                html.append("<div class='safety-alert'>")
                html.append("<h2>🚨 CRITICAL SAFETY ALERTS</h2>")
                html.append("<p><strong>IMMEDIATE ACTION REQUIRED!</strong></p>")
                html.append("<p>The following critical safety violations were detected. "
                           "These issues must be addressed before continuing live-fire training. "
                           "Review with a certified firearms instructor.</p>")
                
                for v in critical_violations:
                    html.append("<div class='safety-alert-item'>")
                    html.append(f"<strong>⚠️ {v['title']}</strong><br>")
                    html.append(f"Occurred in {v['percentage']:.1f}% of frames ({v['num_frames']} frames)<br>")
                    html.append(f"Example frames: {', '.join(map(str, v['example_frames'][:5]))}")
                    html.append("</div>")
                
                html.append("</div>")
            
            html.append("<h2>All Issues Detected</h2>")
            
            for v in violations:
                severity_class = v['severity'].value
                badge_class = f"badge-{severity_class}"
                
                html.append(f"<div class='issue {severity_class}'>")
                html.append(f"<span class='severity-badge {badge_class}'>{v['severity'].value.upper()}</span>")
                html.append(f"<strong>{v['title']}</strong>")
                html.append(f"<p>{v['description']}</p>")
                html.append(f"<div class='stats'>")
                html.append(f"Frequency: {v['percentage']:.1f}% of frames ({v['num_frames']}/{v['total_frames']})<br>")
                html.append(f"Example frames: {', '.join(map(str, v['example_frames'][:5]))}")
                html.append("</div>")
                html.append("</div>")
        
        # Customize next steps based on critical issues
        if any(v['severity'] == Severity.CRITICAL for v in violations):
            html.append("<div class='critical-next-steps'>")
            html.append("<h2>⚠️ Critical Next Steps</h2>")
            html.append("<ol>")
            html.append("<li><strong>STOP live-fire training immediately</strong></li>")
            html.append("<li>Review flagged frames with a certified firearms instructor</li>")
            html.append("<li>Practice draw and presentation with empty firearm</li>")
            html.append("<li>Record dry-fire session to verify safety improvements</li>")
            html.append("<li>Only return to live-fire after instructor approval</li>")
            html.append("</ol>")
            html.append("</div>")
        else:
            html.append("<div class='next-steps'>")
            html.append("<h2>📋 Next Steps</h2>")
            html.append("<ol>")
            html.append("<li>Review flagged frames in the annotated video output</li>")
            html.append("<li>Focus on the highest priority issues first</li>")
            html.append("<li>Practice drills targeting specific weaknesses</li>")
            html.append("<li>Record follow-up session to track improvement</li>")
            html.append("</ol>")
            html.append("</div>")
        
        html.append("</div>")
        html.append("</body>")
        html.append("</html>")
        
        return "\n".join(html)
