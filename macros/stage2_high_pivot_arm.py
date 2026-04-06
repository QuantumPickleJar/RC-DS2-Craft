# =============================================================================
# RC CORNER MODULE - STAGE 2: HIGH-PIVOT ARM - LEFT-HAND FRONT (v0.1)
# =============================================================================
# Creates the HighPivotArm suspension arm geometry for the left-hand front
# corner. Run this in FreeCAD (1.0+) via the Macro Editor or Python Console.
#
# Coordinate system (matches skeleton macro):
#   X = longitudinal (rear -> front)
#   Y = lateral (positive = right, negative = left)
#   Z = vertical (up)
#
# The arm connects:
#   Chassis pivot:   X=147 (pad centre), Y=-36 (left slot), Z=94 (mount plane)
#   Carrier socket:  X=165 (wheel axle),  Y=-143 (wheel centre), Z=75 (wheel radius)
#
# "High pivot" geometry: the chassis-side pivot is at Z=94, which is ABOVE the
# wheel axis at Z=75.  This raises the instantaneous roll centre and creates
# mild anti-dive in braking.
#
# Chassis interface detail (derived from skeleton axle_slot geometry):
#   - The carrier mount pad has two vertical adjustment slots per left corner:
#       Rear slot:  centred at X=136, Y=-36, 12 mm long in X, 4.2 mm wide in Y
#       Front slot: centred at X=158, Y=-36, 12 mm long in X, 4.2 mm wide in Y
#   - The arm has two PIVOT RIBS (10 mm × 4 mm × 10 mm each) that drop into
#     these slots from above during assembly.
#   - Each rib contains a 4.4 mm bore for an M4 pivot pin running in X.
#   - The two ribs together define the pivot axis (X direction at Z=94, Y=-36).
#   - Fore-aft roll-centre adjustment is achieved by repositioning the arm
#     within the 12 mm slot range before locking the pin.
#
# Learning note:
# Part.makeLoft() connects a series of closed Wire profiles into a solid.
# Profiles must have the same number of edges and consistent winding direction.
# Using ruled=True gives flat-faced transitions that are easier to FDM-print
# and avoids unexpected NURBS tangency at profile junctions.
#
# Placeholder / refinement notes:
#   - Pivot bore M4 nominal — confirm hardware before printing.
#   - Carrier socket bore M5 nominal — real ball-joint geometry is Stage 3.
#   - Shock mount X/Y position is at arm mid-span; adjust for motion ratio.
#   - Bump stop pad is a plain disc; rubber insert is Stage 3.
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
GROUND_CLEARANCE = 62.0         # mm
TIRE_OUTER_DIAMETER = 150.0     # mm
TIRE_WIDTH = 62.0               # mm

# High-pivot-arm carrier preset parameters
CARRIER_MOUNT_Z = 94.0          # mm, Z of chassis-side mount plane
LOWEST_HARDPOINT_Z = 64.0       # mm, minimum Z of any carrier component
CARRIER_ENV_LENGTH = 102.0      # mm, X extent of carrier envelope
CARRIER_ENV_WIDTH = 128.0       # mm, Y extent of carrier envelope
CARRIER_ENV_HEIGHT = 88.0       # mm, Z extent of carrier envelope

# Chassis mounting geometry
AXLE_X = WHEELBASE / 2.0                                    # 165.0 mm (front axle)
AXLE_MOUNT_SETBACK = 18.0                                   # mm
AXLE_PAD_CENTER_X = AXLE_X - AXLE_MOUNT_SETBACK            # 147.0 mm
AXLE_SLOT_SPACING_X = 22.0                                  # mm, fore-aft slot pitch
AXLE_SLOT_SPACING_Y = 72.0                                  # mm, lateral slot pitch
AXLE_SLOT_LENGTH = 12.0                                     # mm, slot length in X
AXLE_SLOT_WIDTH = 4.2                                       # mm, slot width in Y

