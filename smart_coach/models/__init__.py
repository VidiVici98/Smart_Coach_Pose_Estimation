"""
Smart Coach Models Module

Model wrappers and utilities.
"""
from .firearm_detector import (
    FirearmDetector,
    FirearmDetection,
    fuse_firearm_and_arm_estimates,
    check_muzzle_body_intersection,
    draw_firearm_detection
)

__all__ = [
    'FirearmDetector',
    'FirearmDetection',
    'fuse_firearm_and_arm_estimates',
    'check_muzzle_body_intersection',
    'draw_firearm_detection'
]
