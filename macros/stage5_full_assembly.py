# =============================================================================
# RC DS2 — STAGE 5: FULL VEHICLE ASSEMBLY  (v0.1)
# =============================================================================
# Mirrors the LHF corner (Stages 1–4) to all four wheel positions, adds the
# chassis skeleton, sealed body pod system, and wheel meshes (tire + rim) to
# produce a single full-vehicle document.
#
# Run this in FreeCAD (1.0+) via the Macro Editor or Python Console.
# For the best result, run all four stage macros first so their documents are
# open in the current session.  The chassis skeleton is opened from disk
# automatically when REPO_ROOT is set (or auto-detected).
#
# CORNER POSITIONS
# ----------------
#   LHF  X = +165  Y = −143  Z = 75   Left-Hand Front  — source geometry
#   RHF  X = +165  Y = +143  Z = 75   Right-Hand Front — Y-mirror of LHF
#   LHR  X = −165  Y = −143  Z = 75   Left-Hand Rear   — X-mirror of LHF
#   RHR  X = −165  Y = +143  Z = 75   Right-Hand Rear  — XY-mirror of LHF
#
# MIRROR PLANES
# -------------
#   Y-mirror  : XZ plane at Y = 0    App.Vector normal (0, 1, 0)
#   X-mirror  : YZ plane at X = 0    App.Vector normal (1, 0, 0)
#   XY-mirror : both planes applied sequentially
#
# MIRRORING NOTE
# --------------
# Stage macros encode shape positions as absolute App.Vector coordinates in
# shape vertex data; the FreeCAD Placement stays at identity.  Part.Shape
# .mirror(point, normal) therefore maps these world-coordinate shapes to the
# three remaining corners without any Placement arithmetic.
#
# OUTPUT DOCUMENT: RC_DS2_Full_Assembly_v01
# -----------------------------------------
#   ├─ Chassis
#   ├─ BodyPods
#   ├─ Corner_LHF   — Stage 1–4 shapes (source)
#   ├─ Corner_RHF   — Stage 1–4 shapes, Y-mirrored
#   ├─ Corner_LHR   — Stage 1–4 shapes, X-mirrored
#   ├─ Corner_RHR   — Stage 1–4 shapes, XY-mirrored
#   ├─ Wheel_LHF    — Tire_LHF + Rim_LHF
#   ├─ Wheel_RHF    — Tire_RHF + Rim_RHF
#   ├─ Wheel_LHR    — Tire_LHR + Rim_LHR
#   └─ Wheel_RHR    — Tire_RHR + Rim_RHR
#
# CONFIGURATION
# =============================================================================

import os

try:
    import FreeCAD as App
    import Part
    import Mesh
except ImportError:
    raise RuntimeError("This script must be run inside FreeCAD.")

# ---- User-configurable -------------------------------------------------------

# Set this to your repository root if auto-detection fails, e.g.:
#   REPO_ROOT = "/home/alice/RC-DS2-Craft"
REPO_ROOT = None

# Filenames relative to the repo root.
CHASSIS_SKELETON_FILENAME = "RC_Chassis_Skeleton.FCStd"
TIRE_STL_FILENAME         = "STL/rc-ds2-tire-tread.stl"
RIM_STL_FILENAME          = "STL/rc-ds2-rim.stl"
PODS_STL_FILENAME         = "STL/rc-ds2-pods.stl"

# Stage-macro document names (LHF source).
STAGE_DOC_NAMES = [
    "Corner_WheelEnd_LH_R1",        # Stage 1 — datum reference frame
    "Corner_HighPivotArm_LHF_v01",  # Stage 2 — high-pivot arm
    "Corner_Upright_LHF_v01",       # Stage 3 — upright / carrier
    "Corner_ShockSpring_LHF_v01",   # Stage 4 — shock absorber & spring
]

# Output document.
ASSEMBLY_DOC_NAME = "RC_DS2_Full_Assembly_v01"
REPLACE_EXISTING  = True

# =============================================================================
# VEHICLE PARAMETERS
# =============================================================================

WHEELBASE           = 330.0
TRACK_WIDTH         = 286.0
TIRE_OUTER_DIAMETER = 150.0
TIRE_WIDTH          =  62.0

WHEEL_AXIS_X = WHEELBASE / 2.0          # 165.0 mm — front axle
WHEEL_AXIS_Y = -(TRACK_WIDTH / 2.0)     # −143.0 mm — LH side
WHEEL_AXIS_Z = TIRE_OUTER_DIAMETER / 2.0  #  75.0 mm

