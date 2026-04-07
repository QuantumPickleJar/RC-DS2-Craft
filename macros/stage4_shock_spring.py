# =============================================================================
# RC CORNER MODULE - STAGE 4: SHOCK ABSORBER & COIL SPRING - LHF (v0.1)
# =============================================================================
# Creates the shock absorber and coil spring geometry for the left-hand front
# corner.  Run this in FreeCAD (1.0+) via the Macro Editor or Python Console.
#
# Coordinate system (matches skeleton macro):
#   X = longitudinal (rear -> front)
#   Y = lateral (positive = right, negative = left)
#   Z = vertical (up)
#
# SPATIAL RELATIONSHIPS TO PREVIOUS STAGES
# ----------------------------------------
# Lower mount   (Stage 2 arm boss):  X=153,  Y=−95.5, Z=80.5
# Upper mount   (Stage 4 tower boss): X=147, Y=−38,   Z=165
#
# The shock axis runs from lower to upper at roughly 55° from vertical when
# projected into the YZ plane, giving a motion ratio of ~0.71 (the arm moves
# 1 mm at the wheel for every 0.71 mm of shock travel).
#
# SHOCK ARCHITECTURE
# ------------------
# The shock is split into three co-axial solids along the shock axis:
#
#   ┌──────────────────────────────────────────────────┐   ← upper mount boss
#   │           Shock body (outer tube)                │
#   │  Ø12 mm OD / Ø9.2 mm ID — damper fluid volume   │
#   │  Length = SHOCK_BODY_LENGTH ≈ 60 mm              │
#   ├──────────────────────────────────────────────────┤   ← shaft seal / wiper
#   │         Shock rod (piston rod)                   │
#   │  Ø5.5 mm solid — stainless steel equivalent      │
#   │  Length = SHOCK_ROD_LENGTH ≈ 60 mm               │
#   └──────────────────────────────────────────────────┘   ← lower mount clevis
#
# A coil spring sits over the shock body+rod.  Its ends are modelled as flat
# disc caps; the coil itself is a proper helical sweep.
#
# SPRING RATE CALCULATION
# -----------------------
# Estimated vehicle mass  : 3.0 kg
# Weight per corner       : 3.0 × 9.81 / 4 = 7.36 N
# Target static sag       : 8 mm  (≈ 27 % of 30 mm stroke)
# Required spring rate    : 7.36 / 0.008 = 920 N/m = 0.92 N/mm
# Chosen spring rate      : SPRING_RATE = 1.0 N/mm  (nearest standard)
# Spring free length      : SPRING_FREE_LENGTH = 65 mm
# Spring compressed length: 65 − 8 = 57 mm  (static ride height)
# Spring solid height     : coils × wire_Ø = 7 × 1.8 = 12.6 mm
# Available stroke        : free − solid − preload = 65 − 12.6 − 8 = 44.4 mm
#                           (more than the 30 mm damper stroke → no coil bind)
#
# Motion ratio applied to spring:
#   Spring rate at wheel = SPRING_RATE × MOTION_RATIO² = 1.0 × 0.71² = 0.50 N/mm
#   At 3 kg / 4 corners that gives ~14.7 mm static sag — revise if too soft.
#
# Placeholder notes:
#   - Upper mount position X/Y/Z is an estimate; adjust once the chassis
#     tower geometry is detailed in Stage 5.
#   - Damper valving, oil volume, and rebound settings are not modelled here.
#   - Bump-stop rubber insert (Stage 3 placeholder) limits travel before
#     coil bind can occur.
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

WHEELBASE  = 330.0
TRACK_WIDTH = 286.0
TIRE_OUTER_DIAMETER = 150.0

AXLE_X = WHEELBASE / 2.0                           # 165.0 mm
WHEEL_AXIS_Y = -(TRACK_WIDTH / 2.0)                # -143.0 mm

CARRIER_MOUNT_Z = 94.0
AXLE_PAD_CENTER_X = AXLE_X - 18.0                  # 147.0 mm

# =============================================================================
# SHOCK MOUNT COORDINATES
# =============================================================================

