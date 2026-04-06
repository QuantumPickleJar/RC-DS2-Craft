# RC Corner Module — FreeCAD Macro Pipeline

These macros are FreeCAD Python scripts that build the RC-DS2 corner module
geometry stage by stage.  Run each script in the FreeCAD Macro Editor or
Python Console in order.

All scripts share the same coordinate system as the chassis skeleton macro:

| Axis | Direction           |
|------|---------------------|
| X    | Longitudinal (rear → front) |
| Y    | Lateral (negative = left, positive = right) |
| Z    | Vertical (up)       |

All dimensions are in **millimetres**.

---

## Stages

### Stage 0 — Parameter audit (no macro)

Cross-check of the chassis skeleton v0.2 macro parameters against the corner
geometry requirements.  Findings are documented in the project issue / PR.

Key numbers carried forward:

| Parameter | Value |
|-----------|-------|
| Wheelbase | 330 mm |
| Track width | 286 mm |
| Ground clearance | 62 mm |
| Tire OD | 150 mm (radius = 75 mm) |
| Carrier mount Z (high_pivot_arm) | 94 mm |
| Front axle X | 165 mm |
| Chassis pivot Y (left arm slot) | −36 mm |

---

### Stage 1 — Corner reference frame

**Script:** `stage1_corner_reference_frame.py`
**Output document:** `Corner_WheelEnd_LH_R1`

Creates the datum reference frame for the left-hand front corner:

- `References/LocalCoordinateSystems/` — LCS markers (green cross + sphere)
  - `LCS_Corner_Interface_LH` — master anchor at carrier mount plane
  - `LCS_TieRodPickup` — steering ball joint (placeholder)
  - `LCS_ShockLower` — lower shock mount (placeholder)
  - `LCS_BumpStopArm` / `LCS_BumpStopCarrier` — bump stop contacts (placeholder)
- `References/DatumAxes/` — axis cylinders (red)
  - `Axis_CarrierPivot` — arm-to-chassis revolute joint axis (X direction)
  - `Axis_Wheel` — wheel rotation axis (Y direction)
  - `Axis_Steering` — kingpin axis (Z direction)
  - `Axis_ShaftEntry` — half-shaft entry (Y direction, inboard of wheel)
- `References/DatumPlanes/` — plane slabs (blue, 85% transparent)
  - `Plane_CornerMidplane` — XZ midplane at wheel centreline for mirroring

**How to verify corner interface position**

Select `LCS_Corner_Interface_LH` in the model tree, then check the bounding
box in **View → Panels → Properties** (or use the Python Console):

```python
obj = App.ActiveDocument.getObject("LCS_Corner_Interface_LH")
bb = obj.Shape.BoundBox
print(bb.Center)   # should be near Vector(165, -143, 94)
```

---

### Stage 2 — High-pivot arm body

**Script:** `stage2_high_pivot_arm.py`
**Output document:** `Corner_HighPivotArm_LHF_v01`

Creates the structural arm that connects the elevated chassis pivot to the
wheel carrier socket:

- `HighPivotArm_LHF/HighPivotArm_LHF_v01` — fused arm solid (amber colour)
- `References/REF_CarrierEnvelope` — carrier envelope overlay (85% transparent)

**Arm architecture**

```
          Chassis end (Z = 94 mm)           Carrier end (Z = 75 mm)
          ·· pivot rib ··                   ·· socket boss ··
X = 136  [rib]──────────────────────────────[socket]  X = 165
          ‖   <─── main spar loft ──────>   ‖
X = 158  [rib]                              Y = -143
Y = -36

Shock mount boss at mid-span  ≈ (X=153, Y=-95, Z=81)
```

Key dimensions:

| Feature | Detail |
|---------|--------|
| Arm Y span | 105 mm  (Y = −38 to Y = −143) |
| Arm Z drop | 19 mm   (Z = 94 → 75) |
| Pivot ribs | 10 × 4 × 10 mm, M4 bore Ø4.4 |
| Carrier socket | Ø16 × 22 mm boss, M5 bore Ø5.25 |
| Shock boss | Ø10 × 14 mm, M4 bore Ø4.4 |
| Bump pad | Ø14 × 4 mm disc |

