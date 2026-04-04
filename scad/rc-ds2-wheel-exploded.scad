//
// PETG beadlock rim + modular hub insert
// Revised to match the latest TPU hybrid water-assist tire.
//
// Design goals in this revision:
// - match the current 150 x 62 tire and 110 mm bead seat
// - preserve a true beadlock clamp, not a cosmetic ring
// - strengthen torque transfer for paddle-driven shock loads
// - keep the 12 mm hex isolated to a replaceable hub insert
// - add realistic washout / drainage openings in the wheel center
//
// Learning note:
// The torque path here is deliberately split:
// 1) axle -> 12 mm hex bore in hub insert
// 2) hub insert -> rounded drive-dog spigot
// 3) drive dog -> main rim body
// The retention screws mostly locate and retain the insert; they should not
// be the primary torque-carrying feature.
//
// Learning note:
// I replaced the old discrete clamp-stop idea with a continuous annular stop.
// That gives a more even clamp limit around the ring and reduces the chance
// that one area of the ring bottoms early while another keeps crushing TPU.
//

$fn = 140;

// -----------------------------------------------------------------------------
// SOURCE-OF-TRUTH TIRE DATA
// -----------------------------------------------------------------------------

// Tire OD including tread
tire_outer_diameter = 150;

// Tire total section width
tire_width = 62;

// Tire internal bead seat diameter
bead_seat_diameter = 110;

// Tire bead lip geometry from the current tire
bead_lip_height = 2.4;
bead_lip_width  = 5.0;
bead_relief_width = 2.0;

// -----------------------------------------------------------------------------
// ORIENTATION
// -----------------------------------------------------------------------------

// +1 = outer face
// -1 = inner face
outer_side =  1;
inner_side = -1;

// -----------------------------------------------------------------------------
// RIM BODY GEOMETRY
// -----------------------------------------------------------------------------

half_w = tire_width / 2;  // 31 mm

// Barrel fit: slight under-size relative to the nominal 110 seat
barrel_fit_clearance_d = 0.6;
rim_barrel_d = bead_seat_diameter - barrel_fit_clearance_d;   // 109.4

// Axial stack per side:
// center straight barrel -> shoulder support -> bead clamp land -> guard lip
seat_half_w          = 15.0;
shoulder_support_w   = 9.0;
clamp_land_w         = bead_lip_width;    // 5.0
guard_w              = 2.0;

// Diameters
shoulder_support_d   = 113.2;
clamp_land_d         = 117.6;
guard_peak_d         = 121.6;
guard_tip_d          = 119.6;

// Ring clamp-stop annulus.
// This is intentionally inside the bead area so the ring can bottom here
// before the TPU lip is over-crushed.
clamp_stop_id        = 86.0;
clamp_stop_od        = 106.0;
clamp_stop_h         = 1.9;

// -----------------------------------------------------------------------------
// BEADLOCK HARDWARE PLACEHOLDERS
// -----------------------------------------------------------------------------

beadlock_bolt_count              = 12;
beadlock_bolt_pcd                = 102.0;
beadlock_bolt_clearance_d        = 4.4;   // M4-ish
beadlock_body_hole_d             = 4.8;

beadlock_ring_od                 = 128.0;
beadlock_ring_id                 = 84.0;
beadlock_ring_th                 = 5.6;
beadlock_ring_boss_d             = 11.6;
beadlock_ring_boss_h             = 1.6;

beadlock_head_counterbore_d      = 8.4;
beadlock_head_counterbore_depth  = 2.6;

beadlock_nut_trap_af             = 7.4;
beadlock_nut_trap_depth          = 3.6;

// -----------------------------------------------------------------------------
// HUB INSERT + TORQUE DOG
// -----------------------------------------------------------------------------

// Chosen axle standard remains 12 mm hex
hub_hex_af                = 12.0;
hub_hex_clearance         = 0.25;

// Rounded drive-dog socket/spigot between insert and rim body.
// This is the primary torque path.
drive_dog_core_r          = 10.8;
drive_dog_lobe_r          = 4.1;
drive_dog_lobe_pcd        = 24.0;
drive_dog_lobes           = 8;
drive_dog_socket_clear    = 0.18;
drive_dog_depth           = 15.0;

// Hub insert flange
hub_insert_flange_d       = 56.0;
hub_insert_flange_th      = 7.0;