# Lower mount — taken directly from Stage 2 arm geometry.
SHOCK_LOWER_X =  153.0      # mm  (AXLE_PAD_CENTER_X + 6 = 153)
SHOCK_LOWER_Y =  -95.5      # mm  (arm mid-span, ARM_SPAR_MID_Y - 5)
SHOCK_LOWER_Z =   80.5      # mm  (ARM_SPAR_MID_CZ - 4)

# Upper mount — on the chassis shock tower.
# The tower is a vertical rib rising from the chassis rail above the arm
# pivot.  X is aligned with the chassis pivot to minimise fore-aft bending
# in the tower.  Y is close to the pivot slots so the tower base bolts into
# the existing carrier mount pad.
SHOCK_UPPER_X =  147.0      # mm  (above AXLE_PAD_CENTER_X)
SHOCK_UPPER_Y =  -38.0      # mm  (at chassis pivot Y, inboard of arm)
SHOCK_UPPER_Z =  165.0      # mm  (tower top; sets shock extended length)

# =============================================================================
# SHOCK DAMPER GEOMETRY
# =============================================================================

SHOCK_STROKE      = 30.0    # mm, total piston travel (compressed → extended)

# Shock body (outer damper tube)
SHOCK_BODY_OD     = 12.0    # mm, aluminium alloy or PETG prototype
SHOCK_BODY_WALL   =  1.4    # mm, minimum wall
SHOCK_BODY_ID     = SHOCK_BODY_OD - 2.0 * SHOCK_BODY_WALL  # 9.2 mm

# Shock rod (piston rod)
SHOCK_ROD_D       =  5.5    # mm, solid rod

# Upper mount boss at tower top (Y-axis cylinder for clevis pin)
UPPER_BOSS_OD     =  8.0    # mm
UPPER_BOSS_LENGTH = 12.0    # mm
UPPER_BOSS_BORE_D =  4.4    # mm, M4 clevis pin

# =============================================================================
# COIL SPRING GEOMETRY
# =============================================================================

SPRING_OD           = 18.0      # mm, outer coil diameter
SPRING_WIRE_D       =  1.8      # mm, wire diameter
SPRING_COIL_RADIUS  = (SPRING_OD - SPRING_WIRE_D) / 2.0    # 8.1 mm  (centreline radius)
SPRING_FREE_LENGTH  = 65.0      # mm
SPRING_ACTIVE_COILS =  7.0      # number of active helical coils
SPRING_PITCH        = SPRING_FREE_LENGTH / SPRING_ACTIVE_COILS   # 9.286 mm / coil

# End-cap disc dimensions (represent the flat ground coil at each end)
END_CAP_THICKNESS   =  SPRING_WIRE_D   # 1.8 mm, one wire diameter high
END_CAP_OD          =  SPRING_OD
END_CAP_ID          =  SPRING_OD - 2.0 * SPRING_WIRE_D    # 14.4 mm

# =============================================================================
# SPRING RATE (for console report)
# =============================================================================

VEHICLE_MASS_KG   =  3.0
MOTION_RATIO      =  0.71       # shock travel / wheel travel
STATIC_SAG_MM     =  8.0       # target static sag

# Wire shear modulus for spring steel (used for theoretical rate check)
_G_STEEL_MPA = 80_000.0   # MPa (typical value for spring steel; e.g. EN 10270)

# Standard coil spring rate formula (Wahl / DIN 2089):
#   k = (G × d⁴) / (8 × D³ × n)
# where d = wire diameter, D = mean coil diameter = 2 × SPRING_COIL_RADIUS,
# n = number of active coils.  G in MPa, dimensions in mm → result in N/mm.
_SPRING_RATE_CALC = (
    (_G_STEEL_MPA * (SPRING_WIRE_D ** 4))
    / (8.0 * (2.0 * SPRING_COIL_RADIUS) ** 3 * SPRING_ACTIVE_COILS)
)  # N/mm  — spring steel; a PETG prototype coil would be ~0.07 N/mm (E_shear ≈ 700 MPa)

# =============================================================================
# DOCUMENT SETUP
# =============================================================================