# Derived chassis attachment coordinates  (LEFT-HAND corner → negative Y)
CHASSIS_PIVOT_Y = -(AXLE_SLOT_SPACING_Y / 2.0)             # -36.0 mm
CHASSIS_PIVOT_Z = CARRIER_MOUNT_Z                           # 94.0 mm
CHASSIS_SLOT_X_REAR = AXLE_PAD_CENTER_X - (AXLE_SLOT_SPACING_X / 2.0)   # 136.0 mm
CHASSIS_SLOT_X_FRONT = AXLE_PAD_CENTER_X + (AXLE_SLOT_SPACING_X / 2.0)  # 158.0 mm
CHASSIS_PIVOT_X_CENTER = AXLE_PAD_CENTER_X                 # 147.0 mm

# Wheel / carrier attachment
WHEEL_AXIS_X = AXLE_X                                       # 165.0 mm
WHEEL_AXIS_Y = -(TRACK_WIDTH / 2.0)                        # -143.0 mm
WHEEL_AXIS_Z = TIRE_OUTER_DIAMETER / 2.0                   # 75.0 mm

# =============================================================================
# ARM GEOMETRY PARAMETERS
# =============================================================================

# Main spar — loft station values
# Chassis-end profile is centred at X=AXLE_PAD_CENTER_X, just outboard of the
# rib faces (Y = CHASSIS_PIVOT_Y − RIB_HALF_Y).
RIB_HALF_Y = 2.0                # half the 4 mm rib thickness

ARM_SPAR_CHASSIS_Y = CHASSIS_PIVOT_Y - RIB_HALF_Y          # -38.0 mm (rib outboard face)
ARM_SPAR_CHASSIS_CX = CHASSIS_PIVOT_X_CENTER                # 147.0 mm
ARM_SPAR_CHASSIS_CZ = CHASSIS_PIVOT_Z - 2.0                 # 92.0 mm (slightly below pivot)
ARM_SPAR_CHASSIS_WIDTH = 40.0   # mm in X (spans both ribs with margin)
ARM_SPAR_CHASSIS_HEIGHT = 10.0  # mm in Z

ARM_SPAR_MID_Y = (ARM_SPAR_CHASSIS_Y + WHEEL_AXIS_Y) / 2.0  # -90.5 mm (midpoint)
ARM_SPAR_MID_CX = 156.0         # mm (biased forward toward axle)
ARM_SPAR_MID_CZ = (CHASSIS_PIVOT_Z + WHEEL_AXIS_Z) / 2.0   # 84.5 mm
ARM_SPAR_MID_WIDTH = 22.0       # mm in X
ARM_SPAR_MID_HEIGHT = 10.0      # mm in Z

ARM_SPAR_CARRIER_Y = WHEEL_AXIS_Y                           # -143.0 mm
ARM_SPAR_CARRIER_CX = WHEEL_AXIS_X                          # 165.0 mm
ARM_SPAR_CARRIER_CZ = WHEEL_AXIS_Z                          # 75.0 mm
ARM_SPAR_CARRIER_WIDTH = 14.0   # mm in X
ARM_SPAR_CARRIER_HEIGHT = 10.0  # mm in Z

# Pivot ribs  —  two rectangular pegs that drop into the chassis pad slots
RIB_HEIGHT_Z = 10.0             # mm, rib height; bore is centred in this
RIB_LENGTH_X = 10.0             # mm in X (fits within 12 mm slot with 1 mm play)
RIB_WIDTH_Y = RIB_HALF_Y * 2.0  # 4.0 mm (0.1 mm clearance inside 4.2 mm slot)
PIVOT_PIN_BORE_D = 4.4          # mm, M4 clearance bore through rib in X

# Carrier-end socket boss  (Z-axis cylinder; bore for upper pivot pin or ball stud)
SOCKET_BOSS_OD = 16.0           # mm
SOCKET_BOSS_HEIGHT = 22.0       # mm, straddles the wheel axis
SOCKET_BORE_D = 5.25            # mm, M5 clearance bore

# Shock lower mount boss  (X-axis cylinder for clevis pin)
SHOCK_BOSS_OD = 10.0            # mm
SHOCK_BOSS_LENGTH = 14.0        # mm
SHOCK_BORE_D = 4.4              # mm, M4 bore
SHOCK_X = CHASSIS_PIVOT_X_CENTER + 6.0                     # 153.0 mm
SHOCK_Y = ARM_SPAR_MID_Y - 5.0                             # -95.5 mm
SHOCK_Z = ARM_SPAR_MID_CZ - 4.0                            # 80.5 mm

