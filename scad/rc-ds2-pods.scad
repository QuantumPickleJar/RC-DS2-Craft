//
// Amphibious RC sealed module set - OpenSCAD
// X = front/rear, Y = left/right, Z = up
//
// This rewrite is intentionally system-minded:
// - main electronics pod = sealed buoyant module
// - battery pod = separate sealed buoyant module
// - side chambers + trim chambers = additional sealed buoyant modules
// - displacement is checked at the system level, not just at the center pod
//
// Higher-learning note:
// In OpenSCAD, once a design stops being a single part and starts becoming a
// family of related modules, named parameters and repeated helper modules pay
// off hard. You do not get C#/Java-style constructors or type safety here, so
// "clean parameter blocks + reusable geometry helpers" is the closest thing to
// defensive engineering.
//
// Higher-learning note:
// Repeated-service wet parts are much happier with insert bores and clamped
// gaskets than with printed threads or glue. PETG creeps over time; clamped
// seals are far more forgiving when you reopen things.
//
// Suggested materials:
// - PETG: shells, lids, gland frames, backers
// - TPU: face gaskets, sealing washers, compression inserts
//

$fn = 64;

// -----------------------------------------------------------------------------
// Part selector
// -----------------------------------------------------------------------------
part = "system_assembly";
// "system_assembly"
// "main_pod_base", "main_pod_lid", "main_pod_gasket"
// "battery_base", "battery_lid", "battery_gasket"
// "side_base", "side_lid", "side_gasket"
// "trim_base", "trim_lid", "trim_gasket"
// "pod_gland_frame", "pod_gland_insert", "pod_gland_backer"
// "battery_gland_frame", "battery_gland_insert", "battery_gland_backer"
// "washer"

// -----------------------------------------------------------------------------
// System-level targets
// -----------------------------------------------------------------------------
aggressive_load_target_kg = 4.5;    // System wet mass target to support aggressively
target_displacement_min_L = 5.6;    // Lower end of desired sealed displacement
target_displacement_max_L = 6.0;    // Upper end of desired sealed displacement

// -----------------------------------------------------------------------------
// Shared seal / fastening parameters
// -----------------------------------------------------------------------------
wall_t          = 3.2;
floor_t         = 3.2;
lid_top_t       = 3.0;
collar_inset    = 2.5;
fit_clear       = 0.35;
lid_cavity_clear = 3.4;

gasket_w        = 2.3;
gasket_h        = 2.6;
gasket_groove_d = 2.0;

lid_screw_d       = 3.4;   // M3 clearance
insert_bore_d     = 4.6;   // Typical M3 insert pilot
insert_bore_depth = 6.0;
lid_boss_d        = 11.0;

washer_od = 7.5;
washer_h  = 1.2;

// -----------------------------------------------------------------------------
// Main electronics pod
// Keep this close to the original center envelope, but now treat it as a sealed
// buoyant module with high-placed immersion-capable glands.
// -----------------------------------------------------------------------------
main_pod_len      = 142;   // Kept slightly under old 150 target because gland bosses add length
main_pod_wid      = 94;
main_pod_base_h   = 35;
main_pod_lid_h    = 19;
main_pod_total_h  = main_pod_base_h + main_pod_lid_h;
main_pod_corner_r = 10;
main_pod_collar_h = 7.0;
main_pod_skirt_d  = main_pod_collar_h + 0.7;

// Existing chassis mount pattern carried forward
mount_spacing_x = 116;
mount_spacing_y = 72;
mount_hole_d    = 3.2;
mount_ped_d     = 12.0;
mount_ped_h     = 4.0;
mount_head_d    = 9.0;

// Main pod lid screws
main_pod_screws = [
    [-54, -30], [-54,  30], [ 54, -30], [ 54,  30],
    [  0, -33], [  0,  33], [-28,   0], [ 28,   0]
];

// Internal pads
esc_pad_len   = 34;
esc_pad_wid   = 28;
esc_pad_h     = 2.2;

center_pad_len = 30;
center_pad_wid = 30;
center_pad_h   = 4.0;

arming_pad_len = 18;
arming_pad_wid = 24;
arming_pad_h   = 3.0;

front_esc_x =  32;
rear_esc_x  = -32;
center_x    =   0;
arming_y    =  20;

// Main pod gland bosses and channels
pod_gland_frame_w    = 38;
pod_gland_frame_h    = 22;
pod_gland_frame_t    = 2.5;
pod_gland_backer_t   = 2.5;
pod_gland_insert_t   = 4.0;
pod_gland_corner_r   = 3.0;

pod_gland_window_w   = 28;
pod_gland_window_h   = 12;
pod_gland_boss_t     = 4.0;
pod_gland_z          = 27;    // high on the wall, not near the floor

pod_gland_bolt_d       = 3.4;
pod_gland_bolt_span_y  = 26;
pod_gland_bolt_span_z  = 12;