**Chassis slot interface**

The two pivot ribs (4 mm wide in Y) drop vertically into the carrier mount
pad slots (4.2 mm wide in Y, 12 mm in X, 22 mm deep in Z).  Once at the
desired ride-height position the M4 pivot pins are inserted from the outboard
side in X.  The 12 mm slot length gives ≈ 2 mm of fore-aft adjustment per
side for roll-centre tuning.

---

### Stage 3 — Upright / carrier body

**Script:** `stage3_upright_carrier.py`
**Output document:** `Corner_Upright_LHF_v01`

Creates the structural upright that receives the arm's socket boss as its
kingpin and carries the wheel hub on its outboard spindle:

- `Upright_LHF/Upright_LHF_v01` — fused upright solid (steel blue)
- `References/REF_ArmSocketEntry` — red marker at top of kingpin bore

**Kingpin pivot explained**

The Stage 2 arm's Ø16 mm socket boss IS the kingpin post.  The upright slides
over it via a Ø16.3 mm bore and steers by rotating about the Z axis.  An M5
bolt passes through the arm boss bore (Ø5.25 mm) and captures the upright
axially while allowing free steering rotation.

**Upright sub-features**

| Feature | Geometry | Key dimension |
|---------|----------|---------------|
| Carrier block | Box centred at wheel axis | 42 × 30 × 52 mm |
| Kingpin bore | Ø16.3 mm Z-axis | Through full block height |
| Kingpin bushing seats | Ø16.8 mm × 3 mm | Top and bottom faces |
| Outboard spindle | Ø28 mm Y-axis protrusion | 14 mm long; tip Y = −172 |
| Hub bore | Ø22 mm Y-axis | Through block + spindle |
| Bearing seat | Ø32 mm × 8 mm recess | At spindle tip |
| Sealing step | Ø25 mm × 3 mm pocket | At inboard face (Y = −128) |
| Steering arm | Rectangular slab | X 159–196, Z 70–98, 8 mm thick |
| Tie-rod pickup boss | Ø10 mm × 14 mm | At (190, −128, 95); M4 bore |

**Bearing / hardware notes**

- Hub bearing: 32 × 22 × 7 mm single-row deep-groove (e.g. 6004 / 61904)
- Kingpin bushings: Ø16.8 × Ø16.3 × 3 mm PTFE rings, one at each face
- Tie-rod clevis: M4, matching Stage 2 shock boss bore standard
- Sealing land: 25 × 22 × 3 mm lip seal (or printed chamfer for mud use)

---

### Assembly Positioner

**Script:** `assemble_corner_to_chassis.py`
**Output document:** `RC_DS2_Assembly_Preview`

Collects the chassis skeleton and all open corner-module stage documents into
a single document so every part can be seen together in one 3D view.

**Why parts appear far apart in separate documents**

Each stage macro places shapes at their absolute global coordinates (e.g.
front-left corner at X=165, Y=−143, Z=75).  When a single-part document is
opened in isolation, FreeCAD's "Fit All" view zooms to that part's bounding
box only, making it look as though it is sitting at the origin.  Opening the
chassis skeleton alongside reveals a different bounding box — hence the
apparent distance.  The positioner copies all shapes into one document so
"Fit All" frames everything together correctly.

**How to use**

1. Run Stage 1, Stage 2, and Stage 3 macros so their documents are open in
   the same FreeCAD session.
2. (Optional) Set `REPO_ROOT` at the top of the script to the absolute path
   of your repository clone.  The script will then open the chassis skeleton
   from disk automatically.
3. Run `assemble_corner_to_chassis.py`.  The script will:
   - Open `RC_Chassis_Skeleton.FCStd` if it is not already open
   - Copy all `Part::Feature` shapes from each stage document and the skeleton
     into a new `RC_DS2_Assembly_Preview` document
   - Print a bounding-box report for every source so positions can be verified

**Expected bounding boxes (LHF corner)**