# Bump stop pad  (disc on the arm's upper face at the chassis end)
BUMP_PAD_D = 14.0               # mm
BUMP_PAD_HEIGHT = 4.0           # mm
BUMP_PAD_X = CHASSIS_PIVOT_X_CENTER + 4.0                  # 151.0 mm
BUMP_PAD_Y = CHASSIS_PIVOT_Y + 10.0                        # -26.0 mm (outboard of pivot)
BUMP_PAD_Z_BOTTOM = ARM_SPAR_CHASSIS_CZ + ARM_SPAR_CHASSIS_HEIGHT / 2.0  # top of spar at chassis end

# =============================================================================
# DOCUMENT SETUP
# =============================================================================

DOC_NAME = "Corner_HighPivotArm_LHF_v01"
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


def make_cyl_x(radius, length, x0, y, z):
    return Part.makeCylinder(radius, length, App.Vector(x0, y, z), App.Vector(1, 0, 0))


def make_cyl_z(radius, length, x, y, z0):
    return Part.makeCylinder(radius, length, App.Vector(x, y, z0), App.Vector(0, 0, 1))


def make_rect_wire_at_y(cx, cy, cz, half_w, half_h):
    """Closed rectangular Wire in the XZ plane at y=cy.

    Vertices run counter-clockwise when viewed from the +Y direction, which
    ensures consistent winding across all loft profiles.
    """
    verts = [
        App.Vector(cx - half_w, cy, cz - half_h),  # bottom-left
        App.Vector(cx + half_w, cy, cz - half_h),  # bottom-right
        App.Vector(cx + half_w, cy, cz + half_h),  # top-right
        App.Vector(cx - half_w, cy, cz + half_h),  # top-left
    ]
    edges = [
        Part.makeLine(verts[0], verts[1]),
        Part.makeLine(verts[1], verts[2]),
        Part.makeLine(verts[2], verts[3]),
        Part.makeLine(verts[3], verts[0]),
    ]
    return Part.Wire(edges)


# =============================================================================
# ARM GEOMETRY BUILDERS
# =============================================================================


def build_arm_spar():
    """Build the main structural spar via a three-station loft.

    Profiles are rectangular sections in the XZ plane at three Y positions:
      Station 1 (chassis end):  wide, high Z   —  Y = -38 mm
      Station 2 (mid-span):     medium width    —  Y = -90.5 mm
      Station 3 (carrier end):  narrow, low Z   —  Y = -143 mm

    ruled=True gives flat-sided faces between stations, which are easier to
    slice cleanly on an FDM printer than smooth NURBS blends.
    """
    profile_chassis = make_rect_wire_at_y(
        ARM_SPAR_CHASSIS_CX, ARM_SPAR_CHASSIS_Y, ARM_SPAR_CHASSIS_CZ,
        ARM_SPAR_CHASSIS_WIDTH / 2.0, ARM_SPAR_CHASSIS_HEIGHT / 2.0,
    )
    profile_mid = make_rect_wire_at_y(
        ARM_SPAR_MID_CX, ARM_SPAR_MID_Y, ARM_SPAR_MID_CZ,
        ARM_SPAR_MID_WIDTH / 2.0, ARM_SPAR_MID_HEIGHT / 2.0,
    )
    profile_carrier = make_rect_wire_at_y(
        ARM_SPAR_CARRIER_CX, ARM_SPAR_CARRIER_Y, ARM_SPAR_CARRIER_CZ,
        ARM_SPAR_CARRIER_WIDTH / 2.0, ARM_SPAR_CARRIER_HEIGHT / 2.0,
    )
    return Part.makeLoft([profile_chassis, profile_mid, profile_carrier], True, True)