// Typical harness bundle channels for front/rear axle module wiring
pod_gland_channels = [3.2, 3.2, 3.2, 3.2, 4.2, 5.2];
pod_gland_channel_span = 24;
pod_gland_slit_w       = 0.8;

// -----------------------------------------------------------------------------
// Separate sealed battery module
// This is geometry-only waterproof packaging. Validate chemistry, pack swelling,
// connector choice, and failure philosophy before trusting a sealed battery box.
// -----------------------------------------------------------------------------
battery_len      = 128;
battery_wid      = 84;
battery_base_h   = 30;
battery_lid_h    = 16;
battery_total_h  = battery_base_h + battery_lid_h;
battery_corner_r = 8;
battery_collar_h = 6.5;
battery_skirt_d  = battery_collar_h + 0.7;

battery_screws = [
    [-44, -24], [-44, 24], [ 44, -24], [ 44, 24],
    [  0, -28], [  0, 28]
];

battery_pad_len = 96;
battery_pad_wid = 58;
battery_pad_h   = 2.5;

// Smaller 2-wire gland for the battery module
battery_gland_frame_w    = 30;
battery_gland_frame_h    = 20;
battery_gland_frame_t    = 2.5;
battery_gland_backer_t   = 2.5;
battery_gland_insert_t   = 4.0;
battery_gland_corner_r   = 3.0;

battery_gland_window_w   = 20;
battery_gland_window_h   = 10;
battery_gland_boss_t     = 4.0;
battery_gland_z          = 22;

battery_gland_bolt_d      = 3.4;
battery_gland_bolt_span_y = 20;
battery_gland_bolt_span_z = 10;

battery_gland_channels = [5.5, 5.5];
battery_gland_channel_span = 10;

// -----------------------------------------------------------------------------
// Side buoyancy chambers
// These are deliberately large; they do the heavy lifting for displacement.
// -----------------------------------------------------------------------------
side_len      = 300;
side_wid      = 60;
side_base_h   = 64;
side_lid_h    = 36;
side_total_h  = side_base_h + side_lid_h;
side_corner_r = 12;
side_collar_h = 8.0;
side_skirt_d  = side_collar_h + 0.7;

side_screws = [
    [-112, -18], [-112, 18], [0, -22], [0, 22], [112, -18], [112, 18]
];

// -----------------------------------------------------------------------------
// Front / rear trim chambers
// These help the flotation balance and give you more freedom over trim.
// -----------------------------------------------------------------------------
trim_len      = 155;
trim_wid      = 50;
trim_base_h   = 46;
trim_lid_h    = 30;
trim_total_h  = trim_base_h + trim_lid_h;
trim_corner_r = 10;
trim_collar_h = 7.0;
trim_skirt_d  = trim_collar_h + 0.7;

trim_screws = [
    [-50, -15], [-50, 15], [0, -18], [0, 18], [50, -15], [50, 15]
];

// -----------------------------------------------------------------------------
// Visual assembly offsets
// -----------------------------------------------------------------------------
explode = 7;
system_side_y_offset = 110;
system_battery_z_offset = -58;
system_trim_x_offset = 205;

// -----------------------------------------------------------------------------
// Displacement math
// -----------------------------------------------------------------------------
function rounded_rect_area(l, w, r) = l * w - (4 - PI) * r * r;
function liters_from_mm3(v) = v / 1000000;
function round_to(x, d=3) = floor(x * pow(10, d) + 0.5) / pow(10, d);

function module_outer_volume_l(l, w, h, r) =
    liters_from_mm3(rounded_rect_area(l, w, r) * h);

function boss_outer_volume_l(w, h, r, t, count=1) =
    count * liters_from_mm3(rounded_rect_area(w, h, r) * t);

main_pod_displacement_L =
    module_outer_volume_l(main_pod_len, main_pod_wid, main_pod_total_h, main_pod_corner_r) +
    boss_outer_volume_l(pod_gland_frame_w, pod_gland_frame_h, pod_gland_corner_r, pod_gland_boss_t, 2);

battery_displacement_L =
    module_outer_volume_l(battery_len, battery_wid, battery_total_h, battery_corner_r) +
    boss_outer_volume_l(battery_gland_frame_w, battery_gland_frame_h, battery_gland_corner_r, battery_gland_boss_t, 1);

side_total_displacement_L =
    2 * module_outer_volume_l(side_len, side_wid, side_total_h, side_corner_r);

trim_total_displacement_L =
    2 * module_outer_volume_l(trim_len, trim_wid, trim_total_h, trim_corner_r);

system_displacement_L =
    main_pod_displacement_L +
    battery_displacement_L +
    side_total_displacement_L +
    trim_total_displacement_L;

freshwater_margin_kg = system_displacement_L - aggressive_load_target_kg;

