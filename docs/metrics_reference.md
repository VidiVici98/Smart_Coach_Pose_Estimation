# Smart Coach – Metrics Reference
##Purpose

This document defines every metric produced by the Smart Coach Pose Detection & Metrics Pipeline.

It serves as:

- A canonical reference for CSV fields

- A contract between vision extraction and downstream analytics

- A design rationale for how metrics are computed

- A guide for future expansion and versioning

- The pipeline converts raw video into frame-indexed biomechanical telemetry.

## Coordinate Systems
1. Pixel Space (Internal Only)

Raw detections initially exist in pixel coordinates:

(x_pixel, y_pixel)


These are never exported directly because they vary with:

- Camera resolution

- Camera distance

- Field of view

- Cropping

2. Body-Normalized Space (Primary Output)

All exported coordinates are normalized using shoulder width:

(x_norm, y_norm) = (x_pixel / shoulder_width, y_pixel / shoulder_width)


This makes measurements comparable across subjects and sessions.

## CSV Schema Overview

Each row represents one video frame.

- Required Fields
- Field	Description
- frame	Frame index
- shoulder_width	Pixel distance between shoulders
- muzzle_safe	Binary safety indicator
- Pose Keypoint Metrics (YOLOv8 Pose)
- Joint Indexing

YOLOv8 pose outputs 33 body landmarks.

Each joint i produces four metrics:

- kps_{i}_x
- kps_{i}_y
- kps_{i}_vx
- kps_{i}_vy

Definitions
Metric	Meaning
kps_i_x	Normalized X coordinate
kps_i_y	Normalized Y coordinate
kps_i_vx	Normalized velocity in X
kps_i_vy	Normalized velocity in Y
Velocity Calculation

Velocity is frame-to-frame displacement in normalized space:

v = position_t - position_(t-1)

## Hand Landmark Metrics (MediaPipe Hands)
Hand Sides

Each hand is tracked independently:

L = left hand

R = right hand

Landmark Indexing

MediaPipe outputs 21 landmarks per hand.

Each landmark produces:

{side}_hand_{i}_x
{side}_hand_{i}_y
{side}_hand_{i}_vx
{side}_hand_{i}_vy

Example
L_hand_8_x   # Left index fingertip X
R_hand_4_y   # Right thumb tip Y

## Trigger Pull Metrics
Fields
L_trigger_pull
R_trigger_pull

Meaning

Binary indicator of trigger movement detected via index fingertip motion.

Current Detection Logic

A trigger pull is flagged when:

index_finger_tip moves upward between frames

Limitations

This is intentionally simplistic and serves as a placeholder for future detection based on:

Finger joint angle change

Grip pose classification

Relative motion vs frame baseline

Body Occupancy Metrics
Body Mask

Derived from Mask R-CNN person segmentation.

Purpose

Used for:

Detecting muzzle sweep across body

Measuring self-intersection risk

Future hitbox reasoning

Internal Representation

Binary mask:

body_mask[y][x] ∈ {0,1}

Muzzle Orientation Metrics
Derived Fields
muzzle_safe

Orientation Vector

The system estimates muzzle direction using:

direction = wrist_position - elbow_position


This acts as a proxy for barrel direction when no gun model exists.

Muzzle Cone Geometry

A triangular cone is projected forward:

Parameter	Meaning
MUZZLE_LENGTH	Projection distance
MUZZLE_ANGLE_RAD	Spread angle
Safety Rule

A frame is unsafe if:

cone intersects body_mask

Result
muzzle_safe = 0 or 1

Derived Biomechanical Metrics (Planned / Optional)

These are not yet exported by default but are supported by available data.

Arm Extension
distance(wrist, shoulder)


Use cases:

Presentation consistency

Fatigue detection

Joint Angles
angle(elbow, shoulder, wrist)


Use cases:

Lockout consistency

Recoil control analysis

Grip Symmetry
distance(left_hand, right_hand)


Use cases:

Support-hand pressure estimation

Grip repeatability scoring

Muzzle Stability
stddev(muzzle_direction over time)


Use cases:

Shot-to-shot consistency

Tremor detection

Trigger Rhythm
Δt between trigger_pull events


Use cases:

Split time estimation

Cadence classification

Object Detection Metrics (Future Expansion)

When firearm detection is integrated:

Gun Bounding Box
gun_x1, gun_y1, gun_x2, gun_y2

Derived Gun Orientation
gun_angle

Grip Alignment Error
angle(gun_vector, wrist_vector)

Muzzle Offset
distance(gun_tip, wrist)

Metric Quality Levels

Each metric falls into one of three reliability tiers:

Tier 1 — High Confidence

Shoulder width

Hand landmark positions

Joint positions

Tier 2 — Moderate Confidence

Velocity

Joint angles

Trigger detection

Tier 3 — Heuristic

Muzzle direction

Safety inference

This classification helps downstream consumers decide how much trust to place in each signal.

Versioning Policy

Metrics evolve. Every breaking change must:

Increment a schema version

Update this document

Add migration notes

Recommended metadata field:

schema_version = "1.0.0"

Design Philosophy
Metrics Should Be:

Explainable

Deterministic

Physically meaningful

Camera-invariant

Metrics Should NOT Be:

Black-box scores

ML predictions

Interpretive judgments

Interpretation belongs downstream.

Roadmap Metrics

Planned additions:

Recoil impulse estimation

Sight alignment deviation

Head-eye-gun alignment vector

Stance width and center-of-mass

Lean angle and balance stability

Support-hand pressure proxy

Reload event detection
