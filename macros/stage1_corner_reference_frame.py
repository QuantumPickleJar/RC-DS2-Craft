# =============================================================================
# RC CORNER MODULE - STAGE 1: CORNER REFERENCE FRAME (v0.1)
# =============================================================================
# Creates the datum reference frame for the left-hand front corner.
# Run this in FreeCAD (1.0+) via the Macro Editor or Python Console.
#
# Coordinate system (matches skeleton macro):
#   X = longitudinal (rear -> front)
#   Y = lateral (positive = right, negative = left)
#   Z = vertical (up)
#
# For the LEFT-HAND corner, Y values are NEGATIVE (port side).
# For the RIGHT-HAND corner, mirror everything through Y=0.
#
# Learning note:
# This script uses direct Part primitives (cylinders and spheres) to
# represent abstract datum objects (axes, LCS markers, planes). FreeCAD's
# PartDesign datum features are more appropriate for production models, but
# Part primitives are simpler to drive from a parametric Python macro.
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

# High-pivot-arm carrier preset (active selection in skeleton macro)
CARRIER_MOUNT_Z = 94.0          # mm, Z of chassis-side mount plane
LOWEST_HARDPOINT_Z = 64.0       # mm, minimum Z of any carrier component

# Axle mount geometry (from skeleton macro)
AXLE_X = WHEELBASE / 2.0                                    # 165.0 mm (front axle)
AXLE_MOUNT_SETBACK = 18.0                                   # mm
AXLE_PAD_CENTER_X = AXLE_X - AXLE_MOUNT_SETBACK             # 147.0 mm
AXLE_SLOT_SPACING_Y = 72.0                                  # mm

# =============================================================================
# CORNER INTERFACE PARAMETERS  (left-hand front)
# =============================================================================

# Corner interface origin: where the corner module attaches to the chassis.
CORNER_INTERFACE_X = AXLE_X                                 # 165.0 mm (at front axle)
CORNER_INTERFACE_Y = -(TRACK_WIDTH / 2.0)                   # -143.0 mm (left side)
CORNER_INTERFACE_Z = CARRIER_MOUNT_Z                        # 94.0 mm

# Wheel axis
WHEEL_AXIS_X = CORNER_INTERFACE_X                           # 165.0 mm
WHEEL_AXIS_Y = CORNER_INTERFACE_Y                           # -143.0 mm
WHEEL_AXIS_Z = TIRE_OUTER_DIAMETER / 2.0                    # 75.0 mm

# Chassis-side arm pivot axis (the pivot ribs engage the carrier mount pad slots
# at Y = -(AXLE_SLOT_SPACING_Y / 2) for the left arm).
CHASSIS_PIVOT_X = AXLE_PAD_CENTER_X                          # 147.0 mm
CHASSIS_PIVOT_Y = -(AXLE_SLOT_SPACING_Y / 2.0)             # -36.0 mm
CHASSIS_PIVOT_Z = CARRIER_MOUNT_Z                           # 94.0 mm

# Tie rod pickup  (placeholder; refined when steering geometry is detailed)
TIE_ROD_X = WHEEL_AXIS_X + 25.0
TIE_ROD_Y = WHEEL_AXIS_Y + 15.0
TIE_ROD_Z = WHEEL_AXIS_Z + 20.0

# Shock lower mount  (placeholder; mid-span on arm)
SHOCK_LOWER_X = CHASSIS_PIVOT_X + 6.0
SHOCK_LOWER_Y = (CHASSIS_PIVOT_Y + WHEEL_AXIS_Y) / 2.0 - 5.0   # midpoint -89.5, offset -5.0 → -94.5 mm
SHOCK_LOWER_Z = (CHASSIS_PIVOT_Z + WHEEL_AXIS_Z) / 2.0 - 4.0   # 80.5 mm

# Bump stop contact points  (placeholder)
BUMP_STOP_ARM_X = CHASSIS_PIVOT_X + 4.0
BUMP_STOP_ARM_Y = CHASSIS_PIVOT_Y + 10.0                    # -26.0 mm
BUMP_STOP_ARM_Z = CHASSIS_PIVOT_Z + 10.0

BUMP_STOP_CARRIER_X = BUMP_STOP_ARM_X
BUMP_STOP_CARRIER_Y = BUMP_STOP_ARM_Y
BUMP_STOP_CARRIER_Z = BUMP_STOP_ARM_Z - 15.0

# =============================================================================
# VISUALISATION PARAMETERS
# =============================================================================