// Echo the system sanity check.
// Real achieved margin will be lower once you include trapped external water,
// hardware, dynamic trim, and any chamber flooding during failure.
echo("Main pod displacement L =", round_to(main_pod_displacement_L, 3));
echo("Battery module displacement L =", round_to(battery_displacement_L, 3));
echo("Side chamber pair displacement L =", round_to(side_total_displacement_L, 3));
echo("Trim chamber pair displacement L =", round_to(trim_total_displacement_L, 3));
echo("System displacement L =", round_to(system_displacement_L, 3));
echo("Freshwater buoyancy margin kg approx =", round_to(freshwater_margin_kg, 3));
echo("Target displacement band L =", [target_displacement_min_L, target_displacement_max_L]);

// -----------------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------------

// Parameters:
// l = overall length in X
// w = overall width in Y
// r = corner radius
module rounded_rect2d(l, w, r) {
    rr = max(0.01, min(r, min(l, w) / 2 - 0.01));
    hull() {
        for (x = [-l/2 + rr, l/2 - rr])
            for (y = [-w/2 + rr, w/2 - rr])
                translate([x, y]) circle(r = rr);
    }
}

// Parameters:
// l = length in X
// w = width in Y
// h = height in Z
// r = corner radius
module rounded_prism_z(l, w, h, r) {
    linear_extrude(height = h)
        rounded_rect2d(l, w, r);
}

// Parameters:
// t = thickness in X
// span_y = width in Y
// span_z = height in Z
// r = corner radius in YZ
module rounded_prism_x_centered(t, span_y, span_z, r) {
    translate([-t/2, 0, 0])
        rotate([0, 90, 0])
            rounded_prism_z(span_y, span_z, t, r);
}

// Parameters:
// od = outer diameter
// id = inner clearance hole
// h  = washer thickness
module sealing_washer(od=washer_od, id=lid_screw_d, h=washer_h) {
    difference() {
        cylinder(d = od, h = h);
        translate([0, 0, -0.01]) cylinder(d = id, h = h + 0.02);
    }
}

// Parameters:
// len / wid / base_h / corner_r = outer shell dimensions
// wall_t / floor_t = wall and floor thickness
// collar_inset / collar_h = stepped upper collar geometry
module sealed_base_outer(len, wid, base_h, corner_r, collar_inset, collar_h) {
    collar_len = len - 2 * collar_inset;
    collar_wid = wid - 2 * collar_inset;
    collar_r   = corner_r - collar_inset;

    union() {
        rounded_prism_z(len, wid, base_h - collar_h, corner_r);
        translate([0, 0, base_h - collar_h])
            rounded_prism_z(collar_len, collar_wid, collar_h, collar_r);
    }
}

// Parameters:
// len / wid / base_h / corner_r = outer dimensions
// wall_t / floor_t = shell thicknesses
// collar_inset = upper collar shrink
module sealed_base_shell(len, wid, base_h, corner_r, wall_t, floor_t, collar_inset, collar_h) {
    collar_len = len - 2 * collar_inset;
    collar_wid = wid - 2 * collar_inset;
    collar_r   = corner_r - collar_inset;

    opening_len = collar_len - 2 * wall_t;
    opening_wid = collar_wid - 2 * wall_t;
    opening_r   = max(1, collar_r - wall_t);

    difference() {
        sealed_base_outer(len, wid, base_h, corner_r, collar_inset, collar_h);

        translate([0, 0, floor_t])
            rounded_prism_z(opening_len, opening_wid, base_h - floor_t + 0.05, opening_r);
    }
}

// Parameters:
// len / wid / lid_h / corner_r = outer lid dimensions
// wall_t / collar_inset / collar_h = fit geometry
// fit_clear / skirt_d / lid_cavity_clear / lid_top_t = inner lid clearances
// gasket_w / gasket_groove_d = face gasket groove sizing
module sealed_lid_shell(len, wid, lid_h, corner_r,
                        wall_t, collar_inset, collar_h,
                        fit_clear, skirt_d, lid_cavity_clear, lid_top_t,
                        gasket_w, gasket_groove_d) {
    collar_len = len - 2 * collar_inset;
    collar_wid = wid - 2 * collar_inset;
    collar_r   = corner_r - collar_inset;

    opening_len = collar_len - 2 * wall_t;
    opening_wid = collar_wid - 2 * wall_t;
    opening_r   = max(1, collar_r - wall_t);

    gasket_margin = (wall_t - gasket_w) / 2;
    gasket_inner_len = opening_len + 2 * gasket_margin;
    gasket_inner_wid = opening_wid + 2 * gasket_margin;
    gasket_inner_r   = max(1, opening_r + gasket_margin);

    gasket_outer_len = gasket_inner_len + 2 * gasket_w;
    gasket_outer_wid = gasket_inner_wid + 2 * gasket_w;
    gasket_outer_r   = gasket_inner_r + gasket_w;

    difference() {
        rounded_prism_z(len, wid, lid_h, corner_r);

        // Lower skirt pocket
        translate([0, 0, -0.01])
            rounded_prism_z(collar_len + 2 * fit_clear,
                            collar_wid + 2 * fit_clear,
                            skirt_d + 0.02,
                            collar_r + fit_clear);

        // Upper cavity
        translate([0, 0, skirt_d])
            rounded_prism_z(opening_len + 2 * lid_cavity_clear,
                            opening_wid + 2 * lid_cavity_clear,
                            lid_h - lid_top_t - skirt_d + 0.02,
                            opening_r + lid_cavity_clear);

        // Face gasket groove in the pocket ceiling
        translate([0, 0, skirt_d - gasket_groove_d - 0.01])
            linear_extrude(height = gasket_groove_d + 0.02)
                difference() {
                    rounded_rect2d(gasket_outer_len, gasket_outer_wid, gasket_outer_r);
                    rounded_rect2d(gasket_inner_len, gasket_inner_wid, gasket_inner_r);
                }
    }
}

