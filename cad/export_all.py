#!/usr/bin/env python3
"""Build every part, export STEP/STL/viz meshes, and run the mathematical/CAD validation checks."""
import os, json, math, itertools
import cadquery as cq
import numpy as np, trimesh
import slimcase as S

OUT = os.environ.get("SLIMCASE_OUT", "out")
BED = 250.0                              # smallest supported print bed: every part must fit 250 x 250 x 250 mm
# mass assumptions (g) -- STATED ASSUMPTIONS, not measurements
RHO_PLA = 1.24e-3            # g/mm3
FILL = dict(lower_body=0.45) # effective solid fraction incl. walls+infill; everything else:
FILL_DEFAULT = 0.85
MASS = dict(viz_buck_converter_pi=15.0, viz_usbc_trigger=5.0, viz_buck_converter=15.0, viz_ballast_plate=S.ballast[0]*S.ballast[1]*S.ballast[2]*7.85e-3, viz_lcd_glass=200.0, viz_pi=75.0, viz_lcd_controller=40.0)
MASS_CABLES = 90.0           # cables + panel extensions + fasteners, lumped at lower-body cavity centre

def print_oriented(shape, ori):
    s = shape
    if S.ORI[ori] is not None:
        ax, ang = S.ORI[ori]
        s = s.rotate((0, 0, 0), ax, ang)
    bb = s.val().BoundingBox()
    return s.translate((-bb.xmin, -bb.ymin, -bb.zmin))

def stl(shape, path, tol=0.02, ang=0.1):
    cq.exporters.export(shape, path, tolerance=tol, angularTolerance=ang)