DATUM_AXIS_LENGTH = 60.0        # mm
DATUM_AXIS_RADIUS = 1.5         # mm
LCS_MARKER_SIZE = 8.0           # mm (full length of each arm)
DATUM_PLANE_HALF = 40.0         # mm (half-size of plane square)
DATUM_PLANE_THICK = 0.5         # mm

# =============================================================================
# DOCUMENT SETUP
# =============================================================================

DOC_NAME = "Corner_WheelEnd_LH_R1"
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


def make_lcs_marker(x, y, z, size):
    """Three-axis cross marker (sphere at origin, cylinders along each axis)."""
    half = size / 2.0
    r = size / 8.0
    x_arm = Part.makeCylinder(r, size, App.Vector(x - half, y, z), App.Vector(1, 0, 0))
    y_arm = Part.makeCylinder(r, size, App.Vector(x, y - half, z), App.Vector(0, 1, 0))
    z_arm = Part.makeCylinder(r, size, App.Vector(x, y, z - half), App.Vector(0, 0, 1))
    origin = Part.makeSphere(r * 1.8, App.Vector(x, y, z))
    return x_arm.fuse(y_arm).fuse(z_arm).fuse(origin)


def make_datum_axis(x, y, z, axis, length, radius):
    half = length / 2.0
    if axis.upper() == "X":
        return Part.makeCylinder(radius, length, App.Vector(x - half, y, z), App.Vector(1, 0, 0))
    if axis.upper() == "Y":
        return Part.makeCylinder(radius, length, App.Vector(x, y - half, z), App.Vector(0, 1, 0))
    if axis.upper() == "Z":
        return Part.makeCylinder(radius, length, App.Vector(x, y, z - half), App.Vector(0, 0, 1))
    raise ValueError(f"axis must be X, Y or Z; got {axis!r}")


def make_datum_plane_xz(x, y, z, half_size, thickness):
    """Thin XZ-plane slab (normal to Y) for the corner midplane."""
    return Part.makeBox(
        half_size * 2.0,
        thickness,
        half_size * 2.0,
        App.Vector(x - half_size, y - thickness / 2.0, z - half_size),
    )


# =============================================================================
# MAIN
# =============================================================================


