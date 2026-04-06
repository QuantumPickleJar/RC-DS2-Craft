# =============================================================================
# RC DS2 ASSEMBLY POSITIONER
# =============================================================================
# Collects the chassis skeleton and all corner-module stage documents into
# a single "RC_DS2_Assembly_Preview" document so that every part can be seen
# in its correct spatial relationship inside one 3D view.
#
# WHY THE PARTS APPEAR FAR APART IN SEPARATE DOCUMENTS
# -----------------------------------------------------
# Each stage macro creates its own FreeCAD document and places shapes at their
# absolute global coordinates (e.g. the front-left corner at X=165, Y=-143,
# Z=75).  When a single-part document is opened in isolation FreeCAD's "Fit
# All" view zooms to that part's bounding box, making it look as though it is
# at the origin.  Opening the chassis skeleton alongside shows a very different
# bounding box — hence the apparent distance.  This script copies every shape
# into one document so "Fit All" frames everything together at once.
#
# HOW POSITIONS ARE PRESERVED
# ----------------------------
# Every stage macro constructs shapes by passing absolute App.Vector
# coordinates directly to Part primitives (makeBox, makeCylinder, makeLoft,
# etc.).  The resulting shapes carry their world positions encoded in their
# vertex data; the FreeCAD Placement property stays at identity.  A plain
# shape copy (shape.copy()) therefore reproduces the same world position
# without needing any Placement transform.  The chassis skeleton .FCStd was
# built from the same global coordinate system, so once its shapes are copied
# alongside the corner parts everything lines up automatically.
#
# USAGE
# -----
#   Option A — automatic  (recommended first run)
#     Run all stage macros (Stage 1, 2, 3) first so their documents are open
#     in the same FreeCAD session, then run this script.  It will find the
#     open documents, open the chassis skeleton from disk, and build the
#     assembly.
#
#   Option B — explicit path
#     Set REPO_ROOT below to the full path of your repository clone.  The
#     script will still open the skeleton from disk even if no stage documents
#     are currently open, and will warn you which stage docs are missing.
#
# CONFIGURATION
# =============================================================================

import os

try:
    import FreeCAD as App
    import Part
except ImportError:
    raise RuntimeError("This script must be run inside FreeCAD.")

# ---- User-configurable -------------------------------------------------------

# Set this to the absolute path of your local repository clone, e.g.:
#   REPO_ROOT = "/home/alice/RC-DS2-Craft"
# Leave as None to let the script auto-detect from any already-open document.
REPO_ROOT = None

# Filename of the chassis skeleton inside the repo root.
CHASSIS_SKELETON_FILENAME = "RC_Chassis_Skeleton.FCStd"

# Corner-module stage document names, in creation order.
# These are the DOC_NAME values each stage macro uses.
STAGE_DOC_NAMES = [
    "Corner_WheelEnd_LH_R1",        # Stage 1 — datum reference frame
    "Corner_HighPivotArm_LHF_v01",  # Stage 2 — high-pivot arm body
    "Corner_Upright_LHF_v01",       # Stage 3 — upright / carrier body
    "Corner_ShockSpring_LHF_v01",   # Stage 4 — shock absorber & coil spring
]

# Output assembly document name.
ASSEMBLY_DOC_NAME = "RC_DS2_Assembly_Preview"
REPLACE_EXISTING  = True

# ---- Visual style per source (R, G, B), transparency 0-100 ------------------

_STYLES = {
    "chassis":        ((0.55, 0.60, 0.65),  25),  # grey, slightly transparent
    "stage1_ref":     ((0.20, 0.80, 0.20),  75),  # green, mostly transparent
    "stage2_arm":     ((0.75, 0.55, 0.15),   0),  # amber
    "stage3_upright": ((0.20, 0.50, 0.80),   0),  # steel blue
    "stage4_shock":   ((0.70, 0.85, 0.30),   0),  # spring green
    "unknown":        ((0.70, 0.70, 0.70),   0),  # fallback grey
}