// Retention bolts for the insert
hub_mount_bolt_count              = 6;
hub_mount_bolt_pcd                = 42.0;
hub_mount_clearance_d             = 4.4;  // M4-ish
hub_mount_head_counterbore_d      = 8.0;
hub_mount_head_counterbore_depth  = 2.8;
hub_mount_nut_trap_af             = 7.4;
hub_mount_nut_trap_depth          = 3.6;

// -----------------------------------------------------------------------------
// WEIGHT / DRAINAGE
// -----------------------------------------------------------------------------

center_bowl_face_d        = 94.0;
center_bowl_floor_d       = 50.0;
center_bowl_depth         = 23.0;

center_window_count       = 6;
center_window_r1          = 17.5;
center_window_r2          = 33.5;
center_window_w           = 10.0;
center_window_h           = 18.0;

// Inner ring washout notches
washout_notch_count       = 6;
washout_notch_d           = 5.0;
washout_notch_center_r    = beadlock_ring_id / 2 + 1.3;

// -----------------------------------------------------------------------------
// HELPERS
// -----------------------------------------------------------------------------

// Parameters:
// af = hex across-flats dimension
module hex2d(af) {
    circle(r = af / sqrt(3), $fn = 6);
}

// Parameters:
// af = hex across-flats dimension
// h  = extrusion height
// center = whether to center on Z
module hex_prism(af, h, center = false) {
    linear_extrude(height = h, center = center)
        hex2d(af);
}

// Parameters:
// count = number of repeated instances
// pcd   = pitch circle diameter
module bolt_circle(count, pcd) {
    for (i = [0 : count - 1]) {
        rotate([0, 0, 360 * i / count])
            translate([pcd / 2, 0, 0])
                children();
    }
}

// Parameters:
// od = outer diameter
// id = inner diameter
// h  = height
// center = center the part on Z or not
module annulus(od, id, h, center = false) {
    difference() {
        cylinder(d = od, h = h, center = center);
        translate([0, 0, center ? 0 : -0.01])
            cylinder(d = id, h = h + 0.02, center = center);
    }
}

// Parameters:
// r1 = inner slot center radius
// r2 = outer slot center radius
// w  = slot width / diameter of end arcs
module radial_slot_2d(r1, r2, w) {
    hull() {
        translate([r1, 0, 0]) circle(d = w);
        translate([r2, 0, 0]) circle(d = w);
    }
}

// Parameters:
// core_r   = radius of the central blending circle
// lobe_r   = lobe radius
// lobe_pcd = pitch diameter of the lobe centers
// lobes    = number of lobes
module drive_dog_2d(core_r, lobe_r, lobe_pcd, lobes) {
    union() {
        circle(r = core_r);
        for (i = [0 : lobes - 1]) {
            rotate([0, 0, 360 * i / lobes])
                translate([lobe_pcd / 2, 0, 0])
                    circle(r = lobe_r);
        }
    }
}

// Parameters:
// od = outer diameter
// id = inner diameter
// h  = thickness
// outer_ch = outer edge chamfer
// inner_ch = inner edge chamfer
module chamfered_ring(od, id, h, outer_ch = 0.8, inner_ch = 0.6) {
    difference() {
        union() {
            cylinder(d = od - 2 * outer_ch, h = outer_ch);
            translate([0, 0, outer_ch])
                cylinder(d = od, h = h - 2 * outer_ch);
            translate([0, 0, h - outer_ch])
                cylinder(d1 = od, d2 = od - 2 * outer_ch, h = outer_ch);
        }

        union() {
            translate([0, 0, -0.01])
                cylinder(d = id + 2 * inner_ch, h = inner_ch + 0.02);
            translate([0, 0, inner_ch])
                cylinder(d = id, h = h - 2 * inner_ch);
            translate([0, 0, h - inner_ch])
                cylinder(d1 = id, d2 = id + 2 * inner_ch, h = inner_ch + 0.02);
        }
    }
}

// -----------------------------------------------------------------------------
// CORE BODY FEATURES
// -----------------------------------------------------------------------------

module side_shell_positive() {
    // Shoulder support from the straight barrel toward the bead clamp area
    translate([0, 0, seat_half_w])
        cylinder(d1 = rim_barrel_d, d2 = shoulder_support_d, h = shoulder_support_w);

    // Clamp land width matches the bead lip width
    translate([0, 0, seat_half_w + shoulder_support_w])
        cylinder(d = clamp_land_d, h = clamp_land_w);

