# =============================================================================
# RC DS2 — TIRE STL IMPORTER (v0.1)
# =============================================================================
# Imports rc-ds2-tire-tread.stl and positions it on the left-hand front wheel
# axis so it sits correctly alongside the chassis skeleton, arm, and upright
# in the assembly preview document.
#
# Run this in FreeCAD (1.0+) via the Macro Editor or Python Console.
# Ideally run *after* assemble_corner_to_chassis.py so the tire lands in the
# already-open RC_DS2_Assembly_Preview document.
#
# POSITIONING LOGIC
# -----------------
# The STL was exported from OpenSCAD with the tire's revolution axis along Z
# and the cross-section in the XY plane:
#
#   STL frame   X: −75 .. +75 mm  (radial)
#               Y: −75 .. +75 mm  (radial)
#               Z: −31 .. +31 mm  (axial / tire width)
#
# In the FreeCAD assembly the wheel axis runs along Y.  Two steps are needed:
#
#   Step 1 — rotate +90° about the X-axis
#               new_Y = −old_Z   →  tire width now runs in ±Y
#               new_Z = +old_Y   →  tire radius now spans Z
#             The wheel's revolution axis (old Z) now points in +Y. ✓
#
#   Step 2 — translate to the LHF wheel axis centre (X=165, Y=−143, Z=75)
#
# After placement:
#   Tire OD      : Ø150 mm — bottom face at Z ≈ 0 (ground plane)
#   Tire width   : 62 mm   — Y = −174 .. −112 mm
#   Wheel centre : (165, −143, 75)
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

# Name of the STL file relative to the repo root (STL sub-directory).
TIRE_STL_FILENAME = "rc-ds2-tire-tread.stl"
PODS_STL_FILENAME = "rc-ds2-pods.stl"

# Set to True to also import the pods/rim STL on the same wheel axis.
IMPORT_PODS = False

# Name of the target document.  If this document is open the tire is added
# there; otherwise a new document is created.
TARGET_DOC_NAME = "RC_DS2_Assembly_Preview"

# Name for the imported tire object in the model tree.
TIRE_OBJECT_NAME  = "Tire_LHF"
PODS_OBJECT_NAME  = "RimPods_LHF"

# Tire colour and transparency (for visual consistency with the assembly).
TIRE_COLOUR       = (0.10, 0.10, 0.10)   # near-black TPU
TIRE_TRANSPARENCY = 0

PODS_COLOUR       = (0.75, 0.75, 0.85)   # light grey PETG
PODS_TRANSPARENCY = 0

# =============================================================================
# WHEEL AXIS PARAMETERS  (shared with all stage macros)
# =============================================================================

WHEELBASE  = 330.0
TRACK_WIDTH = 286.0
TIRE_OUTER_DIAMETER = 150.0

WHEEL_AXIS_X = WHEELBASE / 2.0                 # 165.0 mm
WHEEL_AXIS_Y = -(TRACK_WIDTH / 2.0)            # -143.0 mm
WHEEL_AXIS_Z = TIRE_OUTER_DIAMETER / 2.0       #  75.0 mm

# =============================================================================
# HELPERS
# =============================================================================


def resolve_repo_root():
    """Return the repo root directory, or None if it cannot be detected."""
    if REPO_ROOT:
        return REPO_ROOT

    # Walk the directory and parent-directory of every open document's file.
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

    # Try the macro file's own location if __file__ is defined.
    try:
        # Stage 1: macro file path fallback
        macro_dir = os.path.dirname(os.path.abspath(__file__))
        candidate = os.path.dirname(macro_dir)
        if os.path.isdir(os.path.join(candidate, stl_sub)):
            return candidate
    except NameError:
        App.Console.PrintWarning(
            "  Tire importer: __file__ is not defined (running from Macro Editor).\n"
            "  Set REPO_ROOT at the top of the script if auto-detection fails.\n"
        )

    return None


def get_or_create_document(doc_name):
    existing = App.listDocuments().get(doc_name)
    if existing:
        return existing
    return App.newDocument(doc_name)


def add_group(doc, name):
    return doc.addObject("App::DocumentObjectGroup", name)