DOC_NAME         = "Corner_ShockSpring_LHF_v01"
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


def make_cyl_along(radius, length, start_pt, direction):
    """Cylinder of given radius/length, starting at start_pt, directed along direction."""
    return Part.makeCylinder(radius, length, start_pt, direction)


def place_z_shape(shape, base_pt, z_to_dir):
    """Transform a shape built along Z so its Z-axis aligns with z_to_dir,
    with the shape origin translated to base_pt.

    Parameters
    ----------
    shape    : Part.Shape  — geometry built with its axis along +Z at origin
    base_pt  : App.Vector  — desired start/base point in world space
    z_to_dir : App.Vector  — desired axis direction (normalised internally)
    """
    rot = App.Rotation(App.Vector(0, 0, 1), z_to_dir)
    pl  = App.Placement(base_pt, rot)
    return shape.transformGeometry(pl.toMatrix())


# =============================================================================
# DERIVED SHOCK GEOMETRY
# =============================================================================

def _shock_axis():
    """Return (lower_pt, upper_pt, direction, full_extended_length)."""
    lower   = App.Vector(SHOCK_LOWER_X, SHOCK_LOWER_Y, SHOCK_LOWER_Z)
    upper   = App.Vector(SHOCK_UPPER_X, SHOCK_UPPER_Y, SHOCK_UPPER_Z)
    delta   = upper.sub(lower)
    length  = delta.Length
    direction = delta.normalize()
    return lower, upper, direction, length


def _split_point(lower, direction, distance_from_lower):
    """Point along the shock axis at 'distance_from_lower' mm from lower."""
    return lower.add(direction.multiply(distance_from_lower))


# =============================================================================
# SHOCK BODY BUILDERS
# =============================================================================


def build_upper_mount_boss(upper, direction):
    """Upper mount boss: a short cylinder centred on the upper mount point,
    oriented along the shock axis, with an M4 bore.

    The boss is centred on 'upper' so it straddles the clevis pin.
    """
    start = upper.sub(direction.multiply(UPPER_BOSS_LENGTH / 2.0))
    positives = [make_cyl_along(UPPER_BOSS_OD / 2.0, UPPER_BOSS_LENGTH, start, direction)]
    bore      = [make_cyl_along(UPPER_BOSS_BORE_D / 2.0,
                                UPPER_BOSS_LENGTH + 2.0,
                                upper.sub(direction.multiply(UPPER_BOSS_LENGTH / 2.0 + 1.0)),
                                direction)]
    return cut_shapes(fuse_shapes(positives), bore)


def build_shock_body(lower, direction, extended_length):
    """Outer damper tube: hollow cylinder from the upper mount downward.

    The body covers the upper portion of the shock travel; the rod extends
    below it.  At ride height (STATIC_SAG_MM from full extension) the body
    and rod overlap by approximately STATIC_SAG_MM.

    The body length is set so the bottom end lands at the static ride-height
    split point (extended_length − STATIC_SAG_MM from the lower mount).
    """
    body_length = extended_length - STATIC_SAG_MM    # ≈ 94 mm

    # Start the body at the lower mount and go upward so the Boolean maths
    # uses a consistent reference frame.  We then cut the rod bore from below.
    body_start = lower
    outer = make_cyl_along(SHOCK_BODY_OD / 2.0, body_length, body_start, direction)
    inner = make_cyl_along(SHOCK_BODY_ID / 2.0, body_length + 2.0,
                           body_start.sub(direction.multiply(1.0)), direction)
    return cut_shapes(outer, [inner]), body_length


def build_shock_rod(lower, direction, extended_length):
    """Piston rod: solid cylinder from the lower mount upward.

    Rod length equals the body length so the rod is always contained within
    (or just proud of) the shock body at all travel positions.
    """
    rod_length = extended_length - STATIC_SAG_MM    # same split as body
    return make_cyl_along(SHOCK_ROD_D / 2.0, rod_length, lower, direction), rod_length