// Parameters:
// len / wid / corner_r / wall_t / collar_inset = module sealing land geometry
// gasket_w / gasket_h = TPU gasket section sizing
module face_gasket(len, wid, corner_r, wall_t, collar_inset, gasket_w, gasket_h) {
    collar_len = len - 2 * collar_inset;
    collar_wid = wid - 2 * collar_inset;
    collar_r   = corner_r - collar_inset;

    opening_len = collar_len - 2 * wall_t;
    opening_wid = collar_wid - 2 * wall_t;
    opening_r   = max(1, collar_r - wall_t);

    gasket_margin = (wall_t - gasket_w) / 2;
    gasket_inner_len = opening_len + 2 * gasket_margin;
    gasket_inner_wid = opening_wid + 2 * gasket_margin;
    gasket_inner_r   = max(1, opening_r + gasket_margin);

    gasket_outer_len = gasket_inner_len + 2 * gasket_w;
    gasket_outer_wid = gasket_inner_wid + 2 * gasket_w;
    gasket_outer_r   = gasket_inner_r + gasket_w;

    linear_extrude(height = gasket_h)
        difference() {
            rounded_rect2d(gasket_outer_len - 0.12, gasket_outer_wid - 0.12, gasket_outer_r - 0.05);
            rounded_rect2d(gasket_inner_len + 0.12, gasket_inner_wid + 0.12, gasket_inner_r + 0.05);
        }
}

// Parameters:
// positions = array of [x, y] hole centers
// d = hole diameter
// h = cut height
// z0 = starting Z
module screw_pattern_holes(positions, d, h, z0=0) {
    for (p = positions)
        translate([p[0], p[1], z0])
            cylinder(d = d, h = h);
}

// Parameters:
// positions = array of [x, y] boss centers
// d = boss diameter
// h = boss height
// z0 = base Z
module screw_pattern_bosses(positions, d, h, z0=0) {
    for (p = positions)
        translate([p[0], p[1], z0])
            cylinder(d = d, h = h);
}

// Parameters:
// positions = array of [x, y] locations
// d = recess diameter
// h = recess height
// z0 = recess Z
module screw_pattern_recesses(positions, d, h, z0=0) {
    for (p = positions)
        translate([p[0], p[1], z0])
            cylinder(d = d, h = h);
}

// Parameters:
// frame_w / frame_h / frame_t / corner_r = outer clamp frame
// window_w / window_h = center opening
// bolt_d / bolt_span_y / bolt_span_z = bolt pattern
module split_gland_frame(frame_w, frame_h, frame_t, corner_r,
                         window_w, window_h,
                         bolt_d, bolt_span_y, bolt_span_z) {
    difference() {
        rounded_prism_x_centered(frame_t, frame_w, frame_h, corner_r);

        rounded_prism_x_centered(frame_t + 0.2, window_w, window_h, 2);

        for (yy = [-bolt_span_y / 2, bolt_span_y / 2],
             zz = [-bolt_span_z / 2, bolt_span_z / 2])
            translate([0, yy, zz])
                rotate([0, 90, 0]) cylinder(d = bolt_d, h = frame_t + 0.3, center = true);
    }
}

// Parameters:
// frame_w / frame_h / backer_t / corner_r = backer dimensions
// window_w / window_h = backer opening
// bolt_d / bolt_span_y / bolt_span_z = bolt pattern
module split_gland_backer(frame_w, frame_h, backer_t, corner_r,
                          window_w, window_h,
                          bolt_d, bolt_span_y, bolt_span_z) {
    difference() {
        rounded_prism_x_centered(backer_t, frame_w, frame_h, corner_r);

        rounded_prism_x_centered(backer_t + 0.2, window_w + 2, window_h + 2, 2);

        for (yy = [-bolt_span_y / 2, bolt_span_y / 2],
             zz = [-bolt_span_z / 2, bolt_span_z / 2])
            translate([0, yy, zz])
                rotate([0, 90, 0]) cylinder(d = bolt_d, h = backer_t + 0.3, center = true);
    }
}