```
Chassis skeleton : centred near origin, X −165..+165, Y −143..+143
Stage 1 datums  : X 165..165, Y −143..−128, Z 75..101   (markers, mostly transparent)
Stage 2 arm     : X 147..165, Y −143..−38, Z 75..97   (amber)
Stage 3 upright : X 144..196, Y −172..−124, Z 49..102  (steel blue)
```

**Colour coding in the assembly**

| Colour | Source |
|--------|--------|
| Grey (25% transparent) | Chassis skeleton |
| Green (75% transparent) | Stage 1 datum references |
| Amber (solid) | Stage 2 high-pivot arm |
| Steel blue (solid) | Stage 3 upright / carrier |
| Spring green (solid) | Stage 4 shock & spring |

---

### Stage 4 — Shock absorber & coil spring

**Script:** `stage4_shock_spring.py`
**Output document:** `Corner_ShockSpring_LHF_v01`

Creates the shock absorber and coil spring geometry for the LHF corner,
connecting the Stage 2 arm lower mount to a new chassis tower upper mount.

**Shock axis**

| Point | X | Y | Z |
|-------|---|---|---|
| Lower mount (Stage 2 arm boss) | 153 | −95.5 | 80.5 |
| Upper mount (Stage 4 tower)    | 147 | −38   | 165  |
| Extended length | | | ≈ 102 mm |
| Stroke | | | 30 mm |
| Angle from vertical (YZ) | | | ≈ 34° |

**Sub-features**

| Object | Description |
|--------|-------------|
| `ShockUpperBoss` | Ø8 × 12 mm boss at tower top; M4 clevis bore |
| `ShockBody` | Ø12 mm outer tube (1.4 mm wall) from upper downward |
| `ShockRod` | Ø5.5 mm solid rod from lower upward |
| `CoilSpring` | Proper helical sweep: Ø18 OD, Ø1.8 wire, 65 mm free, 7 active coils |

**Spring rate calculation (reported in FreeCAD console)**

```
Theoretical rate (spring steel) : ~1.6 N/mm
At-wheel rate (MR = 0.71)       : ~0.8 N/mm
Vehicle mass 3 kg / corner      : 7.4 N
Estimated static sag            : ~9 mm at wheel  (tunable via SPRING_RATE / preload)
Coil bind check                 : OK — 44 mm available vs 30 mm stroke
```

**Hardware notes**

- Body and rod are dimensioned for a commercially available 1/10 scale
  aluminium shock (e.g. 80–100 mm extended length, 30 mm stroke).
- Spring wire Ø1.8 mm in spring steel; choose pre-load spacer for desired sag.
- Upper clevis pin: M4, same standard as lower mount on the arm.

---

### Tire STL Importer

**Script:** `import_tire_stl.py`

Imports `STL/rc-ds2-tire-tread.stl` into the assembly preview document and
positions it on the LHF wheel axis so it sits alongside all other parts.

**How to use**

1. Open (or run) `assemble_corner_to_chassis.py` first.
2. Run `import_tire_stl.py`.  The tire is added to `RC_DS2_Assembly_Preview`.
3. Toggle visibility with **Space** after selecting `Tire_LHF` in the model tree,
   or right-click → **Toggle visibility**.

Set `IMPORT_PODS = True` at the top of the script to also import the rim/pods
STL on the same axis.

**Positioning logic**

The STL was exported from OpenSCAD with the wheel's revolution axis along Z.
The macro rotates +90° about X (making Z → Y) and translates to the wheel axis:

```
Wheel axis centre : (165, −143, 75)
Tire bottom Z     : 0 mm  (ground plane)
Tire top Z        : 150 mm
Tire Y span       : −174 .. −112 mm
```

---

### Stage 5 — Mirroring and full-chassis assembly *(planned)*

- Mirror LHF corner to RHF (Y = 0 symmetry)
- Replicate front corners at rear (X sign flip, rear axle X = −165)
- Load into chassis skeleton document as external references

---

## Material notes

All printed parts are assumed to be PETG unless otherwise noted.

- Minimum wall thickness: 3.2 mm (2 × 1.6 mm line width)
- Minimum bore wall: 1.5 mm for M3–M5 inserts
- Beams and arms: rectilinear infill ≥ 40 % for stiffness
- Pivot bores should be reamed or drilled after printing for accurate fit