# Four wheel-axis translations for tire/rim mesh placement.
# Mirroring in Y gives the RH side; mirroring in X gives the rear axle.
_WHEEL_POSITIONS = {
    "LHF": App.Vector( WHEEL_AXIS_X,  WHEEL_AXIS_Y, WHEEL_AXIS_Z),
    "RHF": App.Vector( WHEEL_AXIS_X, -WHEEL_AXIS_Y, WHEEL_AXIS_Z),
    "LHR": App.Vector(-WHEEL_AXIS_X,  WHEEL_AXIS_Y, WHEEL_AXIS_Z),
    "RHR": App.Vector(-WHEEL_AXIS_X, -WHEEL_AXIS_Y, WHEEL_AXIS_Z),
}

# Mirror-plane definitions: (point_on_plane, plane_normal)
_MIRROR_Y  = (App.Vector(0, 0, 0), App.Vector(0, 1, 0))   # XZ plane
_MIRROR_X  = (App.Vector(0, 0, 0), App.Vector(1, 0, 0))   # YZ plane

# =============================================================================
# VISUAL STYLES  (R, G, B), transparency 0-100
# =============================================================================

_STYLES = {
    "chassis":        ((0.55, 0.60, 0.65), 25),
    "pods":           ((0.62, 0.66, 0.72),  0),
    "stage1_ref":     ((0.20, 0.80, 0.20), 75),
    "stage2_arm":     ((0.75, 0.55, 0.15),  0),
    "stage3_upright": ((0.20, 0.50, 0.80),  0),
    "stage4_shock":   ((0.70, 0.85, 0.30),  0),
    "tire":           ((0.10, 0.10, 0.10),  0),
    "rim":            ((0.82, 0.84, 0.87),  0),
    "unknown":        ((0.70, 0.70, 0.70),  0),
}

_DOC_STYLE_MAP = {
    "Corner_WheelEnd":      "stage1_ref",
    "Corner_HighPivotArm":  "stage2_arm",
    "Corner_Upright":       "stage3_upright",
    "Corner_ShockSpring":   "stage4_shock",
}

# =============================================================================
# HELPERS
# =============================================================================


def resolve_repo_root():
    if REPO_ROOT:
        return REPO_ROOT
    for doc in App.listDocuments().values():
        if not doc.FileName:
            continue
        for candidate in (
            os.path.dirname(doc.FileName),
            os.path.dirname(os.path.dirname(doc.FileName)),
        ):
            if os.path.isfile(os.path.join(candidate, CHASSIS_SKELETON_FILENAME)):
                return candidate
    try:
        macro_dir = os.path.dirname(os.path.abspath(__file__))
        candidate = os.path.dirname(macro_dir)
        if os.path.isfile(os.path.join(candidate, CHASSIS_SKELETON_FILENAME)):
            return candidate
    except NameError:
        pass
    return None


def _style_for_doc(doc_name):
    for prefix, key in _DOC_STYLE_MAP.items():
        if doc_name.startswith(prefix):
            return _STYLES[key]
    return _STYLES["unknown"]


def apply_style(obj, colour, transparency):
    try:
        obj.ViewObject.ShapeColor   = colour
        obj.ViewObject.Transparency = transparency
    except Exception:
        pass


def add_group(doc, name):
    return doc.addObject("App::DocumentObjectGroup", name)


def add_shape(doc, name, shape, grp=None):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    if grp is not None:
        grp.addObject(obj)
    return obj


def mirror_shape(shape, mirror_def):
    """Return shape mirrored through the plane described by mirror_def = (point, normal)."""
    pt, nrm = mirror_def
    return shape.mirror(pt, nrm)


# =============================================================================
# CHASSIS SKELETON
# =============================================================================

def collect_chassis(repo_root, asm_doc):
    """Open (or find) the chassis skeleton and copy its shapes into asm_doc."""
    grp = add_group(asm_doc, "Chassis")
    colour, transparency = _STYLES["chassis"]

    # Already open?
    chassis_doc = None
    for doc in App.listDocuments().values():
        if doc.FileName and CHASSIS_SKELETON_FILENAME in doc.FileName:
            chassis_doc = doc
            break

    if chassis_doc is None and repo_root:
        path = os.path.join(repo_root, CHASSIS_SKELETON_FILENAME)
        if os.path.isfile(path):
            App.Console.PrintMessage(f"  Opening chassis from disk: {path}\n")
            chassis_doc = App.openDocument(path)

    if chassis_doc is None:
        App.Console.PrintWarning(
            "  Chassis skeleton not found — skipping.  "
            "Open RC_Chassis_Skeleton.FCStd or set REPO_ROOT.\n"
        )
        return 0

    count = 0
    for obj in chassis_doc.Objects:
        if obj.TypeId != "Part::Feature":
            continue
        if not hasattr(obj, "Shape") or obj.Shape.isNull():
            continue
        copied = add_shape(asm_doc, f"Chassis__{obj.Name}", obj.Shape.copy(), grp)
        if obj.Placement != App.Placement():
            copied.Placement = obj.Placement
        apply_style(copied, colour, transparency)
        count += 1

    App.Console.PrintMessage(f"  Chassis shapes copied : {count}\n")
    return count


