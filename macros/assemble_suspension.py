# =============================================================================
# RC DS2 — SUSPENSION ASSEMBLER: ARM + SHOCK  (v0.1)
# =============================================================================
# Collects the Stage-2 arm and Stage-4 shock/spring into a single suspension
# sub-assembly document and annotates both shock mount points with coloured
# sphere markers and a placeholder chassis tower stub.
#
# Run this in FreeCAD (1.0+) via the Macro Editor or Python Console.
# Stage-2 (Corner_HighPivotArm_LHF_v01) and Stage-4 (Corner_ShockSpring_LHF_v01)
# must be open in the same session, or run those macros first.
#
# OUTPUT DOCUMENT: Suspension_LHF_v01
# ------------------------------------
#   ├─ Arm_Stage2        — shapes from Corner_HighPivotArm_LHF_v01
#   ├─ Shock_Stage4      — shapes from Corner_ShockSpring_LHF_v01
#   ├─ MountPoints
#   │     Mount_Lower    — Ø8 mm sphere at (153, −95.5, 80.5)  — orange
#   │     Mount_Upper    — Ø8 mm sphere at (147, −38, 165)      — cyan
#   └─ TowerStub
#         Tower_Body     — 14 × 8 mm rib, Z = 100 .. 165 mm
#         Tower_Base     — 28 × 20 mm base plate, Z = 94 .. 100 mm
#
# SHOCK MOUNT COORDINATES  (from Stage 2 / Stage 4 parameter blocks)
# -------------------------------------------------------------------
#   Lower (arm boss)   : X = 153.0,  Y = −95.5,  Z =  80.5
#   Upper (tower boss) : X = 147.0,  Y = −38.0,  Z = 165.0
#
# Coordinate system (matches all stage macros):
#   X = longitudinal (rear → front)
#   Y = lateral (positive = right, negative = left)
#   Z = vertical (up)
#
# TOWER STUB NOTE
# ---------------
# The tower geometry here is a first-approximation rib sized to clear the
# existing carrier mount pad and reach the upper clevis pin.  It will be
# replaced by detailed printable geometry in Stage 5.  The base plate sits
# on the CARRIER_MOUNT_Z = 94 mm plane; the rib extends to the upper mount
# at Z = 165 mm.
# =============================================================================

import math

try:
    import FreeCAD as App
    import Part
except ImportError:
    raise RuntimeError("This script must be run inside FreeCAD.")

# =============================================================================
# CONFIGURATION
# =============================================================================

# Source documents produced by the stage macros.
ARM_DOC_NAME   = "Corner_HighPivotArm_LHF_v01"
SHOCK_DOC_NAME = "Corner_ShockSpring_LHF_v01"

# Output document name.
DOC_NAME         = "Suspension_LHF_v01"
REPLACE_EXISTING = True

# =============================================================================
# SHOCK MOUNT COORDINATES
# (from Stage 2: SHOCK_X / SHOCK_Y / SHOCK_Z and Stage 4 upper-mount block)
# =============================================================================

SHOCK_LOWER_X =  153.0   # mm — arm mid-span boss (Stage 2: AXLE_PAD_CENTER_X + 6)
SHOCK_LOWER_Y =  -95.5   # mm — arm mid-span boss (Stage 2: ARM_SPAR_MID_Y − 5)
SHOCK_LOWER_Z =   80.5   # mm — arm mid-span boss (Stage 2: ARM_SPAR_MID_CZ − 4)

SHOCK_UPPER_X =  147.0   # mm — chassis tower boss (Stage 4: AXLE_PAD_CENTER_X)
SHOCK_UPPER_Y =  -38.0   # mm — chassis tower boss (Stage 4: chassis pivot Y)
SHOCK_UPPER_Z =  165.0   # mm — chassis tower boss (Stage 4: tower top)

# =============================================================================
# CHASSIS TOWER STUB GEOMETRY
# =============================================================================

# Base plate: sits on the carrier mount plane (Z = CARRIER_MOUNT_Z = 94 mm).
TOWER_BASE_Z    =  94.0   # mm — carrier mount plane
TOWER_BASE_H    =   6.0   # mm — plate thickness
TOWER_BASE_LEN  =  28.0   # mm in X, centred on SHOCK_UPPER_X
TOWER_BASE_WID  =  20.0   # mm in Y, centred on SHOCK_UPPER_Y

# Rib: rises from the top of the base plate to the upper mount point.
TOWER_RIB_LEN   =  14.0   # mm in X, centred on SHOCK_UPPER_X
TOWER_RIB_WID   =   8.0   # mm in Y, centred on SHOCK_UPPER_Y

# Mount-point marker sphere radius.
MOUNT_MARKER_R  =   4.0   # mm