// Parameters:
// frame_w / frame_h / insert_t / corner_r = outer insert size
// channels = array of wire channel diameters
// channel_span = overall spacing span along Y
// slit_w = slit width for reworkable insert
// bolt_d / bolt_span_y / bolt_span_z = bolt pattern
module split_gland_insert(frame_w, frame_h, insert_t, corner_r,
                          channels, channel_span, slit_w,
                          bolt_d, bolt_span_y, bolt_span_z) {
    difference() {
        rounded_prism_x_centered(insert_t, frame_w - 1.2, frame_h - 1.2, corner_r - 0.6);

        for (i = [0 : len(channels) - 1]) {
            yy = (len(channels) < 2) ? 0 : (-channel_span / 2 + i * (channel_span / (len(channels) - 1)));

            translate([0, yy, 0])
                rotate([0, 90, 0]) cylinder(d = channels[i], h = insert_t + 0.3, center = true);

            translate([0, yy, frame_h / 4])
                cube([insert_t + 0.3, slit_w, frame_h / 2 + 0.6], center = true);
        }

        for (yy = [-bolt_span_y / 2, bolt_span_y / 2],
             zz = [-bolt_span_z / 2, bolt_span_z / 2])
            translate([0, yy, zz])
                rotate([0, 90, 0]) cylinder(d = bolt_d, h = insert_t + 0.3, center = true);
    }
}

// -----------------------------------------------------------------------------
// Main electronics pod
// -----------------------------------------------------------------------------

// Parameters:
// none; uses the main pod globals for pad layout
module main_pod_internal_features() {
    screw_pattern_bosses(main_pod_screws, lid_boss_d, main_pod_base_h - floor_t - 0.6, floor_t);

    // Mount pedestals for the existing chassis pattern
    for (sx = [-1, 1], sy = [-1, 1])
        translate([sx * mount_spacing_x / 2, sy * mount_spacing_y / 2, floor_t])
            cylinder(d = mount_ped_d, h = mount_ped_h);

    // Front ESC pad
    translate([front_esc_x, 0, floor_t])
        rounded_prism_z(esc_pad_len, esc_pad_wid, esc_pad_h, 2);

    // Rear ESC pad
    translate([rear_esc_x, 0, floor_t])
        rounded_prism_z(esc_pad_len, esc_pad_wid, esc_pad_h, 2);

    // Receiver / MCU pad
    translate([center_x, 0, floor_t])
        rounded_prism_z(center_pad_len, center_pad_wid, center_pad_h, 2);

    // Fuse / arming reserve
    translate([0, arming_y, floor_t])
        rounded_prism_z(arming_pad_len, arming_pad_wid, arming_pad_h, 2);

    // Raised external gland bosses
    for (s = [-1, 1])
        translate([s * (main_pod_len / 2 + pod_gland_boss_t / 2 - 0.05), 0, pod_gland_z])
            rounded_prism_x_centered(pod_gland_boss_t, pod_gland_frame_w, pod_gland_frame_h, pod_gland_corner_r);
}

// Parameters:
// none; uses main pod globals
module main_pod_base() {
    difference() {
        union() {
            sealed_base_shell(main_pod_len, main_pod_wid, main_pod_base_h, main_pod_corner_r,
                              wall_t, floor_t, collar_inset, main_pod_collar_h);
            main_pod_internal_features();
        }

        // Lid screw holes and insert bores
        screw_pattern_holes(main_pod_screws, lid_screw_d, main_pod_base_h + 0.1, -0.01);
        screw_pattern_holes(main_pod_screws, insert_bore_d, insert_bore_depth + 0.1, main_pod_base_h - insert_bore_depth);

        // Mount holes and sealing washer seats
        for (sx = [-1, 1], sy = [-1, 1]) {
            translate([sx * mount_spacing_x / 2, sy * mount_spacing_y / 2, -0.01])
                cylinder(d = mount_hole_d, h = main_pod_base_h + 0.02);

            translate([sx * mount_spacing_x / 2, sy * mount_spacing_y / 2, floor_t + mount_ped_h - washer_h])
                cylinder(d = mount_head_d, h = washer_h + 0.05);
        }

        // Front and rear gland windows + bolt holes
        for (s = [-1, 1]) {
            translate([s * (main_pod_len / 2 + pod_gland_boss_t / 2 - 0.05), 0, pod_gland_z])
                rounded_prism_x_centered(pod_gland_boss_t + wall_t + 0.8, pod_gland_window_w, pod_gland_window_h, 2);

            for (yy = [-pod_gland_bolt_span_y / 2, pod_gland_bolt_span_y / 2],
                 zz = [-pod_gland_bolt_span_z / 2, pod_gland_bolt_span_z / 2])
                translate([s * (main_pod_len / 2 + pod_gland_boss_t / 2 - 0.05), yy, pod_gland_z + zz])
                    rotate([0, 90, 0]) cylinder(d = pod_gland_bolt_d, h = pod_gland_boss_t + wall_t + 1.0, center = true);
        }

        // ESC zip-tie slots
        for (yy = [-7, 7]) {
            translate([front_esc_x, yy, floor_t + 0.2])
                rounded_prism_z(12, 3.0, esc_pad_h + 0.2, 1.2);

            translate([rear_esc_x, yy, floor_t + 0.2])
                rounded_prism_z(12, 3.0, esc_pad_h + 0.2, 1.2);
        }

        // Center pad strap slots
        for (xx = [-6, 6], yy = [-8, 8])
            translate([xx, yy, floor_t + 0.2])
                rounded_prism_z(9, 3.0, center_pad_h + 0.2, 1.2);

        // Arming pad slots
        for (xx = [-4, 4])
            translate([xx, arming_y, floor_t + 0.2])
                rounded_prism_z(10, 3.2, arming_pad_h + 0.2, 1.2);
    }
}