# =============================================================================
# BODY PODS
# =============================================================================

def collect_body_pods(repo_root, asm_doc):
    """Import the pods STL at the origin (no rotation needed — same frame)."""
    if repo_root is None:
        App.Console.PrintWarning("  Repo root unknown — skipping body pods.\n")
        return

    path = os.path.join(repo_root, PODS_STL_FILENAME)
    if not os.path.isfile(path):
        App.Console.PrintWarning(f"  Body pods STL not found: {path}  (skipping)\n")
        return

    grp    = add_group(asm_doc, "BodyPods")
    mesh   = Mesh.Mesh()
    mesh.read(path)
    obj    = asm_doc.addObject("Mesh::Feature", "BodyPods_Mesh")
    obj.Mesh = mesh
    # No rotation needed: the pods SCAD uses the same X/Y/Z convention as the
    # FreeCAD assembly and the system sits on Z = 0.
    obj.Placement = App.Placement(
        App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0), 0)
    )
    grp.addObject(obj)
    colour, transparency = _STYLES["pods"]
    apply_style(obj, colour, transparency)
    App.Console.PrintMessage("  Body pods mesh added.\n")


# =============================================================================
# CORNER SHAPES (all four)
# =============================================================================

def collect_corner_shapes(asm_doc):
    """Copy and mirror LHF stage shapes into all four corner groups.

    Shapes from stage docs are at world coordinates; .mirror() maps them
    to the remaining three corners without any Placement arithmetic.
    """
    # Gather all LHF shapes from open stage documents.
    lhf_shapes = []   # list of (short_name, shape, style_key)

    for doc_name in STAGE_DOC_NAMES:
        src = App.listDocuments().get(doc_name)
        if src is None:
            App.Console.PrintWarning(
                f"  '{doc_name}' is not open — run its stage macro for a complete assembly.\n"
            )
            continue

        colour, transparency = _style_for_doc(doc_name)

        for obj in src.Objects:
            if obj.TypeId != "Part::Feature":
                continue
            if not hasattr(obj, "Shape") or obj.Shape.isNull():
                continue
            short = f"{doc_name}__{obj.Name}"
            lhf_shapes.append((short, obj.Shape.copy(), colour, transparency))

    App.Console.PrintMessage(f"  LHF source shapes     : {len(lhf_shapes)}\n")

    # Build one group per corner.
    corners = {
        "LHF": None,            # identity — source
        "RHF": (_MIRROR_Y,),            # Y-mirror
        "LHR": (_MIRROR_X,),            # X-mirror
        "RHR": (_MIRROR_Y, _MIRROR_X),  # Y-mirror then X-mirror
    }

    for tag, mirrors in corners.items():
        grp = add_group(asm_doc, f"Corner_{tag}")
        for short, src_shape, colour, transparency in lhf_shapes:
            shape = src_shape.copy()
            if mirrors:
                for m in mirrors:
                    shape = mirror_shape(shape, m)
            obj = add_shape(asm_doc, f"{tag}__{short}", shape, grp)
            apply_style(obj, colour, transparency)

    App.Console.PrintMessage(
        f"  Corner groups written : LHF  RHF  LHR  RHR  ({len(lhf_shapes)} shapes each)\n"
    )


# =============================================================================
# WHEEL MESHES (tire + rim × 4 corners)
# =============================================================================