    // Two-stage guard lip to avoid a sharp knife edge against TPU
    translate([0, 0, seat_half_w + shoulder_support_w + clamp_land_w])
        cylinder(d1 = clamp_land_d, d2 = guard_peak_d, h = guard_w / 2);

    translate([0, 0, seat_half_w + shoulder_support_w + clamp_land_w + guard_w / 2])
        cylinder(d1 = guard_peak_d, d2 = guard_tip_d, h = guard_w / 2);

    // Continuous clamp stop annulus
    translate([0, 0, seat_half_w + shoulder_support_w])
        annulus(clamp_stop_od, clamp_stop_id, clamp_stop_h, center = false);
}

module center_bowl_positive() {
    translate([0, 0, half_w - center_bowl_depth])
        cylinder(d1 = center_bowl_floor_d, d2 = center_bowl_face_d, h = center_bowl_depth + 0.02);
}

module drive_dog_socket_positive() {
    translate([0, 0, half_w - drive_dog_depth])
        linear_extrude(height = drive_dog_depth + 0.02)
            offset(r = drive_dog_socket_clear)
                drive_dog_2d(
                    drive_dog_core_r,
                    drive_dog_lobe_r,
                    drive_dog_lobe_pcd,
                    drive_dog_lobes
                );
}

// -----------------------------------------------------------------------------
// MAIN RIM BODY
// -----------------------------------------------------------------------------

module rim_body() {
    difference() {
        union() {
            // Straight center barrel
            cylinder(d = rim_barrel_d, h = 2 * seat_half_w, center = true);

            // Positive side features
            side_shell_positive();

            // Negative side features
            mirror([0, 0, 1]) side_shell_positive();
        }

        // Weight-relief / washout bowls
        center_bowl_positive();
        mirror([0, 0, 1]) center_bowl_positive();

        // Center windows: weight reduction + drainage
        linear_extrude(height = center_window_h, center = true)
            for (i = [0 : center_window_count - 1]) {
                rotate([0, 0, i * 360 / center_window_count])
                    radial_slot_2d(center_window_r1, center_window_r2, center_window_w);
            }

        // Hub insert drive-dog socket on the INNER face only
        mirror([0, 0, 1]) drive_dog_socket_positive();

        // Through-bore through the wheel center
        cylinder(d = 18.0, h = 2 * half_w + 2, center = true);

        // Insert retention holes through the center
        bolt_circle(hub_mount_bolt_count, hub_mount_bolt_pcd)
            cylinder(d = hub_mount_clearance_d, h = 2 * half_w + 2, center = true);

        // Counterbores for insert retention screw heads on the OUTER face
        translate([0, 0, half_w - hub_mount_head_counterbore_depth + 0.01])
            bolt_circle(hub_mount_bolt_count, hub_mount_bolt_pcd)
                cylinder(
                    d = hub_mount_head_counterbore_d,
                    h = hub_mount_head_counterbore_depth + 0.5
                );

        // Beadlock through-holes
        bolt_circle(beadlock_bolt_count, beadlock_bolt_pcd)
            cylinder(d = beadlock_body_hole_d, h = 2 * half_w + 4, center = true);
    }
}

// -----------------------------------------------------------------------------
// OUTER BEADLOCK RING
// -----------------------------------------------------------------------------

module outer_beadlock_ring() {
    difference() {
        union() {
            chamfered_ring(
                beadlock_ring_od,
                beadlock_ring_id,
                beadlock_ring_th,
                outer_ch = 0.9,
                inner_ch = 0.7
            );

            // Local bosses around each bolt hole on the exposed face
            translate([0, 0, beadlock_ring_th - 0.01])
                bolt_circle(beadlock_bolt_count, beadlock_bolt_pcd)
                    cylinder(d = beadlock_ring_boss_d, h = beadlock_ring_boss_h);
        }

        // Through-holes
        bolt_circle(beadlock_bolt_count, beadlock_bolt_pcd)
            translate([0, 0, -0.5])
                cylinder(d = beadlock_bolt_clearance_d, h = beadlock_ring_th + beadlock_ring_boss_h + 1.0);

        // Counterbores for screw heads
        bolt_circle(beadlock_bolt_count, beadlock_bolt_pcd)
            translate([0, 0, beadlock_ring_th + beadlock_ring_boss_h - beadlock_head_counterbore_depth + 0.01])
                cylinder(
                    d = beadlock_head_counterbore_d,
                    h = beadlock_head_counterbore_depth + 0.5
                );
    }
}

// -----------------------------------------------------------------------------
// INNER BEADLOCK RING
// -----------------------------------------------------------------------------

