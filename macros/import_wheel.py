# =============================================================================
# RC DS2 — WHEEL IMPORTER  (supersedes import_tire_stl)
# =============================================================================
# Imports rc-ds2-tire-tread.stl AND rc-ds2-rim.stl and positions both on the
# left-hand front wheel axis so they sit correctly alongside the chassis
# skeleton, arm, and upright in the assembly preview document.
#
# Run this in FreeCAD (1.0+) via the Macro Editor or Python Console.
# Ideally run *after* assemble_corner_to_chassis.py so the wheel lands in the
# already-open RC_DS2_Assembly_Preview document.
#
# POSITIONING LOGIC
# -----------------
# Both STL files were exported from OpenSCAD with the wheel's revolution axis
# along Z and the cross-section centred at the XY origin:
#
#   STL frame   X: −75 .. +75 mm  (radial, tire)
#               Y: −75 .. +75 mm  (radial, tire)
#               Z: −31 .. +31 mm  (axial / tire and rim width)
#
# The rim body (rim_body() in the SCAD) is centred at Z = 0 and shares the
# same axial span as the tire, so both meshes use an identical placement.
#
# In the FreeCAD assembly the wheel axis runs along Y.  Two steps are needed:
#
#   Step 1 — rotate +90° about the X-axis
#               new_Y = −old_Z   →  width now runs in ±Y
#               new_Z = +old_Y   →  radius now spans Z
#             The revolution axis (old Z) now points in +Y. ✓
#
#   Step 2 — translate to the LHF wheel axis centre (X=165, Y=−143, Z=75)
#
# After placement:
#   Tire OD          : Ø150 mm — bottom face at Z ≈ 0 (ground plane)
#   Tire / rim width : 62 mm   — Y = −174 .. −112 mm
#   Wheel centre     : (165, −143, 75)
#   Rim barrel Ø     : 109.4 mm (bead seat Ø − 0.6 mm fit clearance)
#
# CONFIGURATION
# =============================================================================

import os

try:
    import FreeCAD as App
    import Mesh
except ImportError:
    raise RuntimeError("This script must be run inside FreeCAD.")

# ---- User-configurable -------------------------------------------------------

# Set this to the absolute path of your repository clone if auto-detection
# fails, e.g.:
#   REPO_ROOT = "/home/alice/RC-DS2-Craft"
# Leave as None to auto-detect from open document file paths.
REPO_ROOT = None

# STL filenames relative to the repo STL sub-directory.
TIRE_STL_FILENAME = "rc-ds2-tire-tread.stl"
RIM_STL_FILENAME  = "rc-ds2-rim.stl"

# Name of the target document.  If this document is open the wheel is added
# there; otherwise a new document is created.
TARGET_DOC_NAME = "RC_DS2_Assembly_Preview"

# Object names in the FreeCAD model tree.
TIRE_OBJECT_NAME = "Tire_LHF"
RIM_OBJECT_NAME  = "Rim_LHF"

# Visual style (R, G, B), transparency 0-100.
TIRE_COLOUR       = (0.10, 0.10, 0.10)   # near-black TPU
TIRE_TRANSPARENCY = 0
RIM_COLOUR        = (0.82, 0.84, 0.87)   # light silver PETG
RIM_TRANSPARENCY  = 0

# =============================================================================
# WHEEL AXIS PARAMETERS  (shared with all stage macros)
# =============================================================================

WHEELBASE           = 330.0
TRACK_WIDTH         = 286.0
TIRE_OUTER_DIAMETER = 150.0

WHEEL_AXIS_X = WHEELBASE / 2.0                  # 165.0 mm
WHEEL_AXIS_Y = -(TRACK_WIDTH / 2.0)             # −143.0 mm
WHEEL_AXIS_Z = TIRE_OUTER_DIAMETER / 2.0        #  75.0 mm

# =============================================================================
# HELPERS
# =============================================================================


def resolve_repo_root():
    """Return the repo root directory, or None if it cannot be detected."""
    if REPO_ROOT:
        return REPO_ROOT

    stl_sub = "STL"
    for doc in App.listDocuments().values():
        if not doc.FileName:
            continue
        for candidate in (
            os.path.dirname(doc.FileName),
            os.path.dirname(os.path.dirname(doc.FileName)),
        ):
            if os.path.isdir(os.path.join(candidate, stl_sub)):
                return candidate

    try:
        macro_dir = os.path.dirname(os.path.abspath(__file__))
        candidate = os.path.dirname(macro_dir)
        if os.path.isdir(os.path.join(candidate, stl_sub)):
            return candidate
    except NameError:
        App.Console.PrintWarning(
            "  Wheel importer: __file__ is not defined (running from Macro Editor).\n"
            "  Set REPO_ROOT at the top of the script if auto-detection fails.\n"
        )

    return None


def get_or_create_document(doc_name):
    existing = App.listDocuments().get(doc_name)
    if existing:
        return existing
    return App.newDocument(doc_name)


def import_mesh_with_placement(doc, stl_path, obj_name, rotation, translation):
    """Read an STL file, apply a rotation + translation Placement, add to doc."""
    mesh = Mesh.Mesh()
    mesh.read(stl_path)
    obj = doc.addObject("Mesh::Feature", obj_name)
    obj.Mesh = mesh
    obj.Placement = App.Placement(translation, rotation)
    return obj