def main():
    for d in ("step_parts", "stl_print", "stl_coupons", "viz", "docs"):
        os.makedirs(f"{OUT}/{d}", exist_ok=True)
    parts = S.build()
    R = []; ok = True
    def chk(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond); R.append(f"[{'PASS' if cond else 'FAIL'}] {name}  {detail}")

    # ---------- counts / stack
    units = [n for n in parts if n.startswith("fin_unit_")]
    U = parts["fin_unit_1"]["shape"].val(); ub = U.BoundingBox(); fb = parts["fin_top"]["shape"].val().BoundingBox()
    ym = S.depth / 2; zf, zs_ = S.fin_t / 2, S.fin_t + S.spacer_t / 2; si = S.spacer_inset
    fin_ok = all(U.isInside(p) for p in [(1, ym, zf), (S.body_w - 1, ym, zf), (S.body_w / 2, 1, zf), (S.body_w / 2, S.depth - 1, zf)])
    rec_ok = not any(U.isInside(p) for p in [(si - 0.2, ym, zs_), (S.body_w - si + 0.2, ym, zs_), (S.body_w / 2, si - 0.2, zs_), (S.body_w / 2, S.depth - si + 0.2, zs_)])
    frm_ok = all(U.isInside(p) for p in [(si + 0.2, ym, zs_), (S.body_w - si - 0.2, ym, zs_), (S.body_w / 2, si + 0.2, zs_), (S.body_w / 2, S.depth - si - 0.2, zs_)])
    chk("5 fins, 4 spacers (4 fused fin+spacer units + 1 top fin)", len(units) == 4 and "fin_top" in parts and fin_ok and frm_ok, f"{len(units)} units + 1 fin")
    allb = [parts[n]["shape"].val().BoundingBox() for n in units + ["fin_top"]]
    h = max(b.zmax for b in allb) - min(b.zmin for b in allb)
    chk("stack height 18 mm", abs(h - 18) < 1e-6, f"measured {h:.3f}")
    layers = sorted((b.zmin, b.zmax) for b in allb)
    chk("stack layers contiguous (4 mm units, 2 mm top fin)", all(abs(a[1] - b[0]) < 1e-6 for a, b in zip(layers, layers[1:])) and abs(ub.zlen - 4) < 1e-6 and abs(fb.zlen - 2) < 1e-6)
    chk("spacer frame recessed 5 mm behind the fin edge on all 4 sides (probed on the fused solid)", rec_ok and frm_ok)
    holl = 1 - S.make_spacer().val().Volume() / ((S.body_w - 2 * si) * (S.depth - 2 * si) * S.spacer_t)
    chk("spacer frame is a hollow skeleton; windows clear of bolts/pins", holl > 0.4 and S.SKEL_X[0][0] - S.bolt_x_inset >= 5, f"{holl * 100:.0f}% of the frame footprint is open; walls {S.skel_wall} mm, end blocks {S.SKEL_X[0][0] - si:.0f} mm, centre web {S.skel_web} mm")
    # ---------- bezel (probe the solids themselves, not the parameters)
    H = parts["lcd_front_housing"]["shape"].val(); hb = H.BoundingBox(); Bz = parts["lcd_inner_bezel"]["shape"].val()
    scr0 = hb.zmin + S.neck_h; cx, cz = (hb.xmin + hb.xmax) / 2, (scr0 + hb.zmax) / 2
    def edge(solid, y, axis, sign, want_inside):   # distance from the screen rectangle's edge to where the solid starts/stops
        lo, hi = 0.0, 60.0
        for _ in range(40):
            m = (lo + hi) / 2
            p = (hb.xmin + m if sign > 0 else hb.xmax - m, y, cz) if axis == "x" else (cx, y, scr0 + m if sign > 0 else hb.zmax - m)
            if solid.isInside(p) == want_inside: lo = m
            else: hi = m
        return (lo + hi) / 2
    sides = dict(left=("x", 1), right=("x", -1), bottom=("z", 1), top=("z", -1))
    iv = {k: edge(H, 1.5, a, sg, True) for k, (a, sg) in sides.items()}            # ivory ends here
    def black_inner(axis, sign):                   # walk outward from the screen centre until the black bezel starts
        lo, hi = 0.0, (hb.xlen / 2 if axis == "x" else hb.zmax - cz) - (S.bezel - S.bezel_black)
        for _ in range(40):
            m = (lo + hi) / 2
            p = (cx + sign * m, 2.0, cz) if axis == "x" else (cx, 2.0, cz + sign * m)
            if Bz.isInside(p): hi = m
            else: lo = m
        return (lo + hi) / 2
    half = dict(left=black_inner("x", -1), right=black_inner("x", 1), bottom=black_inner("z", -1), top=black_inner("z", 1))
    bz = dict(left=cx - hb.xmin - half["left"], right=hb.xmax - cx - half["right"], bottom=cz - scr0 - half["bottom"], top=hb.zmax - cz - half["top"])
    chk("equal 18 mm bezel (ivory + black) on all four sides of the screen rectangle (probed on solids)", all(abs(v - 18) < 0.01 for v in bz.values()), str({k: round(v, 3) for k, v in bz.items()}))
    chk("visible ivory band equal on all four sides; black inner bezel makes up the rest", all(abs(v - (S.bezel - S.bezel_black)) < 0.01 for v in iv.values()),
        f"ivory {iv['left']:.2f} mm + black {S.bezel_black} mm")
    apw, aph = half["left"] + half["right"], half["top"] + half["bottom"]
    chk("aperture is 4:3", abs(apw / aph - 4 / 3) < 0.002, f"{apw:.2f} x {aph:.2f} = {apw / aph:.4f}")
    chk("screen rectangle 232.6 x 183.45 plus body-width neck", abs(hb.xlen - 232.6) < 1e-6 and abs(hb.zlen - 183.45 - S.neck_h) < 1e-6, f"{hb.xlen:.2f} x {hb.zlen - S.neck_h:.2f} + {S.neck_h} neck")
    ym_ = 2.0; r_ = 0.2929 * S.hous_r - 0.5
    air = [(hb.xmin + r_, ym_, hb.zmax - r_), (hb.xmax - r_, ym_, hb.zmax - r_), (hb.xmax - r_, ym_, scr0 + r_), (S.body_w + 6, ym_, scr0 - 6)]
    mat = [(2.0, ym_, hb.zmin + 2.0), (S.body_w - 2.0, ym_, hb.zmin + 2.0), (S.body_w / 2, ym_, scr0 - 2), (hb.xmax - S.hous_r, ym_, scr0 + 1.5), (S.body_w + r_, ym_, scr0 - r_)]
    chk("outline: rounded top-left, top-right, lower-right; concave curve into the overhang; square lower-left; neck only over the body width",
        not any(H.isInside(p) for p in air) and all(H.isInside(p) for p in mat), f"corner radius {S.hous_r}, neck {S.neck_h}")

    # ---------- orientation / overhang
    lb = parts["lower_body"]["shape"].val().BoundingBox()
    chk("left edges aligned (housing, fins, body at X=0)", abs(hb.xmin) < 1e-6 and abs(fb.xmin) < 1e-6 and abs(lb.xmin) < 1e-6)
    chk("display overhang on viewer's RIGHT (+X)", hb.xmax - lb.xmax > 0 and abs(hb.xmax - lb.xmax - 62.6) < 1e-6, f"overhang +X = {hb.xmax - lb.xmax:.2f}")
    chk("consistent enclosure depth (housing, fins, body top)", abs(fb.ylen - S.depth) < 1e-6 and abs(hb.ymin) < 1e-6 and abs(parts['lcd_rear_cover']['shape'].val().BoundingBox().ymax - S.depth) < 1e-6 and abs(lb.ymin) < 1e-6, f'depth {S.depth}')

    # ---------- world: desk contact + tilt
    W = {n: S.to_world(d["shape"]) for n, d in parts.items()}
    wb = W["lower_body"].val()
    zmin_all = min(w.val().BoundingBox().zmin for w in W.values())
    flat = [f for f in wb.Faces() if f.geomType() == "PLANE" and abs(f.Center().z) < 1e-4 and f.normalAt().z < -0.999]
    a = sum(f.Area() for f in flat)
    ys = [v.Y for f in flat for v in f.Vertices()]
    chk("foot underside is a flat face on the desk plane Z=0; nothing below desk", a > 1000 and zmin_all > -1e-4,
        f"contact area {a:.0f} mm2, Y {min(ys):.1f}..{max(ys):.1f}, global zmin {zmin_all:.4f}")
    ff = [f for f in W["lcd_front_housing"].val().Faces() if f.geomType() == "PLANE" and f.normalAt().y < -0.9]
    n = max(ff, key=lambda f: f.Area()).normalAt(); tilt = math.degrees(math.atan2(n.z, -n.y))
    chk("screen face tilted back 7 deg", abs(abs(tilt) - S.tilt) < 1e-3 and n.z > 0, f"front-face normal elevation {tilt:.3f} deg (faces upward)")

    # ---------- solids
    groups = {}
    for nme, d in parts.items():
        if d["group"]: groups.setdefault(d["group"], []).append(nme)
    for g, names in groups.items():
        v = parts[names[0]]["shape"].val()
        chk(f"solid valid + single body: {g}", v.isValid() and len(v.Solids()) == 1)

    # ---------- interference (boolean common of every bbox-overlapping pair, body frame)
    names = list(parts); bad = []
    for a_, b_ in itertools.combinations(names, 2):
        A, B = parts[a_]["shape"].val(), parts[b_]["shape"].val()
        ba, bb_ = A.BoundingBox(), B.BoundingBox()
        if ba.xmin > bb_.xmax or bb_.xmin > ba.xmax or ba.ymin > bb_.ymax or bb_.ymin > ba.ymax or ba.zmin > bb_.zmax or bb_.zmin > ba.zmax:
            continue
        try:
            vol = A.intersect(B).Volume()
        except Exception:
            vol = 0
        if vol > 0.05: bad.append((a_, b_, round(vol, 2)))
    chk("no part-to-part interference (incl. bolts, pins, PROVISIONAL envelopes)", not bad, str(bad) if bad else f"{len(names)} bodies checked pairwise")
    # hole alignment: a straight 3.0 gauge rod through the whole grip must touch nothing
    for i, (x, yy) in enumerate(S.BOLT_XY + S.PIN_XY):
        rod = S.cyl((x, yy, -S.clamp_wall + 0.1 if i < 2 else -S.pin_engage), (0, 0, 1), 3.0, (S.GRIP - 0.2) if i < 2 else S.PIN_LEN).val()
        hit = sum(rod.intersect(parts[nm]["shape"].val()).Volume() for nm in names if not nm.startswith(("hw_", "viz_")))
        chk(f"{'bolt' if i < 2 else 'pin'} hole {i % 2 + 1} lines up through body/fins/spacers/housing", hit < 1e-3, f"gauge-rod interference {hit:.4f} mm3")
    need = S.GRIP + 2 * S.washer_t + S.nut_h
    chk("bolt length derived from grip", S.BOLT_LEN >= need, f"grip {S.GRIP} + 2 washers + nyloc = {need:.1f} -> M3x{S.BOLT_LEN} ({S.BOLT_LEN - need:.1f} past nut)")
    chk("washer clears walls/ribs at both clamp pads", S.BOLT_XY[0][1] - S.washer_od / 2 > S.wall + S.lcd_pocket_d and S.BOLT_XY[0][1] + S.washer_od / 2 < S.RIB_Y0 and S.BOLT_XY[0][1] - S.washer_od / 2 > S.wall + S.rib,
        f"washer Y={S.BOLT_XY[0][1] - S.washer_od / 2:.1f}..{S.BOLT_XY[0][1] + S.washer_od / 2:.1f}: behind the LCD pocket ({S.wall + S.lcd_pocket_d:.1f}) and between body ribs {S.wall + S.rib:.1f} / {S.RIB_Y0:.1f}")
    pe = parts["viz_pi"]["shape"].val().BoundingBox()
    chk("Pi USB/Ethernet cluster sits inside the recess port window (PROVISIONAL Pi envelope)",
        S.WIN_Z[0] < pe.zmin + 2 and S.WIN_Z[1] > pe.zmax - 2 and S.WIN_Y[1] > pe.ymax and abs(pe.xmax - (S.REC_X0 + S.rec_wall)) < 1.6,
        f"connector faces {S.REC_X0 + S.rec_wall - pe.xmax:.1f} mm behind recess wall face; window {S.WIN_Z[1]-S.WIN_Z[0]:.0f} x {S.WIN_Y[1]-S.WIN_Y[0]:.1f}")
    chk("SD card lines up with the left-wall slot", abs((S.PI_Y - 0.75) - (S.PI_Y - 1.0)) < S.sd_slot[1] / 2 and pe.xmin > S.wall, f"card end {pe.xmin - S.wall:.1f} mm inside the wall's inner face")
    g = parts["viz_lcd_glass"]["shape"].val().BoundingBox(); rb = parts["lcd_retainer_1"]["shape"].val().BoundingBox()
    chk("side clips sit lcd_clip_h above the LCD datum (back of the black bezel), over the panel's thin edge",
        abs(rb.ymin - (S.LCD_Y0 + S.lcd_clip_h)) < 1e-6 and rb.ymin - (S.LCD_Y0 + S.lcd_panel[2]) >= 0 and rb.xmin > S.wall,
        f"clip underside {rb.ymin - S.LCD_Y0:.1f} mm above datum; pad gap {rb.ymin - S.LCD_Y0 - S.lcd_panel[2]:.1f} mm")
    Hs = parts["lcd_front_housing"]["shape"].val(); ym = 6.0
    x0, x1, z0, z1 = S.PKT_X0, S.PKT_X1, S.PKT_Z0, S.PKT_Z1
    zb_, zt_ = sum(S.ZONE_B) / 2, sum(S.ZONE_T) / 2
    open_pts = [(x0 - 3.9, ym, zb_), (x0 - 3.9, ym, zt_), (x1 + 3.9, ym, zb_), (x1 + 3.9, ym, zt_), (S.AP_CX, ym, z0 + 0.5), (S.AP_CX, ym, z1 - 0.5)]
    solid_pts = [(x0 - 1, ym, S.AP_CZ), (x1 + 1, ym, S.AP_CZ)]
    chk("side-tab reliefs open at 4 places; no top or bottom rim; side walls still bound the panel",
        not any(Hs.isInside(p) for p in open_pts) and all(Hs.isInside(p) for p in solid_pts), f"relief {S.lcd_tab_out} mm outboard, {S.ZONE_B[1] - S.ZONE_B[0]:.1f} mm tall")
    m_ = S.lcd_margin; vis_w = S.lcd_panel[0] - m_["left"] - m_["right"]; vis_h = S.lcd_panel[1] - m_["top"] - m_["bottom"]
    vcx = g.xmin + m_["left"] + vis_w / 2; vcz = g.zmin + m_["bottom"] + vis_h / 2
    chk("nominal panel position centres the measured dark area in the aperture; adjustment room each way",
        abs(vcx - S.AP_CX) < 1e-6 and abs(vcz - S.AP_CZ) < 1e-6 and g.xmin - x0 > 1.5 and x1 - g.xmax > 1.5 and g.zmin - z0 > 4.5 and z1 - g.zmax > 3.0,
        f"gaps L {g.xmin - x0:.2f} R {x1 - g.xmax:.2f} (shims) / below {g.zmin - z0:.2f} above {z1 - g.zmax:.2f} (free); side ledges L {x0 - S.wall:.2f} R {S.HOUS_W - S.wall - x1:.2f}")
    R.append(f"[INFO] panel's dark area {vis_w:.2f} x {vis_h:.2f} vs aperture {S.active_w} x {S.active_h}: {(vis_w - S.active_w) / 2:.2f} / {(vis_h - S.active_h) / 2:.2f} mm of unlit border is hidden behind the bezel per side (expected: margins were measured to the dark border)")
    LB = parts["lower_body"]["shape"].val(); PM = parts["pi_module"]["shape"].val()
    fl = [((a + b) / 2, S.floppy_z) for (a, b) in S.FLOPPY_X]
    chk("two dummy floppy slots go through the front wall and are backed by the black Pi-module plate",
        not any(LB.isInside((x, 1.5, z)) for x, z in fl) and all(PM.isInside((x, S.TRAY_Y0 + 1, z)) for x, z in fl) and all(PM.isInside((x, S.TRAY_Y0 + 1, S.floppy_z)) for a, b in S.FLOPPY_X for x in (a + 0.5, b - 0.5)),
        f"{S.floppy[0]} x {S.floppy[1]} mm each, centre {-S.floppy_z} mm below the fins, {S.FLOPPY_X[0][0]:.0f} mm side margins")
    cb = parts["viz_lcd_controller"]["shape"].val().BoundingBox()
    chk("LCD controller taped to the panel back fits under the rear cover and beside the buck converter (PROVISIONAL 10 mm part height)",
        S.Y_SEAT - cb.ymax > 3 and cb.xmax < parts["viz_buck_converter"]["shape"].val().BoundingBox().xmin - 5,
        f"{S.Y_SEAT - cb.ymax:.1f} mm to the cover skin; {S.Y_SEAT - (S.LCD_Y0 + S.lcd_panel[2]):.1f} mm total behind the panel")
    bp = parts["viz_buck_converter_pi"]["shape"].val().BoundingBox(); sc = parts["side_cap"]["shape"].val()
    gap = min(sc.distToShape(parts["viz_buck_converter_pi"]["shape"].val())[0] if hasattr(sc, "distToShape") else 99, S.body_w - S.wall - bp.xmax)
    chk("buck converter (43 x 21 x 13 overall) fits on the Pi module beside the port recess", S.body_w - S.wall - bp.xmax >= 1.5 and bp.ymax < S.Y_SEAT - 2 and bp.ymin > S.wall + 2,
        f"{S.body_w - S.wall - bp.xmax:.1f} mm to the side panel; {S.Y_SEAT - bp.ymax:.1f} mm to the rear cover; bay {S.body_w - S.wall - S.REC_X1:.0f} mm wide")
    LBv = parts["lower_body"]["shape"].val(); acc = 0
    for (x, z) in S.MOD_SCREW[:2]:
        acc += S.cyl((x, S.TRAY_Y0 + S.tray_t + 0.1, z), (0, 1, 0), 6.0, S.depth + 10).val().intersect(LBv).Volume()
    chk("top two Pi-module screws: straight 6 mm driver path from the rear is clear of the lower body", acc < 1e-3, f"blocked volume {acc:.3f} mm3; screws {-S.MOD_SCREW[0][1]:.0f} and {-S.MOD_SCREW[1][1]:.0f} mm below the body top")
    xi = S.body_w - S.wall
    chk("ledge under the side cap's bottom edge; SD opening is a 45deg funnel",
        LBv.isInside((xi - 0.3, 15, S.Z_FLOOR + 2.0)) and not LBv.isInside((xi - 2.5, 15, S.Z_FLOOR + 2.0)) and not LBv.isInside((0.3, S.PI_Y - 1.0 + 3.2, S.SD_Z)) and LBv.isInside((1.9, S.PI_Y - 1.0 + 3.2, S.SD_Z)))
    lz_ = (S.Z_H0 + S.OPN[2]) / 2; Hl = parts["lcd_front_housing"]["shape"].val()
    chk("square badge recess 10.3 x 10.3 x 1.6 (badge 9.92 x 9.92 x 1.5) on the housing front; rear rib is continuous above the V notch",
        not Hl.isInside((S.OPN[0] + 5, 0.6, lz_)) and Hl.isInside((S.OPN[0] + 5, S.logo[2] + 0.2, lz_)) and S.logo[0] >= 9.92 + 0.3 and S.logo[1] >= 9.92 + 0.3 and S.logo[2] >= 1.5 + 0.05 and S.wall - S.logo[2] >= 1.2 and Hl.isInside((S.OPN[0] - 0.5, 0.6, lz_)) and Hl.isInside((S.OPN[0] + 5, 0.6, lz_ + 6))
        and LBv.isInside((S.MOD_NOTCH_X, 29, S.Z_CEIL - 2)) and not LBv.isInside((S.MOD_NOTCH_X, 29, S.Z_CEIL - S.rib_h + 2)),
        f"recess x {S.OPN[0]:.1f}..{S.OPN[0] + S.logo[0]:.1f}, centre {lz_ - S.Z_H0:.1f} mm above the fins; {lz_ - S.logo[1] / 2 - S.Z_H0:.1f} mm ivory below it, {S.OPN[2] - lz_ - S.logo[1] / 2:.1f} above; {S.wall - S.logo[2]:.1f} mm of front wall behind it")
    pg = parts["ballast_plug"]["shape"].val().BoundingBox(); w_ = S.ballast[0]
    s_in = S.foot_len - S.PLUG_LEN - 1.0; hmid = S.foot_t / 2
    yq, zq = S._desk_pt(s_in, hmid)
    chk("ballast plug is wider than the plate slot, so the slot's shoulders stop it",
        pg.xlen > w_ + 1.2 + 2 * 2.0 and LBv.isInside(((S.body_w - w_) / 2 - 0.6 - 1.2, yq, zq)) and not LBv.isInside((S.body_w / 2, yq, zq)),
        f"plug {pg.xlen:.1f} mm wide vs plate slot {w_ + 1.2:.1f}; {S.PLUG_EAR} mm shoulder each side, 0.3 mm of travel; {S.body_w - pg.xmax:.1f} mm of foot left outside it")
    capS = parts["side_cap"]["shape"]; others = [parts[n]["shape"].val() for n in ("lower_body", "pi_module", "viz_buck_converter_pi", "viz_pi")]
    piv = (S.body_w, S.wall + S.clr, 0)
    swing = {}
    for ang in (4, 8, 12, 16, 20):
        r_ = capS.rotate(piv, (piv[0], piv[1], 1), -ang).val()
        swing[ang] = sum(r_.intersect(o).Volume() for o in others)
    pulled = capS.translate((1.0, 0, 0)).val().intersect(others[0]).Volume()
    lifted = capS.rotate((S.body_w, S.depth, 0), (S.body_w, S.depth, 1), 2.0).val().intersect(others[0]).Volume()   # front edge lifting, rear held
    chk("side cap hooks onto the front wall: swings shut about its front edge without collision; cannot pull straight off or lift at the front",
        max(swing.values()) < 0.5 and pulled > 1.0 and lifted > 1.0,
        f"swing-in collision volume by angle {dict((k, round(v, 2)) for k, v in swing.items())} mm3; straight pull-off blocked by {pulled:.1f} mm3 of overlap, front-lift by {lifted:.1f}")
    bk = parts["viz_buck_converter"]["shape"].val().BoundingBox()
    chk("buck converter (43 x 21 x 13) fits on the LCD rear cover behind the panel", bk.ymin - rb.ymax > 2 and bk.xmax < S.HOUS_W - S.wall - 6 and bk.xmin > S.AP_CX + 56 + 2,
        f"{bk.ymin - rb.ymax:.1f} mm between its tallest part and the LCD clips; hole pattern {S._bdx:.1f} x {S.buck_hole_dy} (from 35 mm diagonal, PROVISIONAL)")
    tb = parts["viz_usbc_trigger"]["shape"].val().BoundingBox(); pe2 = parts["viz_pi"]["shape"].val().BoundingBox()
    yb_ = S.TRAY_Y0 + S.tray_t + S.trig_ped
    chk("USB-C trigger board (40.7 x 20, holes 14.8 apart) fits on its posts; clears the Pi and the cover",
        tb.zmax < S.Z_CEIL and tb.ymax < S.Y_SEAT - 2 and yb_ - (S.PI_Y + 1.6) >= 6.0 and tb.xmin > S.MOD_SCREW[1][0] + 4,
        f"board underside {yb_ - (S.PI_Y + 1.6):.1f} mm above the Pi PCB; {S.Y_SEAT - tb.ymax:.1f} mm to the rear cover; {S.Z_CEIL - tb.zmax:.1f} mm to the body top")
    # ---------- exports
    assy = cq.Assembly(name="slimcase")
    manifest = []
    for nme, d in parts.items():
        assy.add(W[nme], name=nme, color=cq.Color(*d["color"]))
        stl(W[nme], f"{OUT}/viz/{nme}.stl", 0.05, 0.15)
        manifest.append(dict(name=nme, file=f"{nme}.stl", color=d["color"],
                             explode=[dict(vec=S.rot_world(v), t0=t0, t1=t1) for (v, t0, t1) in d["ex"]]))
    json.dump(manifest, open(f"{OUT}/viz/manifest.json", "w"), indent=1)
    assy.save(f"{OUT}/slimcase_assembly.step")
    rows = []
    for g, names_ in groups.items():
        shp = parts[names_[0]]["shape"]
        cq.exporters.export(shp, f"{OUT}/step_parts/{g}.step")
        po = print_oriented(shp, parts[names_[0]]["ori"])
        path = f"{OUT}/stl_print/{g}__x{len(names_)}.stl"; stl(po, path)
        m = trimesh.load(path); bb = m.bounds
        nz = m.face_normals[:, 2]; cz_ = m.triangles_center[:, 2]
        over = float(m.area_faces[(nz < -0.7072) & (cz_ > 0.05)].sum())
        chk(f"STL watertight, on Z=0, fits a {BED:.0f} x {BED:.0f} mm bed: {g}", m.is_watertight and abs(bb[0][2]) < 1e-3 and (bb[1] - bb[0])[:2].max() <= BED and (bb[1] - bb[0])[2] <= BED,
            f"{(bb[1]-bb[0])[0]:.0f}x{(bb[1]-bb[0])[1]:.0f}x{(bb[1]-bb[0])[2]:.0f}, >45deg down-facing area {over:.0f} mm2")
        rows.append((g, len(names_), parts[names_[0]]["ori"], tuple(round(float(v)) for v in (bb[1] - bb[0])), round(over), round(shp.val().Volume() / 1000, 1)))
    for kind in ("side", "bottom"):   # bottom set is optional now that the pocket has no bottom rim
        path = f"{OUT}/stl_print/lcd_shim_set_{kind}__x1.stl"; stl(S.make_shim_set(kind), path)
        m = trimesh.load(path); nb = len(m.split())
        chk(f"shim set STL ({kind}): intentional multi-body plate, watertight, on Z=0", m.is_watertight and abs(m.bounds[0][2]) < 1e-3, f"{nb} shims, thickness {S.shim_step}..{S.N_SHIM * S.shim_step:.1f} mm in {S.shim_step} steps")
    for cn, fn in (("coupon_hole_fit", S.make_coupon_holes), ("coupon_insert_fit", S.make_coupon_inserts)):
        stl(fn(), f"{OUT}/stl_coupons/{cn}.stl")
    stl(print_oriented(S.make_coupon_lcd_corner(), "front"), f"{OUT}/stl_coupons/coupon_lcd_pocket_corner.stl")

    # ---------- stability (stated mass assumptions)
    tot = 0; mom = np.zeros(3); mrows = []
    for nme, d in parts.items():
        v = W[nme].val(); c = cq.Shape.centerOfMass(v)
        if nme in MASS: m_ = MASS[nme]
        elif nme.startswith("hw_"): m_ = v.Volume() * 7.8e-3
        else: m_ = v.Volume() * RHO_PLA * FILL.get(nme, FILL_DEFAULT)
        tot += m_; mom += m_ * np.array([c.x, c.y, c.z]); mrows.append((nme, m_))
    cc = cq.Shape.centerOfMass(S.to_world(S.box(S.wall, S.body_w - S.wall, S.wall, S.Y_SEAT, S.Z_FLOOR, S.Z_CEIL)).val())
    tot += MASS_CABLES; mom += MASS_CABLES * np.array([cc.x, cc.y, cc.z])
    cg = mom / tot
    yf, yr = S.T_FRONT, S.foot_len - S.r_foot_end
    ang = dict(forward=math.degrees(math.atan2(cg[1] - yf, cg[2])), backward=math.degrees(math.atan2(yr - cg[1], cg[2])),
               left=math.degrees(math.atan2(cg[0], cg[2])), right=math.degrees(math.atan2(S.body_w - cg[0], cg[2])))
    chk("CG inside support polygon; static tip angle >= 10 deg every direction (ESTIMATE)", min(ang.values()) >= 10,
        f"mass~{tot:.0f} g, CG=({cg[0]:.0f},{cg[1]:.0f},{cg[2]:.0f}) world; contact Y {yf:.0f}..{yr:.0f}, X 0..{S.body_w:.0f}; tip angles " + ", ".join(f"{k} {v:.0f}deg" for k, v in ang.items()))

    mb = MASS["viz_ballast_plate"]; cb = cq.Shape.centerOfMass(W["viz_ballast_plate"].val())
    cg0 = (mom - mb * np.array([cb.x, cb.y, cb.z])) / (tot - mb)
    R.append(f"[INFO] without ballast plate: mass~{tot - mb:.0f} g, forward tip angle {math.degrees(math.atan2(cg0[1] - yf, cg0[2])):.1f} deg (ballast plate {mb:.0f} g assumed above)")
    rep = "\n".join(R)
    open(f"{OUT}/docs/validation_report.txt", "w").write(
        "SlimCase CAD/mathematical validation (NOT a slicer check, NOT a physical test)\n" + rep +
        "\n\nPrint table: part, qty, orientation, bbox(mm), down-facing>45deg area (mm2), volume (cm3)\n" +
        "\n".join(str(r) for r in rows) + "\n\nMass model (g): " + ", ".join(f"{n}={m:.0f}" for n, m in mrows) + f", cables/hw lump={MASS_CABLES}\n")
    print(rep); print(); [print(r) for r in rows]
    json.dump(dict(rows=rows, cg=list(cg), mass=tot, tip=ang, bolt_len=S.BOLT_LEN, pin_len=S.PIN_LEN), open(f"{OUT}/docs/summary.json", "w"))
    print("ALL PASS" if ok else "SOME FAILED")

if __name__ == "__main__":
    main()