# =============================================================================
# VISUAL STYLES
# =============================================================================

_STYLES = {
    "arm":          ((0.75, 0.55, 0.15),  0),   # amber — arm body
    "shock":        ((0.70, 0.85, 0.30),  0),   # spring green — shock/spring
    "lower_mount":  ((0.95, 0.50, 0.10),  0),   # orange — lower clevis
    "upper_mount":  ((0.10, 0.78, 0.90),  0),   # cyan — upper tower boss
    "tower":        ((0.55, 0.60, 0.65), 45),   # grey, semi-transparent stub
}

# =============================================================================
# HELPERS
# =============================================================================


def get_or_create_document(doc_name, replace=False):
    existing = App.listDocuments().get(doc_name)
    if existing:
        if replace:
            App.closeDocument(doc_name)
            return App.newDocument(doc_name)
        return existing
    return App.newDocument(doc_name)


def add_group(doc, name, parent=None):
    grp = doc.addObject("App::DocumentObjectGroup", name)
    if parent is not None:
        parent.addObject(grp)
    return grp


def add_shape(doc, name, shape, parent=None):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    if parent is not None:
        parent.addObject(obj)
    return obj


def apply_style(obj, colour, transparency):
    try:
        obj.ViewObject.ShapeColor   = colour
        obj.ViewObject.Transparency = transparency
    except Exception:
        pass


def copy_doc_shapes(src_doc_name, dest_doc, grp, colour, transparency):
    """Copy every Part::Feature shape from src_doc_name into dest_doc under grp.

    Shapes built by stage macros use absolute App.Vector coordinates encoded
    in the shape vertex data; the FreeCAD Placement stays at identity.  A plain
    shape.copy() therefore reproduces the correct world position.

    Returns the number of shapes copied.
    """
    src = App.listDocuments().get(src_doc_name)
    if src is None:
        App.Console.PrintWarning(
            f"  '{src_doc_name}' is not open — skipping.  "
            f"Run the corresponding stage macro first.\n"
        )
        return 0

    count = 0
    for obj in src.Objects:
        if obj.TypeId != "Part::Feature":
            continue
        if not hasattr(obj, "Shape") or obj.Shape.isNull():
            continue

        copy_name = f"{grp.Name}__{obj.Name}"
        copied = add_shape(dest_doc, copy_name, obj.Shape.copy(), grp)
        if obj.Placement != App.Placement():
            copied.Placement = obj.Placement
        apply_style(copied, colour, transparency)
        count += 1

    return count


# =============================================================================
# MOUNT-POINT MARKER
# =============================================================================

def make_mount_marker(centre, radius):
    """Solid sphere centred at centre with given radius."""
    return Part.makeSphere(radius, centre)


# =============================================================================
# CHASSIS TOWER STUB
# =============================================================================

def build_tower_stub():
    """Return (rib_shape, base_shape) for a minimal shock-tower placeholder.

    The base plate spans Z = TOWER_BASE_Z .. TOWER_BASE_Z + TOWER_BASE_H.
    The rib rises from the top of the base plate to SHOCK_UPPER_Z.
    Both solids are centred on (SHOCK_UPPER_X, SHOCK_UPPER_Y) in X and Y.
    """
    rib_z0  = TOWER_BASE_Z + TOWER_BASE_H
    rib_h   = SHOCK_UPPER_Z - rib_z0

    rib = Part.makeBox(
        TOWER_RIB_LEN, TOWER_RIB_WID, rib_h,
        App.Vector(
            SHOCK_UPPER_X - TOWER_RIB_LEN / 2.0,
            SHOCK_UPPER_Y - TOWER_RIB_WID / 2.0,
            rib_z0,
        ),
    )

    base = Part.makeBox(
        TOWER_BASE_LEN, TOWER_BASE_WID, TOWER_BASE_H,
        App.Vector(
            SHOCK_UPPER_X - TOWER_BASE_LEN / 2.0,
            SHOCK_UPPER_Y - TOWER_BASE_WID / 2.0,
            TOWER_BASE_Z,
        ),
    )

    return rib, base


# =============================================================================
# MAIN
# =============================================================================