def apply_style(obj, colour, transparency):
    try:
        obj.ViewObject.ShapeColor   = colour
        obj.ViewObject.Transparency = transparency
    except Exception:
        pass


# =============================================================================
# MAIN
# =============================================================================


def main():
    # ---- Locate repo and STL files ------------------------------------------

    repo_root = resolve_repo_root()
    if repo_root is None:
        App.Console.PrintError(
            "Cannot locate the repository root.  "
            "Set REPO_ROOT at the top of this script.\n"
        )
        return

    stl_dir   = os.path.join(repo_root, "STL")
    tire_path = os.path.join(stl_dir, TIRE_STL_FILENAME)
    rim_path  = os.path.join(stl_dir, RIM_STL_FILENAME)

    if not os.path.isfile(tire_path):
        App.Console.PrintError(f"Tire STL not found: {tire_path}\n")
        return

    if not os.path.isfile(rim_path):
        App.Console.PrintError(
            f"Rim STL not found: {rim_path}\n"
            "  Export rc-ds2-wheel-exploded.scad with part='rim_body' and save\n"
            "  the result as STL/rc-ds2-rim.stl, then re-run this macro.\n"
        )
        return

    App.Console.PrintMessage(f"Repository root : {repo_root}\n")
    App.Console.PrintMessage(f"Tire STL        : {tire_path}\n")
    App.Console.PrintMessage(f"Rim STL         : {rim_path}\n")

    # ---- Open or find the target document ------------------------------------

    doc = get_or_create_document(TARGET_DOC_NAME)
    App.Console.PrintMessage(f"Target document : {doc.Name}\n\n")

    # ---- Placement: rotate +90° about X, then translate to wheel axis --------
    #
    # Both STL files share the same native coordinate frame:
    #   revolution axis = Z, centred at origin, width spans Z = −31 .. +31 mm.
    # Rotating +90° about X maps Z → +Y so the revolution axis aligns with
    # the assembly's wheel axis.  A single Placement handles both meshes.

    rotation    = App.Rotation(App.Vector(1, 0, 0), 90)
    translation = App.Vector(WHEEL_AXIS_X, WHEEL_AXIS_Y, WHEEL_AXIS_Z)

    # ---- Import tire ---------------------------------------------------------

    App.Console.PrintMessage("Importing tire mesh...\n")
    existing = doc.getObject(TIRE_OBJECT_NAME)
    if existing:
        doc.removeObject(TIRE_OBJECT_NAME)

    tire_obj = import_mesh_with_placement(
        doc, tire_path, TIRE_OBJECT_NAME, rotation, translation,
    )
    apply_style(tire_obj, TIRE_COLOUR, TIRE_TRANSPARENCY)
    App.Console.PrintMessage(f"  Added '{TIRE_OBJECT_NAME}' to '{doc.Name}'.\n")

    # ---- Import rim ----------------------------------------------------------

    App.Console.PrintMessage("Importing rim mesh...\n")
    existing_rim = doc.getObject(RIM_OBJECT_NAME)
    if existing_rim:
        doc.removeObject(RIM_OBJECT_NAME)

    rim_obj = import_mesh_with_placement(
        doc, rim_path, RIM_OBJECT_NAME, rotation, translation,
    )
    apply_style(rim_obj, RIM_COLOUR, RIM_TRANSPARENCY)
    App.Console.PrintMessage(f"  Added '{RIM_OBJECT_NAME}' to '{doc.Name}'.\n")

    doc.recompute()

    # ---- Fit view ------------------------------------------------------------

    try:
        import FreeCADGui as Gui
        Gui.SendMsgToActiveView("ViewFit")
    except Exception:
        pass

    # ---- Summary -------------------------------------------------------------

    tire_bottom_z = WHEEL_AXIS_Z - TIRE_OUTER_DIAMETER / 2.0
    tire_top_z    = WHEEL_AXIS_Z + TIRE_OUTER_DIAMETER / 2.0
    tire_y_inner  = WHEEL_AXIS_Y + 31.0
    tire_y_outer  = WHEEL_AXIS_Y - 31.0

    App.Console.PrintMessage("\n=== Wheel Import Summary ===\n")
    App.Console.PrintMessage(
        f"Wheel axis centre     : ({WHEEL_AXIS_X:.1f}, {WHEEL_AXIS_Y:.1f}, {WHEEL_AXIS_Z:.1f})\n"
    )
    App.Console.PrintMessage(
        f"Tire bottom Z         : {tire_bottom_z:.1f} mm  (should be ≈ 0 = ground)\n"
    )
    App.Console.PrintMessage(f"Tire top Z            : {tire_top_z:.1f} mm\n")
    App.Console.PrintMessage(
        f"Tire / rim Y span     : {tire_y_outer:.1f} .. {tire_y_inner:.1f} mm\n"
    )
    App.Console.PrintMessage(
        "Rim barrel Ø          : 109.4 mm  (bead seat Ø 110 − 0.6 mm fit clearance)\n"
    )
    App.Console.PrintMessage(
        f"\nToggle tire : select '{TIRE_OBJECT_NAME}' in the model tree, press Space.\n"
        f"Toggle rim  : select '{RIM_OBJECT_NAME}'  in the model tree, press Space.\n"
    )
    App.Console.PrintMessage("\nWheel import complete.\n")


main()