def build_pivot_ribs():
    """Build the two pivot ribs and cut the M4 pivot bores.

    Each rib is a 10 × 4 × 10 mm rectangular block centred on the chassis
    slot position (X = 136 and X = 158, Y = -36, Z = 94).  The 4 mm Y width
    fits inside the 4.2 mm slot with 0.1 mm clearance each side.  Each rib
    has a 4.4 mm bore in the X direction for the M4 pivot pin.
    """
    positives = []
    negatives = []

    for slot_x in (CHASSIS_SLOT_X_REAR, CHASSIS_SLOT_X_FRONT):
        rib = make_centered_box(
            RIB_LENGTH_X, RIB_WIDTH_Y, RIB_HEIGHT_Z,
            slot_x, CHASSIS_PIVOT_Y, CHASSIS_PIVOT_Z,
        )
        positives.append(rib)

        # M4 bore through the rib in X (pin inserted from the outboard side)
        bore = make_cyl_x(
            PIVOT_PIN_BORE_D / 2.0,
            RIB_LENGTH_X + 2.0,
            slot_x - RIB_LENGTH_X / 2.0 - 1.0,
            CHASSIS_PIVOT_Y,
            CHASSIS_PIVOT_Z,
        )
        negatives.append(bore)

    return cut_shapes(fuse_shapes(positives), negatives)


def build_carrier_socket():
    """Build the carrier-end socket boss (Z-axis cylinder with M5 bore).

    The socket is centred on the wheel axis (X=165, Y=-143, Z=75) and runs
    ±11 mm in Z to straddle the wheel axis.  Stage 3 will add the ball-joint
    seat geometry inside the bore.
    """
    positives = []
    negatives = []

    boss = make_cyl_z(
        SOCKET_BOSS_OD / 2.0,
        SOCKET_BOSS_HEIGHT,
        WHEEL_AXIS_X,
        WHEEL_AXIS_Y,
        WHEEL_AXIS_Z - SOCKET_BOSS_HEIGHT / 2.0,
    )
    positives.append(boss)

    bore = make_cyl_z(
        SOCKET_BORE_D / 2.0,
        SOCKET_BOSS_HEIGHT + 2.0,
        WHEEL_AXIS_X,
        WHEEL_AXIS_Y,
        WHEEL_AXIS_Z - SOCKET_BOSS_HEIGHT / 2.0 - 1.0,
    )
    negatives.append(bore)

    return cut_shapes(fuse_shapes(positives), negatives)


def build_shock_mount():
    """Build the shock lower mount boss (X-axis clevis cylinder with M4 bore)."""
    positives = []
    negatives = []

    boss = make_cyl_x(
        SHOCK_BOSS_OD / 2.0,
        SHOCK_BOSS_LENGTH,
        SHOCK_X - SHOCK_BOSS_LENGTH / 2.0,
        SHOCK_Y,
        SHOCK_Z,
    )
    positives.append(boss)

    bore = make_cyl_x(
        SHOCK_BORE_D / 2.0,
        SHOCK_BOSS_LENGTH + 2.0,
        SHOCK_X - SHOCK_BOSS_LENGTH / 2.0 - 1.0,
        SHOCK_Y,
        SHOCK_Z,
    )
    negatives.append(bore)

    return cut_shapes(fuse_shapes(positives), negatives)


def build_bump_pad():
    """Build the bump stop pad disc on the arm's upper face (chassis end)."""
    return make_cyl_z(
        BUMP_PAD_D / 2.0,
        BUMP_PAD_HEIGHT,
        BUMP_PAD_X,
        BUMP_PAD_Y,
        BUMP_PAD_Z_BOTTOM,
    )


def build_carrier_envelope_ref():
    """Return the carrier envelope reference box for a clearance check overlay."""
    env_z_centre = LOWEST_HARDPOINT_Z + CARRIER_ENV_HEIGHT / 2.0
    return make_centered_box(
        CARRIER_ENV_LENGTH, CARRIER_ENV_WIDTH, CARRIER_ENV_HEIGHT,
        WHEEL_AXIS_X, WHEEL_AXIS_Y, env_z_centre,
    )


# =============================================================================
# MAIN
# =============================================================================


