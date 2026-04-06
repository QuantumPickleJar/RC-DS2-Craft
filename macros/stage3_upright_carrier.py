# =============================================================================
# RC CORNER MODULE - STAGE 3: UPRIGHT / CARRIER BODY - LEFT-HAND FRONT (v0.1)
# =============================================================================
# Creates the upright (carrier body) for the left-hand front corner.
# Run this in FreeCAD (1.0+) via the Macro Editor or Python Console.
#
# Coordinate system (matches skeleton macro):
#   X = longitudinal (rear -> front)
#   Y = lateral (positive = right, negative = left)
#   Z = vertical (up)
#
# Spatial relationships to Stage 2 arm:
#   - The arm's carrier socket boss (Ø16 mm, Z-axis, at wheel axis) IS the
#     kingpin post.  The upright slides over it via a Ø16.3 mm bore and steers
#     by rotating around this boss.  No separate kingpin required.
#   - An M5 bolt passes through the arm boss bore (Ø5.25 mm) and captures the
#     upright axially; the upright rotates freely around the bolt shank.
#   - The wheel hub rotates on the outboard spindle (Y-axis) independently of
#     the steering rotation — two separate revolute joints in one assembly.
#
# Upright sub-features:
#   1. Carrier body block   — main structural volume, spans kingpin bore in Z
#   2. Kingpin bore         — Ø16.3 mm in Z, full block height; bushing seats
#                             at top and bottom (Ø16.8 mm × 3 mm each)
#   3. Outboard spindle     — Ø28 mm protrusion in –Y for wheel hub
#   4. Hub bore (Y-axis)    — Ø22 mm, full through incl. spindle (half-shaft)
#   5. Bearing seat recess  — Ø32 mm × 8 mm at spindle tip (outboard end)
#   6. Sealing land step    — Ø25 mm × 3 mm at inboard face (lip seal)
#   7. Steering arm tab     — diagonal slab from block to tie-rod pickup
#   8. Tie-rod pickup boss  — Ø10 mm × 14 mm cylinder, M4 bore in Z
#
# Placeholder notes:
#   - Kingpin bushing seats accept Ø16.8 mm × Ø16.3 mm × 3 mm PTFE/nylon
#     rings; a tighter printed bore is possible for direct plastic-on-plastic.
#   - Bearing seat accepts a 32 × 22 × 7 mm single-row deep-groove ball
#     bearing (e.g. 6004 or 61904); verify availability before printing.
#   - Steering arm length sets the mechanical advantage for the servo; adjust
#     TIE_ROD_X offset and servo arm length together.
#   - Brake disc / drum geometry is Stage 4.
# =============================================================================

import math

try:
    import FreeCAD as App
    import Part
except Exception:
    raise RuntimeError("This script must be run inside FreeCAD.")

# =============================================================================
# VEHICLE PARAMETERS  (from RC_Chassis_Skeleton_v02 macro)
# =============================================================================

WHEELBASE = 330.0               # mm
TRACK_WIDTH = 286.0             # mm
TIRE_OUTER_DIAMETER = 150.0     # mm
TIRE_WIDTH = 62.0               # mm

CARRIER_MOUNT_Z = 94.0          # mm, Z of chassis-side mount plane
LOWEST_HARDPOINT_Z = 64.0       # mm, minimum Z of any carrier component

AXLE_X = WHEELBASE / 2.0                                    # 165.0 mm (front axle)
AXLE_SLOT_SPACING_Y = 72.0                                  # mm

WHEEL_AXIS_X = AXLE_X                                       # 165.0 mm
WHEEL_AXIS_Y = -(TRACK_WIDTH / 2.0)                        # -143.0 mm
WHEEL_AXIS_Z = TIRE_OUTER_DIAMETER / 2.0                   # 75.0 mm

# =============================================================================
# CARRIER BODY BLOCK
# =============================================================================

CARRIER_BLOCK_X = 42.0          # mm in X (fore-aft span)
CARRIER_BLOCK_Y = 30.0          # mm in Y (inboard–outboard)
CARRIER_BLOCK_Z = 52.0          # mm in Z (vertical span)

# Derived face positions
CARRIER_INBOARD_Y  = WHEEL_AXIS_Y + CARRIER_BLOCK_Y / 2.0  # -128.0 mm (toward chassis)
CARRIER_OUTBOARD_Y = WHEEL_AXIS_Y - CARRIER_BLOCK_Y / 2.0  # -158.0 mm (toward wheel)
CARRIER_TOP_Z      = WHEEL_AXIS_Z + CARRIER_BLOCK_Z / 2.0  # 101.0 mm
CARRIER_BOT_Z      = WHEEL_AXIS_Z - CARRIER_BLOCK_Z / 2.0  #  49.0 mm