// Parameters:
// none; uses main pod globals
module main_pod_lid() {
    difference() {
        sealed_lid_shell(main_pod_len, main_pod_wid, main_pod_lid_h, main_pod_corner_r,
                         wall_t, collar_inset, main_pod_collar_h,
                         fit_clear, main_pod_skirt_d, lid_cavity_clear, lid_top_t,
                         gasket_w, gasket_groove_d);

        screw_pattern_holes(main_pod_screws, lid_screw_d, main_pod_lid_h + 0.02, -0.01);
        screw_pattern_recesses(main_pod_screws, washer_od, washer_h + 0.02, main_pod_lid_h - washer_h);
    }
}

// Parameters:
// none; uses main pod globals
module main_pod_gasket() {
    face_gasket(main_pod_len, main_pod_wid, main_pod_corner_r, wall_t, collar_inset, gasket_w, gasket_h);
}

// -----------------------------------------------------------------------------
// Battery module
// -----------------------------------------------------------------------------

// Parameters:
// none; uses battery globals
module battery_internal_features() {
    screw_pattern_bosses(battery_screws, lid_boss_d, battery_base_h - floor_t - 0.6, floor_t);

    translate([0, 0, floor_t])
        rounded_prism_z(battery_pad_len, battery_pad_wid, battery_pad_h, 3);

    // Rear gland boss
    translate([-battery_len / 2 - battery_gland_boss_t / 2 + 0.05, 0, battery_gland_z])
        rounded_prism_x_centered(battery_gland_boss_t, battery_gland_frame_w, battery_gland_frame_h, battery_gland_corner_r);
}

// Parameters:
// none; uses battery globals
module battery_base() {
    difference() {
        union() {
            sealed_base_shell(battery_len, battery_wid, battery_base_h, battery_corner_r,
                              wall_t, floor_t, collar_inset, battery_collar_h);
            battery_internal_features();
        }

        screw_pattern_holes(battery_screws, lid_screw_d, battery_base_h + 0.1, -0.01);
        screw_pattern_holes(battery_screws, insert_bore_d, insert_bore_depth + 0.1, battery_base_h - insert_bore_depth);

        // Rear gland window + bolt holes
        translate([-battery_len / 2 - battery_gland_boss_t / 2 + 0.05, 0, battery_gland_z])
            rounded_prism_x_centered(battery_gland_boss_t + wall_t + 0.8, battery_gland_window_w, battery_gland_window_h, 2);

        for (yy = [-battery_gland_bolt_span_y / 2, battery_gland_bolt_span_y / 2],
             zz = [-battery_gland_bolt_span_z / 2, battery_gland_bolt_span_z / 2])
            translate([-battery_len / 2 - battery_gland_boss_t / 2 + 0.05, yy, battery_gland_z + zz])
                rotate([0, 90, 0]) cylinder(d = battery_gland_bolt_d, h = battery_gland_boss_t + wall_t + 1.0, center = true);

        // Strap slots for the pack
        for (xx = [-22, 22], yy = [-14, 14])
            translate([xx, yy, floor_t + 0.2])
                rounded_prism_z(11, 3.2, battery_pad_h + 0.2, 1.2);
    }
}

// Parameters:
// none; uses battery globals
module battery_lid() {
    difference() {
        sealed_lid_shell(battery_len, battery_wid, battery_lid_h, battery_corner_r,
                         wall_t, collar_inset, battery_collar_h,
                         fit_clear, battery_skirt_d, lid_cavity_clear, lid_top_t,
                         gasket_w, gasket_groove_d);

        screw_pattern_holes(battery_screws, lid_screw_d, battery_lid_h + 0.02, -0.01);
        screw_pattern_recesses(battery_screws, washer_od, washer_h + 0.02, battery_lid_h - washer_h);
    }
}

// Parameters:
// none; uses battery globals
module battery_gasket() {
    face_gasket(battery_len, battery_wid, battery_corner_r, wall_t, collar_inset, gasket_w, gasket_h);
}

// -----------------------------------------------------------------------------
// Buoyancy side chamber
// These are simple sealed flotation modules; no penetrations by default.
// -----------------------------------------------------------------------------