module inner_beadlock_ring() {
    difference() {
        union() {
            chamfered_ring(
                beadlock_ring_od,
                beadlock_ring_id,
                beadlock_ring_th,
                outer_ch = 0.9,
                inner_ch = 0.7
            );

            // Local bosses around each bolt hole on the exposed face
            translate([0, 0, beadlock_ring_th - 0.01])
                bolt_circle(beadlock_bolt_count, beadlock_bolt_pcd)
                    cylinder(d = beadlock_ring_boss_d, h = beadlock_ring_boss_h);
        }

        // Through-holes
        bolt_circle(beadlock_bolt_count, beadlock_bolt_pcd)
            translate([0, 0, -0.5])
                cylinder(d = beadlock_bolt_clearance_d, h = beadlock_ring_th + beadlock_ring_boss_h + 1.0);

        // Hex nut traps on the exposed face
        bolt_circle(beadlock_bolt_count, beadlock_bolt_pcd)
            translate([0, 0, beadlock_ring_th + beadlock_ring_boss_h - beadlock_nut_trap_depth + 0.01])
                hex_prism(
                    beadlock_nut_trap_af,
                    beadlock_nut_trap_depth + 0.6,
                    center = false
                );

        // Washout notches near the inner ID.
        // These are intentionally away from the tire clamp zone.
        for (i = [0 : washout_notch_count - 1]) {
            rotate([0, 0, i * 360 / washout_notch_count])
                translate([washout_notch_center_r, 0, -0.5])
                    cylinder(d = washout_notch_d, h = beadlock_ring_th + beadlock_ring_boss_h + 1.0);
        }
    }
}

// -----------------------------------------------------------------------------
// MODULAR HUB INSERT
// -----------------------------------------------------------------------------

module hub_insert() {
    difference() {
        union() {
            // Flange on the inner face
            cylinder(d = hub_insert_flange_d, h = hub_insert_flange_th);

            // Rounded drive-dog spigot into the rim body
            translate([0, 0, hub_insert_flange_th])
                linear_extrude(height = drive_dog_depth)
                    drive_dog_2d(
                        drive_dog_core_r,
                        drive_dog_lobe_r,
                        drive_dog_lobe_pcd,
                        drive_dog_lobes
                    );
        }

        // 12 mm hex axle bore through the whole insert
        translate([0, 0, -0.5])
            hex_prism(
                hub_hex_af + hub_hex_clearance,
                hub_insert_flange_th + drive_dog_depth + 1.0,
                center = false
            );

        // Retention screw holes
        bolt_circle(hub_mount_bolt_count, hub_mount_bolt_pcd)
            translate([0, 0, -0.5])
                cylinder(d = hub_mount_clearance_d, h = hub_insert_flange_th + 1.0);

        // Nut traps on the visible flange face
        bolt_circle(hub_mount_bolt_count, hub_mount_bolt_pcd)
            translate([0, 0, 0.01])
                hex_prism(
                    hub_mount_nut_trap_af,
                    hub_mount_nut_trap_depth + 0.5,
                    center = false
                );
    }
}

// -----------------------------------------------------------------------------
// COAXIAL EXPLODED PREVIEW
// -----------------------------------------------------------------------------

show_layout = true;
explode_gap = 6;

// Parameters:
// none
// Keeps every part on the same wheel axis (X/Y centered), and explodes them
// along Z so the preview reads like an assembly stack instead of side-by-side.
module show_layout_exploded() {
    rim_face_z      = half_w;  // outermost face of the rim body from center
    ring_total_th   = beadlock_ring_th + beadlock_ring_boss_h;
    insert_total_th = hub_insert_flange_th + drive_dog_depth;

    // Main rim body stays centered at the origin
    rim_body();

    // OUTER beadlock ring:
    // same orientation, moved off the +Z face
    translate([0, 0, rim_face_z + explode_gap])
        outer_beadlock_ring();

    // INNER beadlock ring:
    // flipped so its clamp face still points toward the rim, then moved off -Z
    translate([0, 0, -rim_face_z - explode_gap])
        rotate([180, 0, 0])
            inner_beadlock_ring();

    // Hub insert:
    // stays aimed toward +Z so its drive dog still points into the inner-face socket
    // positioned farther down the same axis behind the inner ring
    translate([0, 0, -rim_face_z - explode_gap - ring_total_th - explode_gap - insert_total_th])
        hub_insert();
}

if (show_layout)
    show_layout_exploded();