def import_mesh_with_placement(doc, stl_path, obj_name, rotation, translation):
    """Read an STL file, apply a rotation+translation Placement, and add to doc.

    Parameters
    ----------
    rotation    : App.Rotation  — orientation to apply (see module header for tire)
    translation : App.Vector    — world-space position of the mesh origin
    """
    mesh = Mesh.Mesh()
    mesh.read(stl_path)

    mesh_obj = doc.addObject("Mesh::Feature", obj_name)
    mesh_obj.Mesh = mesh
    mesh_obj.Placement = App.Placement(translation, rotation)
    return mesh_obj


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
    pods_path = os.path.join(stl_dir, PODS_STL_FILENAME)

    if not os.path.isfile(tire_path):
        App.Console.PrintError(f"Tire STL not found: {tire_path}\n")
        return

    App.Console.PrintMessage(f"Repository root : {repo_root}\n")
    App.Console.PrintMessage(f"Tire STL        : {tire_path}\n")

    # ---- Open or find the target document ------------------------------------

    doc = get_or_create_document(TARGET_DOC_NAME)
    App.Console.PrintMessage(f"Target document : {doc.Name}\n\n")

    # ---- Placement: rotate +90° about X, then translate to wheel axis --------
    #
    # The STL has the wheel's revolution axis along Z.
    # Rotating +90° about X maps:  Z → +Y  (revolution axis now along +Y ✓)
    #                              Y → −Z  (radial direction now spans Z ✓)
    # Translating to (WHEEL_AXIS_X, WHEEL_AXIS_Y, WHEEL_AXIS_Z) centres the
    # tire on the LHF wheel axis.

    rotation    = App.Rotation(App.Vector(1, 0, 0), 90)
    translation = App.Vector(WHEEL_AXIS_X, WHEEL_AXIS_Y, WHEEL_AXIS_Z)

    # ---- Import tire ---------------------------------------------------------

    App.Console.PrintMessage("Importing tire mesh...\n")

    # Remove any previous instance with the same name to allow re-running.
    existing = doc.getObject(TIRE_OBJECT_NAME)
    if existing:
        doc.removeObject(TIRE_OBJECT_NAME)

    tire_obj = import_mesh_with_placement(
        doc, tire_path, TIRE_OBJECT_NAME, rotation, translation,
    )
    apply_style(tire_obj, TIRE_COLOUR, TIRE_TRANSPARENCY)
    App.Console.PrintMessage(f"  Added '{TIRE_OBJECT_NAME}' to '{doc.Name}'.\n")

    # ---- Import pods / rim (optional) ----------------------------------------

    if IMPORT_PODS and os.path.isfile(pods_path):
        App.Console.PrintMessage("Importing pods/rim mesh...\n")
        existing_pods = doc.getObject(PODS_OBJECT_NAME)
        if existing_pods:
            doc.removeObject(PODS_OBJECT_NAME)

        pods_obj = import_mesh_with_placement(
            doc, pods_path, PODS_OBJECT_NAME, rotation, translation,
        )
        apply_style(pods_obj, PODS_COLOUR, PODS_TRANSPARENCY)
        App.Console.PrintMessage(f"  Added '{PODS_OBJECT_NAME}' to '{doc.Name}'.\n")
    elif IMPORT_PODS:
        App.Console.PrintWarning(f"  Pods STL not found, skipping: {pods_path}\n")

    doc.recompute()

    # ---- Fit view ------------------------------------------------------------

    try:
        import FreeCADGui as Gui
        Gui.SendMsgToActiveView("ViewFit")
    except Exception:
        pass

    # ---- Summary -------------------------------------------------------------

    tire_bottom_z  = WHEEL_AXIS_Z - TIRE_OUTER_DIAMETER / 2.0
    tire_top_z     = WHEEL_AXIS_Z + TIRE_OUTER_DIAMETER / 2.0
    tire_y_inner   = WHEEL_AXIS_Y + 31.0    # half of 62 mm width
    tire_y_outer   = WHEEL_AXIS_Y - 31.0

    App.Console.PrintMessage("\n=== Tire STL Import Summary ===\n")
    App.Console.PrintMessage(f"Wheel axis centre : ({WHEEL_AXIS_X:.1f}, {WHEEL_AXIS_Y:.1f}, {WHEEL_AXIS_Z:.1f})\n")
    App.Console.PrintMessage(f"Tire bottom Z     : {tire_bottom_z:.1f} mm  (should be ≈ 0 = ground)\n")
    App.Console.PrintMessage(f"Tire top Z        : {tire_top_z:.1f} mm\n")
    App.Console.PrintMessage(f"Tire Y span       : {tire_y_outer:.1f} .. {tire_y_inner:.1f} mm\n")
    App.Console.PrintMessage(f"\nToggle visibility : select '{TIRE_OBJECT_NAME}' in the model tree\n")
    App.Console.PrintMessage("                    then press Space (or right-click → Toggle visibility).\n")
    App.Console.PrintMessage("\nTire import complete.\n")


main()