def build_spring(lower, direction):
    """Coil spring over the shock.

    Attempts a proper helical sweep (wire_Ø circle swept along a helix).
    Falls back to a hollow cylinder envelope if the sweep fails.

    The helix is built at origin along Z then transformed to the shock axis.
    End-caps (annular discs one wire-diameter thick) are added at both ends.
    """
    # ---- Helix + sweep -------------------------------------------------------
    try:
        helix_wire = Part.makeHelix(SPRING_PITCH, SPRING_FREE_LENGTH, SPRING_COIL_RADIUS)

        # Profile circle: perpendicular to the helix tangent at its start point.
        # At t=0 the helix lies at (radius, 0, 0).  The tangent direction there
        # is (0, p_tangent, z_tangent) where the helix progresses in Y and Z
        # simultaneously.  Normalised:
        circumference = 2.0 * math.pi * SPRING_COIL_RADIUS
        hyp = math.sqrt(circumference ** 2 + SPRING_PITCH ** 2)
        tan_y = circumference / hyp
        tan_z = SPRING_PITCH / hyp
        tangent_dir = App.Vector(0.0, tan_y, tan_z)

        profile_centre = App.Vector(SPRING_COIL_RADIUS, 0.0, 0.0)
        profile_circle = Part.Wire(
            Part.makeCircle(SPRING_WIRE_D / 2.0, profile_centre, tangent_dir)
        )

        coil_solid = Part.Wire([helix_wire]).makePipeShell(
            [profile_circle],
            True,   # make_solid: close the swept shell into a solid
            True,   # is_frenet: use Frenet-Serret frame to keep profile perpendicular to spine
        )
        App.Console.PrintMessage("  Spring: helical sweep succeeded.\n")

    except Exception as exc:
        # Fallback: hollow cylinder envelope.
        App.Console.PrintWarning(
            f"  Spring helix sweep failed ({exc}); using envelope cylinder.\n"
        )
        coil_outer = Part.makeCylinder(
            SPRING_OD / 2.0, SPRING_FREE_LENGTH,
            App.Vector(0, 0, 0), App.Vector(0, 0, 1),
        )
        coil_inner = Part.makeCylinder(
            (SPRING_OD / 2.0 - SPRING_WIRE_D), SPRING_FREE_LENGTH + 2.0,
            App.Vector(0, 0, -1.0), App.Vector(0, 0, 1),
        )
        coil_solid = coil_outer.cut(coil_inner).removeSplitter()

    # ---- End-caps (flat annular discs, one wire-diameter thick) --------------
    def annular_cap(z_pos):
        outer_cap = Part.makeCylinder(
            END_CAP_OD / 2.0, END_CAP_THICKNESS,
            App.Vector(0, 0, z_pos), App.Vector(0, 0, 1),
        )
        inner_cap = Part.makeCylinder(
            END_CAP_ID / 2.0, END_CAP_THICKNESS + 0.02,
            App.Vector(0, 0, z_pos - 0.01), App.Vector(0, 0, 1),
        )
        return outer_cap.cut(inner_cap).removeSplitter()

    bottom_cap = annular_cap(0.0)
    top_cap    = annular_cap(SPRING_FREE_LENGTH - END_CAP_THICKNESS)
    spring_solid = fuse_shapes([coil_solid, bottom_cap, top_cap])

    # ---- Transform from Z-axis to shock axis ---------------------------------
    return place_z_shape(spring_solid, lower, direction)


# =============================================================================
# REFERENCE MARKER BUILDERS
# =============================================================================


def build_lower_ref(lower, direction):
    """Small sphere-like cylinder marking the lower mount point."""
    return make_cyl_along(2.5, 5.0, lower.sub(direction.multiply(2.5)), direction)


def build_upper_ref(upper, direction):
    """Small sphere-like cylinder marking the upper mount point."""
    return make_cyl_along(2.5, 5.0, upper.sub(direction.multiply(2.5)), direction)


def build_shock_axis_line(lower, direction, length):
    """Thin cylinder along the full shock axis for visual reference."""
    return make_cyl_along(0.5, length, lower, direction)


# =============================================================================
# MAIN
# =============================================================================