# Map document-name prefix → style key
_DOC_STYLE_MAP = {
    "Corner_WheelEnd":      "stage1_ref",
    "Corner_HighPivotArm":  "stage2_arm",
    "Corner_Upright":       "stage3_upright",
    "Corner_ShockSpring":   "stage4_shock",
    "RC_Chassis_Skeleton":  "chassis",
}

# =============================================================================
# HELPERS
# =============================================================================


def resolve_repo_root():
    """Return the repository root directory, or None if it cannot be found."""
    if REPO_ROOT:
        return REPO_ROOT

    # Walk open documents: check the directory of each saved file for the
    # chassis skeleton, and go one level up if needed.
    for doc in App.listDocuments().values():
        if not doc.FileName:
            continue
        for candidate in (os.path.dirname(doc.FileName),
                          os.path.dirname(os.path.dirname(doc.FileName))):
            if os.path.isfile(os.path.join(candidate, CHASSIS_SKELETON_FILENAME)):
                return candidate
    return None


def _style_for_doc(doc_name):
    for prefix, key in _DOC_STYLE_MAP.items():
        if doc_name.startswith(prefix):
            return _STYLES[key]
    return _STYLES["unknown"]


def _apply_style(obj, colour, transparency):
    try:
        obj.ViewObject.ShapeColor   = colour
        obj.ViewObject.Transparency = transparency
    except Exception:
        pass


def _bb_str(bb):
    """Return a compact bounding-box string for a FreeCAD BoundBox."""
    return (
        f"X [{bb.XMin:+.1f} .. {bb.XMax:+.1f}]  "
        f"Y [{bb.YMin:+.1f} .. {bb.YMax:+.1f}]  "
        f"Z [{bb.ZMin:+.1f} .. {bb.ZMax:+.1f}]"
    )


def ensure_doc_open(doc_name):
    """Return the named document if it is already open, else None."""
    return App.listDocuments().get(doc_name)


def open_chassis_skeleton(repo_root):
    """Open RC_Chassis_Skeleton.FCStd and return its document, or None."""
    # Already open?
    for doc in App.listDocuments().values():
        if doc.FileName and CHASSIS_SKELETON_FILENAME in doc.FileName:
            App.Console.PrintMessage(f"  Chassis skeleton already open as '{doc.Name}'.\n")
            return doc

    if repo_root is None:
        App.Console.PrintWarning(
            "  Chassis skeleton: cannot find repo root.  "
            "Set REPO_ROOT at the top of this script.\n"
        )
        return None

    path = os.path.join(repo_root, CHASSIS_SKELETON_FILENAME)
    if not os.path.isfile(path):
        App.Console.PrintWarning(f"  Chassis skeleton not found at: {path}\n")
        return None

    App.Console.PrintMessage(f"  Opening chassis skeleton from disk: {path}\n")
    return App.openDocument(path)


def copy_shapes_into(source_doc, assembly_doc, group_name, colour, transparency):
    """Copy every Part::Feature shape from source_doc into a group in assembly_doc.

    Returns the number of objects copied.
    """
    grp = assembly_doc.addObject("App::DocumentObjectGroup", group_name)
    count = 0

    for obj in source_doc.Objects:
        if obj.TypeId != "Part::Feature":
            continue
        if not hasattr(obj, "Shape") or obj.Shape.isNull():
            continue

        copy_name = f"{group_name}__{obj.Name}"
        copy = assembly_doc.addObject("Part::Feature", copy_name)

        # Shapes built with absolute App.Vector coordinates carry their world
        # position in the shape vertex data.  The FreeCAD Placement is
        # identity for these objects, so a simple .copy() is sufficient.
        copy.Shape = obj.Shape.copy()

        # Preserve non-identity Placement if present (e.g. skeleton may have
        # positioned bodies via Placement rather than absolute coordinates).
        if obj.Placement != App.Placement():
            copy.Placement = obj.Placement

        _apply_style(copy, colour, transparency)
        grp.addObject(copy)
        count += 1

    return count


# =============================================================================
# MAIN
# =============================================================================