def main():
    doc = get_or_create_document(DOC_NAME)

    arm_group = add_group(doc, "HighPivotArm_LHF")
    refs_group = add_group(doc, "References")

    created = []

    # Build components
    App.Console.PrintMessage("Building arm spar (loft)...\n")
    spar = build_arm_spar()

    App.Console.PrintMessage("Building pivot ribs...\n")
    ribs = build_pivot_ribs()

    App.Console.PrintMessage("Building carrier socket...\n")
    socket = build_carrier_socket()

    App.Console.PrintMessage("Building shock mount boss...\n")
    shock = build_shock_mount()

    App.Console.PrintMessage("Building bump stop pad...\n")
    bump = build_bump_pad()

    # Fuse all arm solids into one body
    App.Console.PrintMessage("Fusing arm components...\n")
    arm_solid = fuse_shapes([spar, ribs, socket, shock, bump])

    arm_obj = add_shape_object(doc, "HighPivotArm_LHF_v01", arm_solid, arm_group)
    created.append(arm_obj)

    # Carrier envelope reference (transparent overlay for clearance check)
    env_ref = build_carrier_envelope_ref()
    env_obj = add_shape_object(doc, "REF_CarrierEnvelope", env_ref, refs_group)
    created.append(env_obj)

    # Apply view settings
    try:
        import FreeCADGui  # noqa: F401
        arm_obj.ViewObject.ShapeColor = (0.75, 0.55, 0.15)     # amber / PETG colour
        arm_obj.ViewObject.Transparency = 0
        env_obj.ViewObject.ShapeColor = (0.2, 0.6, 0.9)
        env_obj.ViewObject.Transparency = 85
    except Exception:
        pass

    doc.recompute()

    # Summary
    arm_y_span = abs(WHEEL_AXIS_Y - ARM_SPAR_CHASSIS_Y)
    arm_z_drop = CHASSIS_PIVOT_Z - WHEEL_AXIS_Z
    arm_x_sweep = abs(WHEEL_AXIS_X - CHASSIS_PIVOT_X_CENTER)

    App.Console.PrintMessage("\n=== HighPivotArm LHF v0.1 - Stage 2 Summary ===\n")
    App.Console.PrintMessage(f"Document      : {doc.Name}\n")
    App.Console.PrintMessage(f"\nArm span:\n")
    App.Console.PrintMessage(f"  Y span (inboard -> outboard) : {arm_y_span:.1f} mm\n")
    App.Console.PrintMessage(f"  Z drop (chassis -> wheel)    : {arm_z_drop:.1f} mm\n")
    App.Console.PrintMessage(f"  X sweep (setback -> axle)    : {arm_x_sweep:.1f} mm\n")
    App.Console.PrintMessage(f"\nChassis pivot (X axis):  X={CHASSIS_PIVOT_X_CENTER:.1f}  Y={CHASSIS_PIVOT_Y:.1f}  Z={CHASSIS_PIVOT_Z:.1f}\n")
    App.Console.PrintMessage(f"  Rear slot at X={CHASSIS_SLOT_X_REAR:.1f}  |  Front slot at X={CHASSIS_SLOT_X_FRONT:.1f}\n")
    App.Console.PrintMessage(f"  Rib width in Y = {RIB_WIDTH_Y:.1f} mm  (slot {AXLE_SLOT_WIDTH:.1f} mm  →  {AXLE_SLOT_WIDTH - RIB_WIDTH_Y:.2f} mm total clearance)\n")
    App.Console.PrintMessage(f"\nCarrier socket: X={WHEEL_AXIS_X:.1f}  Y={WHEEL_AXIS_Y:.1f}  Z={WHEEL_AXIS_Z:.1f}\n")
    App.Console.PrintMessage(f"Shock mount:    X={SHOCK_X:.1f}  Y={SHOCK_Y:.1f}  Z={SHOCK_Z:.1f}\n")
    App.Console.PrintMessage(f"\nPivot bore  : {PIVOT_PIN_BORE_D:.1f} mm  (M4 nominal)\n")
    App.Console.PrintMessage(f"Socket bore : {SOCKET_BORE_D:.2f} mm  (M5 nominal — ball joint seat in Stage 3)\n")
    App.Console.PrintMessage(f"Shock bore  : {SHOCK_BORE_D:.1f} mm  (M4 nominal)\n")
    App.Console.PrintMessage(f"\nCarrier envelope check: {CARRIER_ENV_LENGTH:.0f} x {CARRIER_ENV_WIDTH:.0f} x {CARRIER_ENV_HEIGHT:.0f} mm\n")
    App.Console.PrintMessage(f"  Arm must remain inside this envelope throughout full suspension travel.\n")
    App.Console.PrintMessage("\nStage 2 complete. Proceed to Stage 3 (Upright / carrier body).\n")

    return doc, arm_obj


main()