# =============================================================================
# KINGPIN BORE  (Z-axis)
# =============================================================================

# The arm's socket boss is Ø16 mm.  0.15 mm radial clearance on each side.
KINGPIN_BORE_D = 16.3

# PTFE/nylon bushing seats at top and bottom of the kingpin bore.
# These are slightly larger-diameter, shallow pockets that accept a thin ring
# to reduce wear at the rotation contact surfaces.
KINGPIN_BUSHING_D     = 16.8    # mm, bushing seat bore
KINGPIN_BUSHING_DEPTH =  3.0    # mm, depth at each face

# =============================================================================
# HUB BORE  (Y-axis)
# =============================================================================

HUB_BORE_D           = 22.0    # mm, half-shaft clearance bore

# =============================================================================
# OUTBOARD SPINDLE PROTRUSION
# =============================================================================

SPINDLE_OD           = 28.0    # mm
SPINDLE_LENGTH       = 14.0    # mm, extends in -Y from outboard carrier face
SPINDLE_TIP_Y        = CARRIER_OUTBOARD_Y - SPINDLE_LENGTH   # -172.0 mm

# Bearing seat at spindle tip (outboard end).
# A 32 × 22 × 7 mm deep-groove ball bearing (e.g. 6004) fits here.
HUB_BEARING_OD       = 32.0    # mm, bearing outer seat diameter
HUB_BEARING_DEPTH    =  8.0    # mm, recess depth from spindle tip

# =============================================================================
# INBOARD SEALING LAND  (Y-axis pocket on inboard face)
# =============================================================================

SEAL_BORE_D          = 25.0    # mm, stepped bore for lip seal OD
SEAL_BORE_DEPTH      =  3.0    # mm, depth from inboard face into body

# =============================================================================
# STEERING ARM  (diagonal slab, forward + inboard + upward)
# =============================================================================

# Tie-rod pickup coordinates (match Stage 1 LCS_TieRodPickup)
TIE_ROD_X = WHEEL_AXIS_X + 25.0    # 190.0 mm (forward of wheel axis)
TIE_ROD_Y = WHEEL_AXIS_Y + 15.0    # -128.0 mm (= CARRIER_INBOARD_Y)
TIE_ROD_Z = WHEEL_AXIS_Z + 20.0    #  95.0 mm (above wheel axis)

# Arm slab extents  — wraps from the carrier body to just past the pickup
STEER_ARM_X0     = WHEEL_AXIS_X - 6.0                      # 159.0 mm
STEER_ARM_X1     = TIE_ROD_X    + 6.0                      # 196.0 mm
STEER_ARM_Z0     = WHEEL_AXIS_Z - 5.0                      #  70.0 mm
STEER_ARM_Z1     = TIE_ROD_Z   + 3.0                       #  98.0 mm
STEER_ARM_THICK  = 8.0                                      # mm in Y
STEER_ARM_Y0     = TIE_ROD_Y   - STEER_ARM_THICK / 2.0    # -132.0 mm
STEER_ARM_Y1     = TIE_ROD_Y   + STEER_ARM_THICK / 2.0    # -124.0 mm

# Tie-rod pickup boss (Z-axis cylinder straddling TIE_ROD_Z)
TIE_ROD_BOSS_OD      = 10.0    # mm
TIE_ROD_BOSS_HEIGHT  = 14.0    # mm in Z
TIE_ROD_BOSS_Z0      = TIE_ROD_Z - TIE_ROD_BOSS_HEIGHT / 2.0   # 88.0 mm
TIE_ROD_BORE_D       =  4.4    # mm, M4 clevis pin clearance in Z

# =============================================================================
# DOCUMENT SETUP
# =============================================================================

DOC_NAME = "Corner_Upright_LHF_v01"
REPLACE_EXISTING = True

# =============================================================================
# HELPERS
# =============================================================================


def get_or_create_document(doc_name):
    existing = App.listDocuments().get(doc_name)
    if existing:
        if REPLACE_EXISTING:
            App.closeDocument(doc_name)
            return App.newDocument(doc_name)
        return existing
    return App.newDocument(doc_name)


def add_group(doc, name, parent=None):
    grp = doc.addObject("App::DocumentObjectGroup", name)
    if parent is not None:
        parent.addObject(grp)
    return grp