def main():
    doc = get_or_create_document(DOC_NAME)

    references_group = add_group(doc, "References")
    lcs_group = add_group(doc, "LocalCoordinateSystems", references_group)
    axes_group = add_group(doc, "DatumAxes", references_group)
    planes_group = add_group(doc, "DatumPlanes", references_group)

    created = []

    # -------------------------------------------------------------------------
    # LOCAL COORDINATE SYSTEMS
    # -------------------------------------------------------------------------

    # LCS_Corner_Interface_LH  —  master anchor for the corner module at the
    # chassis carrier mount plane (Z=94), at the wheel centreline (Y=-143).
    created.append(add_shape_object(
        doc, "LCS_Corner_Interface_LH",
        make_lcs_marker(CORNER_INTERFACE_X, CORNER_INTERFACE_Y, CORNER_INTERFACE_Z,
                        LCS_MARKER_SIZE * 1.5),
        lcs_group,
    ))

    # LCS_TieRodPickup  —  ball joint attachment on steering ear (placeholder).
    created.append(add_shape_object(
        doc, "LCS_TieRodPickup",
        make_lcs_marker(TIE_ROD_X, TIE_ROD_Y, TIE_ROD_Z, LCS_MARKER_SIZE),
        lcs_group,
    ))

    # LCS_ShockLower  —  lower shock mount position on arm (placeholder).
    created.append(add_shape_object(
        doc, "LCS_ShockLower",
        make_lcs_marker(SHOCK_LOWER_X, SHOCK_LOWER_Y, SHOCK_LOWER_Z, LCS_MARKER_SIZE),
        lcs_group,
    ))

    # LCS_BumpStopArm  —  bump stop contact point on arm (placeholder).
    created.append(add_shape_object(
        doc, "LCS_BumpStopArm",
        make_lcs_marker(BUMP_STOP_ARM_X, BUMP_STOP_ARM_Y, BUMP_STOP_ARM_Z,
                        LCS_MARKER_SIZE * 0.8),
        lcs_group,
    ))

    # LCS_BumpStopCarrier  —  bump stop contact point on carrier (placeholder).
    created.append(add_shape_object(
        doc, "LCS_BumpStopCarrier",
        make_lcs_marker(BUMP_STOP_CARRIER_X, BUMP_STOP_CARRIER_Y, BUMP_STOP_CARRIER_Z,
                        LCS_MARKER_SIZE * 0.8),
        lcs_group,
    ))

    # -------------------------------------------------------------------------
    # DATUM AXES
    # -------------------------------------------------------------------------

    # Axis_CarrierPivot  —  main revolute joint axis (X direction).
    # The two arm pivot ribs engage the chassis pad slots and rotate around this axis.
    created.append(add_shape_object(
        doc, "Axis_CarrierPivot",
        make_datum_axis(CHASSIS_PIVOT_X, CHASSIS_PIVOT_Y, CHASSIS_PIVOT_Z,
                        "X", DATUM_AXIS_LENGTH, DATUM_AXIS_RADIUS),
        axes_group,
    ))

    # Axis_Wheel  —  wheel rotation axis (Y direction).
    created.append(add_shape_object(
        doc, "Axis_Wheel",
        make_datum_axis(WHEEL_AXIS_X, WHEEL_AXIS_Y, WHEEL_AXIS_Z,
                        "Y", DATUM_AXIS_LENGTH, DATUM_AXIS_RADIUS),
        axes_group,
    ))

    # Axis_Steering  —  steering kingpin axis (Z direction, at wheel centre).
    created.append(add_shape_object(
        doc, "Axis_Steering",
        make_datum_axis(WHEEL_AXIS_X, WHEEL_AXIS_Y, WHEEL_AXIS_Z,
                        "Z", DATUM_AXIS_LENGTH, DATUM_AXIS_RADIUS),
        axes_group,
    ))

    # Axis_ShaftEntry  —  half-shaft entry direction (Y direction, inboard of wheel).
    shaft_entry_y = WHEEL_AXIS_Y + (TIRE_WIDTH / 2.0) + 10.0
    created.append(add_shape_object(
        doc, "Axis_ShaftEntry",
        make_datum_axis(WHEEL_AXIS_X, shaft_entry_y, WHEEL_AXIS_Z,
                        "Y", DATUM_AXIS_LENGTH * 0.8, DATUM_AXIS_RADIUS * 0.8),
        axes_group,
    ))

    # -------------------------------------------------------------------------
    # DATUM PLANES
    # -------------------------------------------------------------------------

    # Plane_CornerMidplane  —  XZ midplane at wheel centreline Y, for mirroring.
    created.append(add_shape_object(
        doc, "Plane_CornerMidplane",
        make_datum_plane_xz(WHEEL_AXIS_X, WHEEL_AXIS_Y, WHEEL_AXIS_Z,
                            DATUM_PLANE_HALF, DATUM_PLANE_THICK),
        planes_group,
    ))

    # -------------------------------------------------------------------------
    # VIEW SETTINGS
    # -------------------------------------------------------------------------
    try:
        import FreeCADGui  # noqa: F401
        for obj in created:
            if obj.Name.startswith("LCS_"):
                obj.ViewObject.ShapeColor = (0.2, 0.8, 0.2)
                obj.ViewObject.Transparency = 30
            elif obj.Name.startswith("Axis_"):
                obj.ViewObject.ShapeColor = (0.8, 0.2, 0.2)
                obj.ViewObject.Transparency = 20
            elif obj.Name.startswith("Plane_"):
                obj.ViewObject.ShapeColor = (0.2, 0.2, 0.8)
                obj.ViewObject.Transparency = 70
    except Exception:
        pass

    doc.recompute()

    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------
    App.Console.PrintMessage("\n=== Corner Reference Frame - Stage 1 Summary ===\n")
    App.Console.PrintMessage(f"Document : {doc.Name}\n")
    App.Console.PrintMessage(f"Corner   : Left-Hand Front\n")
    App.Console.PrintMessage(f"\nCorner interface origin:\n")
    App.Console.PrintMessage(f"  X = {CORNER_INTERFACE_X:.1f} mm  (front axle)\n")
    App.Console.PrintMessage(f"  Y = {CORNER_INTERFACE_Y:.1f} mm  (left side, negative)\n")
    App.Console.PrintMessage(f"  Z = {CORNER_INTERFACE_Z:.1f} mm  (carrier mount plane)\n")
    App.Console.PrintMessage(f"\nWheel axis: X={WHEEL_AXIS_X:.1f}  Y={WHEEL_AXIS_Y:.1f}  Z={WHEEL_AXIS_Z:.1f}\n")
    App.Console.PrintMessage(f"Chassis pivot: X={CHASSIS_PIVOT_X:.1f}  Y={CHASSIS_PIVOT_Y:.1f}  Z={CHASSIS_PIVOT_Z:.1f}\n")
    App.Console.PrintMessage(f"\nObjects created: {len(created)}\n")
    App.Console.PrintMessage("Stage 1 complete. Proceed to Stage 2 (HighPivotArm body).\n")

    return doc, created


main()