def main():
    doc = get_or_create_document(DOC_NAME, replace=REPLACE_EXISTING)
    App.Console.PrintMessage(f"Output document : {doc.Name}\n\n")

    # ---- Arm (Stage 2) -------------------------------------------------------

    grp_arm = add_group(doc, "Arm_Stage2")
    n_arm = copy_doc_shapes(ARM_DOC_NAME, doc, grp_arm, *_STYLES["arm"])
    App.Console.PrintMessage(f"  Arm shapes copied     : {n_arm}\n")

    # ---- Shock / spring (Stage 4) --------------------------------------------

    grp_shock = add_group(doc, "Shock_Stage4")
    n_shock = copy_doc_shapes(SHOCK_DOC_NAME, doc, grp_shock, *_STYLES["shock"])
    App.Console.PrintMessage(f"  Shock shapes copied   : {n_shock}\n")

    # ---- Mount-point markers -------------------------------------------------

    grp_mounts = add_group(doc, "MountPoints")

    lower_pt = App.Vector(SHOCK_LOWER_X, SHOCK_LOWER_Y, SHOCK_LOWER_Z)
    upper_pt = App.Vector(SHOCK_UPPER_X, SHOCK_UPPER_Y, SHOCK_UPPER_Z)

    lower_obj = add_shape(
        doc, "Mount_Lower", make_mount_marker(lower_pt, MOUNT_MARKER_R), grp_mounts
    )
    apply_style(lower_obj, *_STYLES["lower_mount"])

    upper_obj = add_shape(
        doc, "Mount_Upper", make_mount_marker(upper_pt, MOUNT_MARKER_R), grp_mounts
    )
    apply_style(upper_obj, *_STYLES["upper_mount"])

    App.Console.PrintMessage("  Mount markers placed.\n")

    # ---- Chassis tower stub --------------------------------------------------

    grp_tower = add_group(doc, "TowerStub")
    rib_shape, base_shape = build_tower_stub()

    tower_rib  = add_shape(doc, "Tower_Body", rib_shape,  grp_tower)
    tower_base = add_shape(doc, "Tower_Base", base_shape, grp_tower)
    for obj in (tower_rib, tower_base):
        apply_style(obj, *_STYLES["tower"])

    App.Console.PrintMessage("  Tower stub placed.\n")

    doc.recompute()

    # ---- Fit view ------------------------------------------------------------

    try:
        import FreeCADGui as Gui
        Gui.SendMsgToActiveView("ViewFit")
    except Exception:
        pass

    # ---- Report --------------------------------------------------------------

    delta  = upper_pt.sub(lower_pt)
    length = delta.Length
    angle_from_vertical = math.degrees(math.acos(abs(delta.z) / length))

    App.Console.PrintMessage("\n=== Suspension Assembly Summary ===\n")
    App.Console.PrintMessage(
        f"Lower mount (arm boss)   : ({SHOCK_LOWER_X:.1f}, {SHOCK_LOWER_Y:.1f}, {SHOCK_LOWER_Z:.1f}) mm\n"
    )
    App.Console.PrintMessage(
        f"Upper mount (tower boss) : ({SHOCK_UPPER_X:.1f}, {SHOCK_UPPER_Y:.1f}, {SHOCK_UPPER_Z:.1f}) mm\n"
    )
    App.Console.PrintMessage(f"Shock axis length        : {length:.1f} mm  (fully extended)\n")
    App.Console.PrintMessage(f"Angle from vertical      : {angle_from_vertical:.1f}°\n")
    App.Console.PrintMessage(
        f"Tower base Z             : {TOWER_BASE_Z:.1f} .. {TOWER_BASE_Z + TOWER_BASE_H:.1f} mm\n"
    )
    App.Console.PrintMessage(
        f"Tower rib Z              : {TOWER_BASE_Z + TOWER_BASE_H:.1f} .. {SHOCK_UPPER_Z:.1f} mm\n"
    )
    App.Console.PrintMessage(
        f"Tower rib section (X×Y)  : {TOWER_RIB_LEN:.0f} × {TOWER_RIB_WID:.0f} mm\n"
    )
    App.Console.PrintMessage(
        "\nMount markers:\n"
        "  Orange sphere → lower clevis (arm boss)   : 'Mount_Lower'\n"
        "  Cyan sphere   → upper tower boss          : 'Mount_Upper'\n"
        "\nHardware notes:\n"
        "  Lower clevis pin : M4, axis along X, through arm boss at"
        f" ({SHOCK_LOWER_X:.0f}, {SHOCK_LOWER_Y:.1f}, {SHOCK_LOWER_Z:.1f})\n"
        "  Upper clevis pin : M4, axis along Y, through tower boss at"
        f" ({SHOCK_UPPER_X:.0f}, {SHOCK_UPPER_Y:.1f}, {SHOCK_UPPER_Z:.1f})\n"
        "  Shock body OD    : Ø12 mm  (PETG prototype / aluminium)\n"
        "  Shock rod Ø      : Ø5.5 mm\n"
        "  Spring OD        : Ø18 mm  /  free length 65 mm\n"
        "  Spring rate      : 1.0 N/mm  (spring steel) → 0.50 N/mm at wheel\n"
    )
    App.Console.PrintMessage("Suspension assembly complete.\n")


main()