def add_shape_object(doc, name, shape, parent=None):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    if parent is not None:
        parent.addObject(obj)
    return obj


def fuse_shapes(shapes):
    if not shapes:
        raise ValueError("fuse_shapes() requires at least one shape.")
    result = shapes[0]
    for shp in shapes[1:]:
        result = result.fuse(shp)
    return result.removeSplitter()


def cut_shapes(base, cutters):
    result = base
    for cutter in cutters:
        result = result.cut(cutter)
    return result.removeSplitter()


def make_box(x_len, y_len, z_len, x0, y0, z0):
    return Part.makeBox(x_len, y_len, z_len, App.Vector(x0, y0, z0))


def make_centered_box(x_len, y_len, z_len, cx, cy, cz):
    return make_box(
        x_len, y_len, z_len,
        cx - x_len / 2.0, cy - y_len / 2.0, cz - z_len / 2.0,
    )


def make_cyl_y(radius, length, x, y0, z):
    """Cylinder with its axis along +Y, starting at y0."""
    return Part.makeCylinder(radius, length, App.Vector(x, y0, z), App.Vector(0, 1, 0))


def make_cyl_z(radius, length, x, y, z0):
    """Cylinder with its axis along +Z, starting at z0."""
    return Part.makeCylinder(radius, length, App.Vector(x, y, z0), App.Vector(0, 0, 1))


# =============================================================================
# GEOMETRY BUILDERS
# =============================================================================


def build_carrier_block():
    """Main structural block centred on the wheel axis."""
    return make_centered_box(
        CARRIER_BLOCK_X, CARRIER_BLOCK_Y, CARRIER_BLOCK_Z,
        WHEEL_AXIS_X, WHEEL_AXIS_Y, WHEEL_AXIS_Z,
    )


def build_spindle():
    """Outboard hub spindle protrusion (Y-axis cylinder).

    Protrudes from the outboard carrier face in the –Y direction.
    The wheel hub slides over this spindle; the bearing seat at the tip
    locates the hub bearing.
    """
    return make_cyl_y(
        SPINDLE_OD / 2.0, SPINDLE_LENGTH,
        WHEEL_AXIS_X, SPINDLE_TIP_Y, WHEEL_AXIS_Z,
    )


def build_steering_arm_raw():
    """Steering arm slab + tie-rod pickup boss (before bore subtraction).

    The slab is a rectangular sweep from the inboard carrier face out to the
    tie-rod pickup.  The boss is a cylinder straddling TIE_ROD_Z at TIE_ROD_X.
    """
    slab = make_box(
        STEER_ARM_X1 - STEER_ARM_X0,
        STEER_ARM_Y1 - STEER_ARM_Y0,
        STEER_ARM_Z1 - STEER_ARM_Z0,
        STEER_ARM_X0, STEER_ARM_Y0, STEER_ARM_Z0,
    )
    boss = make_cyl_z(
        TIE_ROD_BOSS_OD / 2.0, TIE_ROD_BOSS_HEIGHT,
        TIE_ROD_X, TIE_ROD_Y, TIE_ROD_BOSS_Z0,
    )
    return fuse_shapes([slab, boss])