// Parameters:
// none; uses side globals
module side_base() {
    difference() {
        union() {
            sealed_base_shell(side_len, side_wid, side_base_h, side_corner_r,
                              wall_t, floor_t, collar_inset, side_collar_h);

            screw_pattern_bosses(side_screws, lid_boss_d, side_base_h - floor_t - 0.6, floor_t);
        }

        screw_pattern_holes(side_screws, lid_screw_d, side_base_h + 0.1, -0.01);
        screw_pattern_holes(side_screws, insert_bore_d, insert_bore_depth + 0.1, side_base_h - insert_bore_depth);
    }
}

// Parameters:
// none; uses side globals
module side_lid() {
    difference() {
        sealed_lid_shell(side_len, side_wid, side_lid_h, side_corner_r,
                         wall_t, collar_inset, side_collar_h,
                         fit_clear, side_skirt_d, lid_cavity_clear, lid_top_t,
                         gasket_w, gasket_groove_d);

        screw_pattern_holes(side_screws, lid_screw_d, side_lid_h + 0.02, -0.01);
        screw_pattern_recesses(side_screws, washer_od, washer_h + 0.02, side_lid_h - washer_h);
    }
}

// Parameters:
// none; uses side globals
module side_gasket() {
    face_gasket(side_len, side_wid, side_corner_r, wall_t, collar_inset, gasket_w, gasket_h);
}

// -----------------------------------------------------------------------------
// Trim chamber
// -----------------------------------------------------------------------------

// Parameters:
// none; uses trim globals
module trim_base() {
    difference() {
        union() {
            sealed_base_shell(trim_len, trim_wid, trim_base_h, trim_corner_r,
                              wall_t, floor_t, collar_inset, trim_collar_h);

            screw_pattern_bosses(trim_screws, lid_boss_d, trim_base_h - floor_t - 0.6, floor_t);
        }

        screw_pattern_holes(trim_screws, lid_screw_d, trim_base_h + 0.1, -0.01);
        screw_pattern_holes(trim_screws, insert_bore_d, insert_bore_depth + 0.1, trim_base_h - insert_bore_depth);
    }
}

// Parameters:
// none; uses trim globals
module trim_lid() {
    difference() {
        sealed_lid_shell(trim_len, trim_wid, trim_lid_h, trim_corner_r,
                         wall_t, collar_inset, trim_collar_h,
                         fit_clear, trim_skirt_d, lid_cavity_clear, lid_top_t,
                         gasket_w, gasket_groove_d);

        screw_pattern_holes(trim_screws, lid_screw_d, trim_lid_h + 0.02, -0.01);
        screw_pattern_recesses(trim_screws, washer_od, washer_h + 0.02, trim_lid_h - washer_h);
    }
}

// Parameters:
// none; uses trim globals
module trim_gasket() {
    face_gasket(trim_len, trim_wid, trim_corner_r, wall_t, collar_inset, gasket_w, gasket_h);
}

// -----------------------------------------------------------------------------
// Preview assembly
// -----------------------------------------------------------------------------

// Parameters:
// none; uses all module globals and visual offsets
module system_assembly() {
    // Main pod
    color([0.62, 0.66, 0.72]) main_pod_base();
    color([0.82, 0.84, 0.88]) translate([0, 0, main_pod_base_h + explode]) main_pod_lid();
    color([0.94, 0.44, 0.16]) translate([0, 0, main_pod_base_h + explode + main_pod_skirt_d - gasket_h]) main_pod_gasket();

    // Main pod gland hardware preview (front)
    color([0.74, 0.77, 0.82])
        translate([main_pod_len / 2 + pod_gland_frame_t / 2 + 6, 0, pod_gland_z])
            split_gland_frame(pod_gland_frame_w, pod_gland_frame_h, pod_gland_frame_t, pod_gland_corner_r,
                              pod_gland_window_w, pod_gland_window_h,
                              pod_gland_bolt_d, pod_gland_bolt_span_y, pod_gland_bolt_span_z);

    color([0.18, 0.18, 0.18])
        translate([main_pod_len / 2 + pod_gland_frame_t + pod_gland_insert_t / 2 + 10, 0, pod_gland_z])
            split_gland_insert(pod_gland_frame_w, pod_gland_frame_h, pod_gland_insert_t, pod_gland_corner_r,
                               pod_gland_channels, pod_gland_channel_span, pod_gland_slit_w,
                               pod_gland_bolt_d, pod_gland_bolt_span_y, pod_gland_bolt_span_z);

    color([0.70, 0.72, 0.76])
        translate([main_pod_len / 2 - pod_gland_backer_t / 2 - 6, 0, pod_gland_z])
            split_gland_backer(pod_gland_frame_w, pod_gland_frame_h, pod_gland_backer_t, pod_gland_corner_r,
                               pod_gland_window_w, pod_gland_window_h,
                               pod_gland_bolt_d, pod_gland_bolt_span_y, pod_gland_bolt_span_z);