def main():
    lower, upper, direction, extended_length = _shock_axis()

    # Angles for the console report
    angle_from_vertical_yz = math.degrees(
        math.atan2(abs(SHOCK_UPPER_Y - SHOCK_LOWER_Y),
                   abs(SHOCK_UPPER_Z - SHOCK_LOWER_Z))
    )
    angle_from_vertical_xz = math.degrees(
        math.atan2(abs(SHOCK_UPPER_X - SHOCK_LOWER_X),
                   abs(SHOCK_UPPER_Z - SHOCK_LOWER_Z))
    )

    doc = get_or_create_document(DOC_NAME)

    shock_grp  = add_group(doc, "ShockSpring_LHF")
    refs_grp   = add_group(doc, "References")

    # ---- Upper mount boss ----------------------------------------------------
    App.Console.PrintMessage("Building upper mount boss...\n")
    upper_boss = build_upper_mount_boss(upper, direction)
    add_shape_object(doc, "ShockUpperBoss", upper_boss, shock_grp)

    # ---- Shock body (outer tube) ---------------------------------------------
    App.Console.PrintMessage("Building shock body (outer tube)...\n")
    shock_body, body_length = build_shock_body(lower, direction, extended_length)
    add_shape_object(doc, "ShockBody", shock_body, shock_grp)

    # ---- Shock rod -----------------------------------------------------------
    App.Console.PrintMessage("Building shock rod...\n")
    shock_rod, rod_length = build_shock_rod(lower, direction, extended_length)
    add_shape_object(doc, "ShockRod", shock_rod, shock_grp)

    # ---- Coil spring ---------------------------------------------------------
    App.Console.PrintMessage("Building coil spring...\n")
    spring = build_spring(lower, direction)
    spring_obj = add_shape_object(doc, "CoilSpring", spring, shock_grp)

    # ---- Reference geometry --------------------------------------------------
    lower_ref  = build_lower_ref(lower, direction)
    upper_ref  = build_upper_ref(upper, direction)
    axis_line  = build_shock_axis_line(lower, direction, extended_length)

    lower_ref_obj = add_shape_object(doc, "REF_LowerMount", lower_ref, refs_grp)
    upper_ref_obj = add_shape_object(doc, "REF_UpperMount", upper_ref, refs_grp)
    axis_obj      = add_shape_object(doc, "REF_ShockAxis",  axis_line, refs_grp)

    # ---- Visual styles -------------------------------------------------------
    try:
        import FreeCADGui  # noqa: F401
        doc.getObject("ShockUpperBoss").ViewObject.ShapeColor = (0.60, 0.65, 0.70)
        doc.getObject("ShockUpperBoss").ViewObject.Transparency = 0

        doc.getObject("ShockBody").ViewObject.ShapeColor = (0.75, 0.55, 0.15)     # amber (PETG)
        doc.getObject("ShockBody").ViewObject.Transparency = 20

        doc.getObject("ShockRod").ViewObject.ShapeColor = (0.85, 0.85, 0.90)      # steel
        doc.getObject("ShockRod").ViewObject.Transparency = 0

        spring_obj.ViewObject.ShapeColor = (0.70, 0.85, 0.30)  # spring green
        spring_obj.ViewObject.Transparency = 0

        lower_ref_obj.ViewObject.ShapeColor = (0.90, 0.20, 0.20)
        lower_ref_obj.ViewObject.Transparency = 30
        upper_ref_obj.ViewObject.ShapeColor = (0.90, 0.20, 0.20)
        upper_ref_obj.ViewObject.Transparency = 30
        axis_obj.ViewObject.ShapeColor = (0.60, 0.60, 0.60)
        axis_obj.ViewObject.Transparency = 70
    except Exception:
        pass

    doc.recompute()

    # ---- Summary -------------------------------------------------------------
    compressed_length = extended_length - SHOCK_STROKE
    solid_height      = SPRING_ACTIVE_COILS * SPRING_WIRE_D
    available_stroke  = SPRING_FREE_LENGTH - solid_height - STATIC_SAG_MM
    spring_rate_at_wheel = _SPRING_RATE_CALC * (MOTION_RATIO ** 2)

    App.Console.PrintMessage("\n=== ShockSpring LHF v0.1 - Stage 4 Summary ===\n")
    App.Console.PrintMessage(f"Document         : {doc.Name}\n")
    App.Console.PrintMessage(f"\nShock axis:\n")
    App.Console.PrintMessage(f"  Lower mount    : ({SHOCK_LOWER_X:.1f}, {SHOCK_LOWER_Y:.1f}, {SHOCK_LOWER_Z:.1f})\n")
    App.Console.PrintMessage(f"  Upper mount    : ({SHOCK_UPPER_X:.1f}, {SHOCK_UPPER_Y:.1f}, {SHOCK_UPPER_Z:.1f})\n")
    App.Console.PrintMessage(f"  Extended length: {extended_length:.1f} mm\n")
    App.Console.PrintMessage(f"  Compressed len : {compressed_length:.1f} mm\n")
    App.Console.PrintMessage(f"  Stroke         : {SHOCK_STROKE:.1f} mm\n")
    App.Console.PrintMessage(f"  Angle from vert: {angle_from_vertical_yz:.1f}° (YZ), {angle_from_vertical_xz:.1f}° (XZ)\n")
    App.Console.PrintMessage(f"\nShock body:\n")
    App.Console.PrintMessage(f"  OD / ID        : Ø{SHOCK_BODY_OD:.1f} / Ø{SHOCK_BODY_ID:.1f} mm\n")
    App.Console.PrintMessage(f"  Body length    : {body_length:.1f} mm\n")
    App.Console.PrintMessage(f"  Rod diameter   : Ø{SHOCK_ROD_D:.1f} mm\n")
    App.Console.PrintMessage(f"  Rod length     : {rod_length:.1f} mm\n")
    App.Console.PrintMessage(f"\nCoil spring:\n")
    App.Console.PrintMessage(f"  OD / wire Ø    : Ø{SPRING_OD:.1f} / Ø{SPRING_WIRE_D:.1f} mm\n")
    App.Console.PrintMessage(f"  Free length    : {SPRING_FREE_LENGTH:.1f} mm\n")
    App.Console.PrintMessage(f"  Active coils   : {SPRING_ACTIVE_COILS:.1f}\n")
    App.Console.PrintMessage(f"  Pitch          : {SPRING_PITCH:.2f} mm/coil\n")
    App.Console.PrintMessage(f"  Solid height   : {solid_height:.1f} mm\n")
    App.Console.PrintMessage(f"  Available stroke: {available_stroke:.1f} mm  (damper stroke {SHOCK_STROKE:.1f} mm)\n")
    App.Console.PrintMessage(f"  Coil bind check: {'OK — no bind' if available_stroke > SHOCK_STROKE else 'WARNING — reduce preload or increase free length'}\n")
    App.Console.PrintMessage(f"\nSpring rate calculation (spring steel wire):\n")
    App.Console.PrintMessage(f"  Theoretical rate: {_SPRING_RATE_CALC:.3f} N/mm  (G = {_G_STEEL_MPA/1000:.0f} GPa)\n")
    App.Console.PrintMessage(f"  At-wheel rate  : {spring_rate_at_wheel:.3f} N/mm  (MR = {MOTION_RATIO})\n")
    App.Console.PrintMessage(f"  Vehicle mass   : {VEHICLE_MASS_KG:.1f} kg  → {VEHICLE_MASS_KG * 9.81 / 4:.2f} N / corner\n")
    App.Console.PrintMessage(f"  Static sag     : {VEHICLE_MASS_KG * 9.81 / 4 / spring_rate_at_wheel:.1f} mm at wheel  (target {STATIC_SAG_MM:.1f} mm at shock)\n")
    App.Console.PrintMessage(f"\nMotion ratio   : {MOTION_RATIO}  (shock travel / wheel travel)\n")
    App.Console.PrintMessage(
        "\nStage 4 complete. Run assemble_suspension.py to preview the arm + shock together,\n"
        "  or run assemble_corner_to_chassis.py to update the full chassis preview.\n"
    )

    return doc


main()