def build_upright_solid():
    """Build the complete upright solid: fuse all positives, subtract all bores.

    Bore subtraction order (largest-diameter first to minimise Boolean complexity):
      1.  Hub bore  Ø22 mm in Y  —  full through incl. spindle
      2.  Bearing seat  Ø32 mm × 8 mm  —  recess at spindle tip
      3.  Kingpin bore  Ø16.3 mm in Z  —  full block height
      4.  Kingpin bushing seats  Ø16.8 mm × 3 mm  —  top and bottom faces
      5.  Seal step  Ø25 mm × 3 mm  —  pocket at inboard face
      6.  Tie-rod bore  Ø4.4 mm in Z  —  through pickup boss
    """
    # -------- POSITIVES --------
    block    = build_carrier_block()
    spindle  = build_spindle()
    steer    = build_steering_arm_raw()
    upright  = fuse_shapes([block, spindle, steer])

    # -------- NEGATIVES --------
    negatives = []

    # 1. Hub bore in Y (full span: spindle tip → inboard face + overcuts)
    hub_bore_len = CARRIER_BLOCK_Y + SPINDLE_LENGTH + 2.0   # 46 mm
    negatives.append(make_cyl_y(
        HUB_BORE_D / 2.0, hub_bore_len,
        WHEEL_AXIS_X, SPINDLE_TIP_Y - 1.0, WHEEL_AXIS_Z,
    ))

    # 2. Bearing seat recess at spindle tip (outboard end, Ø32 × 8 mm)
    negatives.append(make_cyl_y(
        HUB_BEARING_OD / 2.0, HUB_BEARING_DEPTH + 0.01,
        WHEEL_AXIS_X, SPINDLE_TIP_Y - 0.01, WHEEL_AXIS_Z,
    ))

    # 3. Kingpin bore in Z (full block height + overcuts at both ends)
    negatives.append(make_cyl_z(
        KINGPIN_BORE_D / 2.0, CARRIER_BLOCK_Z + 2.0,
        WHEEL_AXIS_X, WHEEL_AXIS_Y, CARRIER_BOT_Z - 1.0,
    ))

    # 4a. Kingpin bushing seat at top face (3 mm pocket, Ø16.8 mm)
    negatives.append(make_cyl_z(
        KINGPIN_BUSHING_D / 2.0, KINGPIN_BUSHING_DEPTH + 0.01,
        WHEEL_AXIS_X, WHEEL_AXIS_Y, CARRIER_TOP_Z - KINGPIN_BUSHING_DEPTH,
    ))

    # 4b. Kingpin bushing seat at bottom face (3 mm pocket, Ø16.8 mm)
    negatives.append(make_cyl_z(
        KINGPIN_BUSHING_D / 2.0, KINGPIN_BUSHING_DEPTH + 0.01,
        WHEEL_AXIS_X, WHEEL_AXIS_Y, CARRIER_BOT_Z - 0.01,
    ))

    # 5. Sealing land step at inboard face (Ø25 × 3 mm pocket)
    #    Pocket runs from CARRIER_INBOARD_Y – 3 mm to CARRIER_INBOARD_Y.
    negatives.append(make_cyl_y(
        SEAL_BORE_D / 2.0, SEAL_BORE_DEPTH + 0.01,
        WHEEL_AXIS_X, CARRIER_INBOARD_Y - SEAL_BORE_DEPTH - 0.01, WHEEL_AXIS_Z,
    ))

    # 6. Tie-rod bore (Ø4.4 mm in Z, through pickup boss)
    negatives.append(make_cyl_z(
        TIE_ROD_BORE_D / 2.0, TIE_ROD_BOSS_HEIGHT + 2.0,
        TIE_ROD_X, TIE_ROD_Y, TIE_ROD_BOSS_Z0 - 1.0,
    ))

    return cut_shapes(upright, negatives)


# =============================================================================
# MAIN
# =============================================================================