    // Battery module
    color([0.55, 0.58, 0.64])
        translate([0, 0, system_battery_z_offset]) battery_base();
    color([0.78, 0.80, 0.84])
        translate([0, 0, system_battery_z_offset + battery_base_h + explode]) battery_lid();
    color([0.94, 0.44, 0.16])
        translate([0, 0, system_battery_z_offset + battery_base_h + explode + battery_skirt_d - gasket_h]) battery_gasket();

    // Side chambers
    color([0.50, 0.54, 0.60]) translate([0,  system_side_y_offset, 0]) side_base();
    color([0.76, 0.78, 0.82]) translate([0,  system_side_y_offset, side_base_h + explode]) side_lid();
    color([0.94, 0.44, 0.16]) translate([0,  system_side_y_offset, side_base_h + explode + side_skirt_d - gasket_h]) side_gasket();

    color([0.50, 0.54, 0.60]) translate([0, -system_side_y_offset, 0]) side_base();
    color([0.76, 0.78, 0.82]) translate([0, -system_side_y_offset, side_base_h + explode]) side_lid();
    color([0.94, 0.44, 0.16]) translate([0, -system_side_y_offset, side_base_h + explode + side_skirt_d - gasket_h]) side_gasket();

    // Front / rear trim chambers
    color([0.58, 0.61, 0.67]) translate([ system_trim_x_offset, 0, 0]) trim_base();
    color([0.79, 0.81, 0.85]) translate([ system_trim_x_offset, 0, trim_base_h + explode]) trim_lid();
    color([0.94, 0.44, 0.16]) translate([ system_trim_x_offset, 0, trim_base_h + explode + trim_skirt_d - gasket_h]) trim_gasket();

    color([0.58, 0.61, 0.67]) translate([-system_trim_x_offset, 0, 0]) trim_base();
    color([0.79, 0.81, 0.85]) translate([-system_trim_x_offset, 0, trim_base_h + explode]) trim_lid();
    color([0.94, 0.44, 0.16]) translate([-system_trim_x_offset, 0, trim_base_h + explode + trim_skirt_d - gasket_h]) trim_gasket();
}

// -----------------------------------------------------------------------------
// Output switch
// -----------------------------------------------------------------------------
if (part == "main_pod_base")
    main_pod_base();
else if (part == "main_pod_lid")
    main_pod_lid();
else if (part == "main_pod_gasket")
    main_pod_gasket();
else if (part == "battery_base")
    battery_base();
else if (part == "battery_lid")
    battery_lid();
else if (part == "battery_gasket")
    battery_gasket();
else if (part == "side_base")
    side_base();
else if (part == "side_lid")
    side_lid();
else if (part == "side_gasket")
    side_gasket();
else if (part == "trim_base")
    trim_base();
else if (part == "trim_lid")
    trim_lid();
else if (part == "trim_gasket")
    trim_gasket();
else if (part == "pod_gland_frame")
    split_gland_frame(pod_gland_frame_w, pod_gland_frame_h, pod_gland_frame_t, pod_gland_corner_r,
                      pod_gland_window_w, pod_gland_window_h,
                      pod_gland_bolt_d, pod_gland_bolt_span_y, pod_gland_bolt_span_z);
else if (part == "pod_gland_insert")
    split_gland_insert(pod_gland_frame_w, pod_gland_frame_h, pod_gland_insert_t, pod_gland_corner_r,
                       pod_gland_channels, pod_gland_channel_span, pod_gland_slit_w,
                       pod_gland_bolt_d, pod_gland_bolt_span_y, pod_gland_bolt_span_z);
else if (part == "pod_gland_backer")
    split_gland_backer(pod_gland_frame_w, pod_gland_frame_h, pod_gland_backer_t, pod_gland_corner_r,
                       pod_gland_window_w, pod_gland_window_h,
                       pod_gland_bolt_d, pod_gland_bolt_span_y, pod_gland_bolt_span_z);
else if (part == "battery_gland_frame")
    split_gland_frame(battery_gland_frame_w, battery_gland_frame_h, battery_gland_frame_t, battery_gland_corner_r,
                      battery_gland_window_w, battery_gland_window_h,
                      battery_gland_bolt_d, battery_gland_bolt_span_y, battery_gland_bolt_span_z);
else if (part == "battery_gland_insert")
    split_gland_insert(battery_gland_frame_w, battery_gland_frame_h, battery_gland_insert_t, battery_gland_corner_r,
                       battery_gland_channels, battery_gland_channel_span, pod_gland_slit_w,
                       battery_gland_bolt_d, battery_gland_bolt_span_y, battery_gland_bolt_span_z);
else if (part == "battery_gland_backer")
    split_gland_backer(battery_gland_frame_w, battery_gland_frame_h, battery_gland_backer_t, battery_gland_corner_r,
                       battery_gland_window_w, battery_gland_window_h,
                       battery_gland_bolt_d, battery_gland_bolt_span_y, battery_gland_bolt_span_z);
else if (part == "washer")
    sealing_washer();
else
    system_assembly();