def collect_wheel_meshes(repo_root, asm_doc):
    """Import tire and rim STLs at each of the four wheel positions."""
    if repo_root is None:
        App.Console.PrintWarning("  Repo root unknown — skipping wheel meshes.\n")
        return

    tire_path = os.path.join(repo_root, TIRE_STL_FILENAME)
    rim_path  = os.path.join(repo_root, RIM_STL_FILENAME)

    missing = [p for p in (tire_path, rim_path) if not os.path.isfile(p)]
    if missing:
        App.Console.PrintWarning(
            "  Missing wheel STL file(s):\n"
            + "".join(f"    {p}\n" for p in missing)
            + "  Run import_wheel.py or check STL/ directory.\n"
        )
        if not os.path.isfile(tire_path) and not os.path.isfile(rim_path):
            return

    # Both STL files are in the same native frame: revolution axis = Z,
    # centred at origin.  Rotating +90° about X aligns the revolution axis
    # with the assembly's wheel axis (Y).  The translation then places the
    # centre at each wheel position.
    rotation = App.Rotation(App.Vector(1, 0, 0), 90)

    for tag, translation in _WHEEL_POSITIONS.items():
        grp = add_group(asm_doc, f"Wheel_{tag}")

        for (stl_path, obj_name, style_key) in (
            (tire_path, f"Tire_{tag}", "tire"),
            (rim_path,  f"Rim_{tag}",  "rim"),
        ):
            if not os.path.isfile(stl_path):
                App.Console.PrintWarning(
                    f"  {obj_name}: STL not found, skipping.\n"
                )
                continue
            mesh = Mesh.Mesh()
            mesh.read(stl_path)
            mobj = asm_doc.addObject("Mesh::Feature", obj_name)
            mobj.Mesh = mesh
            mobj.Placement = App.Placement(translation, rotation)
            grp.addObject(mobj)
            colour, transparency = _STYLES[style_key]
            apply_style(mobj, colour, transparency)

    App.Console.PrintMessage("  Wheel meshes placed   : LHF  RHF  LHR  RHR\n")


# =============================================================================
# MAIN
# =============================================================================


def main():
    repo_root = resolve_repo_root()
    if repo_root:
        App.Console.PrintMessage(f"Repository root : {repo_root}\n")
    else:
        App.Console.PrintWarning(
            "Repository root not detected.  Set REPO_ROOT at the top of this "
            "script to load the chassis skeleton, pods, and wheel STL files.\n"
        )

    # ---- Create or replace the assembly document ----------------------------

    if REPLACE_EXISTING and ASSEMBLY_DOC_NAME in App.listDocuments():
        App.closeDocument(ASSEMBLY_DOC_NAME)

    asm_doc = App.newDocument(ASSEMBLY_DOC_NAME)
    App.Console.PrintMessage(f"\nAssembly document : '{ASSEMBLY_DOC_NAME}'\n\n")

    # ---- Populate the assembly ----------------------------------------------

    App.Console.PrintMessage("[ Chassis ]\n")
    collect_chassis(repo_root, asm_doc)

    App.Console.PrintMessage("\n[ Body pods ]\n")
    collect_body_pods(repo_root, asm_doc)

    App.Console.PrintMessage("\n[ Corner geometry — Stages 1-4 ]\n")
    collect_corner_shapes(asm_doc)

    App.Console.PrintMessage("\n[ Wheel meshes — tire + rim × 4 ]\n")
    collect_wheel_meshes(repo_root, asm_doc)

    asm_doc.recompute()

    # ---- Fit view ------------------------------------------------------------

    try:
        import FreeCADGui as Gui
        Gui.SendMsgToActiveView("ViewFit")
    except Exception:
        pass

    # ---- Summary -------------------------------------------------------------

    App.Console.PrintMessage("\n=== Full Vehicle Assembly Summary ===\n")
    App.Console.PrintMessage(f"  Wheelbase        : {WHEELBASE:.0f} mm\n")
    App.Console.PrintMessage(f"  Track width      : {TRACK_WIDTH:.0f} mm\n")
    App.Console.PrintMessage(f"  Tire OD          : {TIRE_OUTER_DIAMETER:.0f} mm\n")
    App.Console.PrintMessage(
        f"  Front axle X     : ±{WHEEL_AXIS_X:.0f} mm  "
        f"(rear axle at X = −{WHEEL_AXIS_X:.0f} mm)\n"
    )
    App.Console.PrintMessage(
        f"  Wheel centre Y   : ±{abs(WHEEL_AXIS_Y):.0f} mm  "
        f"(LH = −{abs(WHEEL_AXIS_Y):.0f}, RH = +{abs(WHEEL_AXIS_Y):.0f})\n"
    )
    App.Console.PrintMessage(
        f"  Wheel centre Z   :  {WHEEL_AXIS_Z:.0f} mm  (ground plane = Z 0)\n"
    )
    App.Console.PrintMessage(
        "\nDocument groups:\n"
        "  Chassis       — skeleton rails, pods, carrier pads\n"
        "  BodyPods      — sealed electronics + buoyancy pod system\n"
        "  Corner_LHF/RHF/LHR/RHR — arm, upright, shock, spring\n"
        "  Wheel_LHF/RHF/LHR/RHR  — tire + beadlock rim mesh\n"
    )
    App.Console.PrintMessage("Full vehicle assembly complete.\n")


main()