def main():
    doc = get_or_create_document(DOC_NAME)

    upright_group = add_group(doc, "Upright_LHF")
    refs_group    = add_group(doc, "References")

    App.Console.PrintMessage("Building carrier block, spindle, steering arm...\n")
    App.Console.PrintMessage("  Fusing positives...\n")
    App.Console.PrintMessage("  Cutting bores (hub Y, bearing seat, kingpin Z,\n")
    App.Console.PrintMessage("                 bushing seats, seal step, tie-rod)...\n")

    upright_solid = build_upright_solid()

    upright_obj = add_shape_object(doc, "Upright_LHF_v01", upright_solid, upright_group)

    # Reference marker: arm socket entry point (top of kingpin bore)
    arm_socket_marker = make_cyl_z(
        1.5, 4.0, WHEEL_AXIS_X, WHEEL_AXIS_Y, CARRIER_TOP_Z + 1.0,
    )
    marker_obj = add_shape_object(
        doc, "REF_ArmSocketEntry", arm_socket_marker, refs_group,
    )

    # Apply view settings
    try:
        import FreeCADGui  # noqa: F401
        upright_obj.ViewObject.ShapeColor  = (0.20, 0.50, 0.80)  # steel blue
        upright_obj.ViewObject.Transparency = 0
        marker_obj.ViewObject.ShapeColor   = (0.90, 0.20, 0.20)  # red reference
        marker_obj.ViewObject.Transparency = 20
    except Exception:
        pass

    doc.recompute()

    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------
    seal_shoulder = (SEAL_BORE_D - HUB_BORE_D) / 2.0
    bearing_wall  = (SPINDLE_OD - HUB_BEARING_OD) / 2.0
    steer_arm_x_reach = TIE_ROD_X - WHEEL_AXIS_X
    steer_arm_z_rise  = TIE_ROD_Z - WHEEL_AXIS_Z
    steer_arm_y_inset = TIE_ROD_Y - WHEEL_AXIS_Y

    App.Console.PrintMessage("\n=== Upright LHF v0.1 - Stage 3 Summary ===\n")
    App.Console.PrintMessage(f"Document        : {doc.Name}\n")
    App.Console.PrintMessage(f"\nCarrier block   : {CARRIER_BLOCK_X:.0f} x {CARRIER_BLOCK_Y:.0f} x {CARRIER_BLOCK_Z:.0f} mm\n")
    App.Console.PrintMessage(f"  Centre        : X={WHEEL_AXIS_X:.1f}  Y={WHEEL_AXIS_Y:.1f}  Z={WHEEL_AXIS_Z:.1f}\n")
    App.Console.PrintMessage(f"  Inboard Y     : {CARRIER_INBOARD_Y:.1f} mm\n")
    App.Console.PrintMessage(f"  Outboard Y    : {CARRIER_OUTBOARD_Y:.1f} mm\n")
    App.Console.PrintMessage(f"  Top Z         : {CARRIER_TOP_Z:.1f} mm\n")
    App.Console.PrintMessage(f"  Bottom Z      : {CARRIER_BOT_Z:.1f} mm\n")
    App.Console.PrintMessage(f"\nKingpin bore    : Ø{KINGPIN_BORE_D:.1f} mm  (arm boss Ø16.0 mm + 0.15 mm clearance)\n")
    App.Console.PrintMessage(f"  Bushing seats : Ø{KINGPIN_BUSHING_D:.1f} mm x {KINGPIN_BUSHING_DEPTH:.0f} mm  at top and bottom\n")
    App.Console.PrintMessage(f"\nHub bore (Y)    : Ø{HUB_BORE_D:.1f} mm\n")
    App.Console.PrintMessage(f"  Spindle OD    : Ø{SPINDLE_OD:.1f} mm  x {SPINDLE_LENGTH:.0f} mm  (tip Y={SPINDLE_TIP_Y:.1f} mm)\n")
    App.Console.PrintMessage(f"  Bearing seat  : Ø{HUB_BEARING_OD:.1f} mm x {HUB_BEARING_DEPTH:.0f} mm  (wall remaining = {bearing_wall:.1f} mm)\n")
    App.Console.PrintMessage(f"  Seal step     : Ø{SEAL_BORE_D:.1f} mm x {SEAL_BORE_DEPTH:.0f} mm  (shoulder = {seal_shoulder:.1f} mm)\n")
    App.Console.PrintMessage(f"\nSteering arm    : reach +{steer_arm_x_reach:.0f} mm X  +{steer_arm_y_inset:.0f} mm Y  +{steer_arm_z_rise:.0f} mm Z\n")
    App.Console.PrintMessage(f"  Pickup boss   : Ø{TIE_ROD_BOSS_OD:.0f} mm x {TIE_ROD_BOSS_HEIGHT:.0f} mm  at ({TIE_ROD_X:.0f}, {TIE_ROD_Y:.0f}, {TIE_ROD_Z:.0f})\n")
    App.Console.PrintMessage(f"  Pickup bore   : Ø{TIE_ROD_BORE_D:.1f} mm  (M4 clevis pin)\n")
    App.Console.PrintMessage(f"\nTire clearance check:\n")
    App.Console.PrintMessage(f"  Tire inner face Y : {WHEEL_AXIS_Y + TIRE_WIDTH / 2.0:.1f} mm\n")
    App.Console.PrintMessage(f"  Carrier inboard Y : {CARRIER_INBOARD_Y:.1f} mm\n")
    App.Console.PrintMessage(f"  Gap (must be > 0) : {CARRIER_INBOARD_Y - (WHEEL_AXIS_Y + TIRE_WIDTH / 2.0):.1f} mm\n")
    App.Console.PrintMessage(f"  Tire outer face Y : {WHEEL_AXIS_Y - TIRE_WIDTH / 2.0:.1f} mm\n")
    App.Console.PrintMessage(f"  Spindle tip Y     : {SPINDLE_TIP_Y:.1f} mm\n")
    App.Console.PrintMessage(f"  Gap (must be > 0) : {(WHEEL_AXIS_Y - TIRE_WIDTH / 2.0) - SPINDLE_TIP_Y:.1f} mm\n")
    App.Console.PrintMessage("\nStage 3 complete. Run assemble_corner_to_chassis.py to preview all parts together.\n")

    return doc, upright_obj


main()