def main():
    # ---- Preparation --------------------------------------------------------

    repo_root = resolve_repo_root()
    if repo_root:
        App.Console.PrintMessage(f"Repository root: {repo_root}\n")
    else:
        App.Console.PrintWarning(
            "Repository root not found.  Chassis skeleton will be skipped\n"
            "unless it is already open.  Set REPO_ROOT to fix this.\n"
        )

    # ---- Create or replace the assembly document ----------------------------

    if REPLACE_EXISTING and ASSEMBLY_DOC_NAME in App.listDocuments():
        App.closeDocument(ASSEMBLY_DOC_NAME)

    asm_doc = App.newDocument(ASSEMBLY_DOC_NAME)
    App.Console.PrintMessage(f"\nAssembly document: '{ASSEMBLY_DOC_NAME}'\n")

    # ---- Collect source documents -------------------------------------------

    sources = []  # list of (document, group_label)

    # Chassis skeleton (opened from disk if needed)
    App.Console.PrintMessage("\n[1/4] Chassis skeleton\n")
    chassis_doc = open_chassis_skeleton(repo_root)
    if chassis_doc:
        sources.append((chassis_doc, "Chassis_Skeleton"))
    else:
        App.Console.PrintWarning("  Skipping chassis skeleton — not available.\n")

    # Corner-module stage documents
    for idx, stage_name in enumerate(STAGE_DOC_NAMES, start=2):
        App.Console.PrintMessage(f"\n[{idx}/{len(STAGE_DOC_NAMES) + 1}] {stage_name}\n")
        stage_doc = ensure_doc_open(stage_name)
        if stage_doc:
            App.Console.PrintMessage(f"  Found open document.\n")
            sources.append((stage_doc, stage_name.replace(" ", "_")))
        else:
            App.Console.PrintWarning(
                f"  Document '{stage_name}' is not open.  "
                f"Run its stage macro first, then re-run this script.\n"
            )

    # ---- Copy shapes --------------------------------------------------------

    App.Console.PrintMessage("\nCopying shapes into assembly...\n")

    total_objects = 0
    bb_report = []

    for source_doc, group_label in sources:
        colour, transp = _style_for_doc(source_doc.Name)
        n = copy_shapes_into(source_doc, asm_doc, group_label, colour, transp)
        total_objects += n
        App.Console.PrintMessage(f"  {group_label}: {n} object(s) copied.\n")

        # Aggregate bounding box for the group
        group_shapes = [
            obj.Shape for obj in asm_doc.Objects
            if obj.TypeId == "Part::Feature"
            and obj.Name.startswith(group_label)
            and not obj.Shape.isNull()
        ]
        if group_shapes:
            compound = Part.makeCompound(group_shapes)
            bb_report.append((group_label, compound.BoundBox))

    asm_doc.recompute()

    # ---- Fit view (GUI only) ------------------------------------------------

    try:
        import FreeCADGui as Gui
        Gui.SendMsgToActiveView("ViewFit")
    except Exception:
        pass

    # ---- Summary ------------------------------------------------------------

    App.Console.PrintMessage(f"\n{'=' * 60}\n")
    App.Console.PrintMessage(f"RC_DS2_Assembly_Preview — positioning report\n")
    App.Console.PrintMessage(f"{'=' * 60}\n")
    App.Console.PrintMessage(f"Total objects copied: {total_objects}\n\n")
    App.Console.PrintMessage("Bounding boxes (world coordinates, mm):\n\n")

    overall_bb = None
    for label, bb in bb_report:
        App.Console.PrintMessage(f"  {label}:\n    {_bb_str(bb)}\n\n")
        if overall_bb is None:
            overall_bb = bb
        else:
            overall_bb = overall_bb.united(bb)

    if overall_bb:
        App.Console.PrintMessage(
            f"  OVERALL:\n    {_bb_str(overall_bb)}\n\n"
        )

    App.Console.PrintMessage("Expected corner anchor (LHF): X=165  Y=-143  Z=75\n")
    App.Console.PrintMessage(
        "If parts appear misaligned, confirm that the chassis skeleton macro\n"
        "uses the same global coordinate origin as the stage macros\n"
        "(front axle at X=+165, left side Y=negative).\n"
    )
    App.Console.PrintMessage("\nAssembly preview complete.\n")

    return asm_doc


main()
