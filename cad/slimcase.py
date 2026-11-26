#!/usr/bin/env python3
"""
SlimCase - parametric FDM enclosure (CadQuery).  All units mm.

DESIGN (BODY) FRAME  -- everything is modelled un-tilted:
    +X = viewer's RIGHT when facing the screen   (left edges of all sections at X=0)
    +Y = depth, front face at Y=0, rear at Y=DEPTH (viewer stands at -Y, looks along +Y)
    +Z = up along the enclosure axis; Z=0 is the top of the lower body / bottom of fin stack
WORLD FRAME -- body frame rotated -TILT about X (top leans back, toward +Y), then shifted so
    the desk is Z=0 and the virtual front-bottom corner of the body is Y=0.
"""
import math, json, os, sys
import cadquery as cq

# ----------------------------------------------------------------------------- parameters
P = dict(
    # display
    active_w=196.6, active_h=147.45,      # 9.7" 4:3 active area (nominal)
    bezel=18.0,                           # ONE parameter, all four sides
    # LCD panel as MEASURED on one panel: 8-3/16" x 6-9/16" excluding tabs; side thickness 2.8
    lcd_panel=(207.96, 166.69, 2.8),
    lcd_margin=dict(left=5.0, right=2.5, bottom=6.0, top=9.5),   # panel edge -> edge of the black border, from the front; measured values, turned 180deg after top/bottom turned out to be swapped
    lcd_adj=1.6,                          # pocket is this much bigger than the panel on each side; shims take up the gap
    shim_step=0.4,                        # shim thickness increment (2 layers at 0.2 mm)
    lcd_pocket_d=6.5,                     # PROVISIONAL pocket wall height (thick bottom edge of the panel + margin)
    lcd_bottom=(20.0, 5.5, 0.85),         # thicker strip along the BOTTOM edge: height PROVISIONAL, thickness 5.5 and 85% of width as reported
    lcd_clip_h=3.0,                       # underside of the side clips above the pocket floor (panel 2.8 + thin pad)
    lcd_tab_out=5.0, lcd_tab_zone=10.0, lcd_tab_slack=3.0,   # side-tab reliefs: tabs ~4 mm proud within ~10 mm of each corner, +/- slack for vertical adjustment
    # housing outline (per the design sketch): body-width neck below the screen, soft radius on the exposed corners
    neck_h=14.0, hous_r=8.0,
    logo=(10.3, 10.3, 1.6), logo_r=1.4,   # square badge recess (w, h, depth; corner radius) in the ivory below the screen, left edge on the bezel opening's left edge.
                                          # Badge: 9.92 x 9.92 plate, 0.5 thick (0.4 chamfer underneath) + raised logo, 1.5 total; 0.19 clearance per side, 0.1 deeper than the badge
    # black inner bezel: drops in from behind, trapped by the LCD
    bezel_black=5.9,                      # limited to ~6: the opening must stay inside the LCD pocket (right side) or the housing needs supports
    bez_flange_t=1.0, bez_flange_w=2.0, bez_r=3.0, bez_clr=0.2,
    # dummy floppy slots in the lower-body front (width, height), centre height below the fins, gap between them
    floppy=(60.0, 4.0), floppy_z=-25.0, floppy_gap=10.0,
    rib_front=4.0,                        # front ribs are shallow so the Pi-module plate laps over them
    # body
    body_w=170.0, straight_h=105.0, depth=36.0, wall=3.0, clamp_wall=5.0,
    tilt=7.0,
    foot_t=10.0, foot_len=150.0,           # foot_len = desk length measured from virtual front corner
    r_front=24.0, r_rear=14.0, r_foot_end=2.0,   # r_rear is limited by the rear-opening height
    rear_bevel=3.0,                       # 45deg bevel on all rear edges (prints without support)
    side_thick=2.5,                       # local wall thickening behind the side rear bevels
    lcd_cap_t=5.0,                        # LCD rear cover is a bevelled cap over the housing wall ends
    sill_h=4.0,                           # lip under the rear opening that the cover hooks behind
    # ballast: steel flat plate slid into a slot in the foot from the rear edge (x-width, length, thickness)
    ballast=(152.4, 120.0, 4.76), ballast_clr=0.45, ballast_front=22.0,
    # fin stack
    n_fins=5, fin_t=2.0, spacer_t=2.0, spacer_inset=5.0,
    passage_w=80.0, passage_d=16.0,
    bolt_clear=3.4, pin_d=3.0, pin_clear=0.3, pin_engage=3.5,
    bolt_x_inset=18.0, bolt_pin_off=4.0,  # bolt and pin share one end block: bolt toward the front, pin toward the rear
    skel_wall=4.0, skel_end=6.0, skel_web=4.0,   # hollow fin stack: frame wall, end-block margin past the bolt, centre web
    washer_od=7.0, washer_t=0.5, nut_h=4.0, shcs_head_d=5.5, shcs_head_h=3.0,
    # fits / fasteners
    clr=0.2,                              # general printed sliding clearance
    insert_d=4.0, insert_d_v=4.2, insert_depth=5.5,   # M3x5 heat-set pilots from fit-test coupons: 4.0 for holes that print sideways, 4.2 for holes that print vertically
    csk_d=6.5,
    cover_t=3.0, rib=7.0, rib_h=9.0, tab_len=12.0,
    # Pi module = tray + open port recess in ONE part (Pi ports exposed through the recess side wall)
    pi_x0=6.5,                            # Pi PCB left edge (SD end, faces the left wall)
    pi_z0=-93.0,                          # Pi PCB lower edge
    pi_usb_overhang=3.0,                  # connector faces beyond PCB edge (Pi 4B/5 nominal)
    tray_t=2.5, tray_boss_h=4.0, pi_standoff=3.0,
    rec_wall=2.5, rec_w=51.0,             # recess inner width = plug + cable-bend room
    rec_z=(-96.5, -14.5),                 # recess outer extent
    port_win_margin=1.0,                  # window around the USB/Ethernet cluster (fits Pi 4B and Pi 5)
    # USB-C PD trigger board, from the seller's drawing: 40.7 x 20 board, two 3 mm holes 15 mm apart flanking the connector
    usbc_slot=(9.4, 3.6), usbc_z=-26.0, trig_board=(40.7, 20.0, 1.6), trig_hole_pitch=14.8,
    trig_hole_end=3.15,                   # measured: 3.2 mm holes, edge 1.5-1.6 from the connector-end edge and 1.0 from the sides
    trig_overhang=1.5,                    # PROVISIONAL: receptacle sticks out past the board edge
    trig_ped=11.0,                        # board underside above the tray plate: clears everything on the Pi incl. a Pi 4 audio jack
    # LM2596-style buck converter from the seller's picture: 43 x 21 board, 13 tall, two diagonal holes 35 mm apart
    buck_board=(43.0, 21.0, 13.0), buck_hole_diag=35.0,
    buck_hole_dy=16.0,                    # PROVISIONAL: hole spacing across the 21 mm width (the 35 mm diagonal then fixes the other)
    buck_standoff=3.0, buck_cx=185.0,
    buck_pi_stand=2.5, buck_pi_c=(18.5, -52.0),   # second mount: on the outside of the port-recess wall, board on edge (centre y, z)
    sd_slot=(15.0, 4.0),                  # SD access slot in the left wall (z, y)
    # LCD controller, PROVISIONAL (no drawing supplied): 72x51 board, 65x44 hole pattern
    ctl_board=(72.0, 51.0), ctl_holes=(65.0, 44.0), ctl_standoff=4.0,
    chamfer=1.0,
)
globals().update(P)

# ----------------------------------------------------------------------------- derived
HOUS_W = active_w + 2 * bezel                 # 232.6
HOUS_H = active_h + 2 * bezel                 # 183.45
OVERHANG = HOUS_W - body_w                    # 62.6 (to viewer's right, left edges aligned)
STACK_H = n_fins * fin_t + (n_fins - 1) * spacer_t   # 18
Z_H0 = STACK_H                                # display housing bottom
Z_SCR0 = Z_H0 + neck_h                        # bottom of the screen rectangle (the neck fills Z_H0..Z_SCR0 over the body width)
Z_H1 = Z_SCR0 + HOUS_H
AP_CX, AP_CZ = HOUS_W / 2, Z_SCR0 + HOUS_H / 2  # aperture centre
LCD_Y0 = wall + bez_flange_t                  # LCD front-face datum: it rests on the back of the black bezel
OPN = (AP_CX - active_w / 2 - bezel_black, AP_CX + active_w / 2 + bezel_black,
       AP_CZ - active_h / 2 - bezel_black, AP_CZ + active_h / 2 + bezel_black)   # ivory opening that the black bezel fills
PASS_X0 = body_w / 2 - passage_w / 2; PASS_X1 = PASS_X0 + passage_w
PASS_Y0 = depth / 2 - passage_d / 2;  PASS_Y1 = PASS_Y0 + passage_d
BOLT_XY = [(bolt_x_inset, depth / 2 - bolt_pin_off), (body_w - bolt_x_inset, depth / 2 - bolt_pin_off)]
PIN_XY = [(bolt_x_inset, depth / 2 + bolt_pin_off), (body_w - bolt_x_inset, depth / 2 + bolt_pin_off)]
SKEL_Y = (spacer_inset + skel_wall, depth - spacer_inset - skel_wall)     # hollow windows through every fin and spacer
SKEL_X = [(bolt_x_inset + skel_end, body_w / 2 - skel_web / 2), (body_w / 2 + skel_web / 2, body_w - bolt_x_inset - skel_end)]
GRIP = clamp_wall + STACK_H + clamp_wall
_need = GRIP + 2 * washer_t + nut_h + 1.0
BOLT_LEN = next(L for L in (6, 8, 10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 60) if L >= _need)
PIN_LEN = STACK_H + 2 * pin_engage
Z_FLOOR = -straight_h                         # cavity floor (body frame)
Z_CEIL = -clamp_wall
TAU = math.radians(tilt)
T_FRONT = r_front / math.tan(math.radians(90 - tilt) / 2)   # tangent length of front curve
Z_A = -(straight_h + T_FRONT)                 # virtual front-bottom corner (Y=0)
_B_Z = Z_A + foot_t / math.cos(TAU) + depth * math.tan(TAU)             # foot top where it meets the rear face
Z_OPEN = max(Z_FLOOR + sill_h, _B_Z + r_rear / math.tan(math.radians(90 - tilt) / 2) + 1.0)   # rear opening starts above sill / foot fillet
Z_SCR_LOW = -84.0                         # lower-right cover screw: raised so a driver clears the foot
X_COV0, X_COV1 = wall + side_thick, body_w - wall - side_thick
Y_LCDW = depth - lcd_cap_t                # LCD housing wall ends / cap seat
RIB_Y0 = depth - cover_t - rib                # rear ribs
Y_SEAT = depth - cover_t                      # inner face of rear covers
PI_BOARD = (85.0, 56.0)
REC_X0 = pi_x0 + PI_BOARD[0] + 1.5        # recess outer-left wall, just clear of the PCB edge
REC_X1 = REC_X0 + 2 * rec_wall + rec_w
TRAY_X0 = wall + 1.5
TRAY_Z = (pi_z0 - 0.5, Z_CEIL - 0.5)
TRAY_Y0 = wall + tray_boss_h
PI_Y = TRAY_Y0 + tray_t + pi_standoff     # PCB underside
MOD_SCREW = [(11.5, -20.0), (44.0, -17.0), (REC_X0 + 19.0, -62.0), (REC_X1 - 12.0, -45.0)]   # (X,Z); top two sit BELOW the rear-cover rib so a driver / insert iron reaches them from behind; all clear of the floppy slots
MOD_NOTCH_X = 44.0                        # the rear rib is notched behind this screw (it can't go lower without showing in a floppy slot)
WIN_Z = (pi_z0 + 2 - port_win_margin, pi_z0 + 54 + port_win_margin)
WIN_Y = (PI_Y + 1.6 - 0.5, PI_Y + 1.6 + 16 + port_win_margin)
RIB_X1 = REC_X0 - 5.0                     # rear/front ribs stop short of the recess
SD_Z = pi_z0 + PI_BOARD[1] / 2
PI_HOLES = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]   # Pi 4B/5 (same pattern), M2.5
# nominal panel position: visible image centred in the aperture
PANEL_CX = AP_CX + (lcd_margin["right"] - lcd_margin["left"]) / 2
PANEL_CZ = AP_CZ + (lcd_margin["top"] - lcd_margin["bottom"]) / 2
PKT_X0, PKT_X1 = PANEL_CX - lcd_panel[0] / 2 - lcd_adj, PANEL_CX + lcd_panel[0] / 2 + lcd_adj
PKT_Z0, PKT_Z1 = Z_SCR0 + wall, Z_H1 - wall   # no top/bottom rims: the pocket runs the full inside height for free vertical adjustment
_pb, _pt = PANEL_CZ - lcd_panel[1] / 2, PANEL_CZ + lcd_panel[1] / 2
ZONE_B = (max(_pb - lcd_tab_slack, PKT_Z0), _pb + lcd_tab_zone + lcd_tab_slack)        # side-tab relief heights
ZONE_T = (_pt - lcd_tab_zone - lcd_tab_slack, min(_pt + lcd_tab_slack, PKT_Z1 - 1.5))
LEDGE_MIN = min(PKT_X0 - wall, HOUS_W - wall - PKT_X1)                        # narrower side ledge sets the (identical) clip geometry
RET_Z = [PANEL_CZ - 45, PANEL_CZ + 45]
RET_X = [PKT_X0 - LEDGE_MIN / 2, PKT_X1 + LEDGE_MIN / 2]
N_SHIM = int(round(2 * lcd_adj / shim_step))
_XL, _XR = (wall + PKT_X0) / 2, HOUS_W - wall - 4.5       # cover-screw columns on the side ledges, just clear of the tab reliefs
LCDCOV_SCREW = [(_XL, ZONE_B[1] + 6.75), (_XR, ZONE_B[1] + 6.75), (_XL, ZONE_T[0] - 6.75), (_XR, ZONE_T[0] - 6.75)]
FLOPPY_X = [((body_w - floppy_gap) / 2 - floppy[0], (body_w - floppy_gap) / 2), ((body_w + floppy_gap) / 2, (body_w + floppy_gap) / 2 + floppy[0])]
BUCK_C = (buck_cx, AP_CZ)
_bdx = math.sqrt(buck_hole_diag ** 2 - buck_hole_dy ** 2)
BUCK_HOLES = [(sx * buck_hole_dy / 2, sz * _bdx / 2) for sx in (-1, 1) for sz in (-1, 1)]   # all four corners offered: the board uses whichever diagonal its holes are on
X_SCR_R = body_w - wall - tab_len + 4.5
COVER_SCREW = [(20.0, Z_CEIL - rib_h / 2), (70.0, Z_CEIL - rib_h / 2), (X_SCR_R, Z_CEIL - rib_h / 2), (X_SCR_R, Z_SCR_LOW)]
HOOK_X = [(28.0, 44.0), (60.0, 76.0)]     # cover bottom hooks (replace the inaccessible lower screws)
CAP_TOP_SCREW = (body_w - wall - tab_len / 2, wall + rib / 2)     # (X,Y) through top wall, hidden by fin
CTL_C = (body_w / 2, Z_H0 + clamp_wall + 12 + ctl_board[1] / 2)

# ----------------------------------------------------------------------------- helpers
def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))

def cyl(p, d, dia, h):
    return cq.Workplane(obj=cq.Solid.makeCylinder(dia / 2, h, cq.Vector(*p), cq.Vector(*d)))

def csk(p, d, thru=cover_t):
    """90deg countersunk M3 clearance hole starting at surface point p, going along d."""
    h = (csk_d - bolt_clear) / 2
    c = cq.Workplane(obj=cq.Solid.makeCone(csk_d / 2, bolt_clear / 2, h, cq.Vector(*p), cq.Vector(*d)))
    back = tuple(-0.01 * k for k in d)
    return c.union(cyl((p[0] + back[0], p[1] + back[1], p[2] + back[2]), d, bolt_clear, thru + 0.02))

def rounded_profile(pts, radii):
    """Closed 2D outline with a tangent arc of the given radius at each vertex (0 = sharp)."""
    n = len(pts); segs = []
    for i, (p, r) in enumerate(zip(pts, radii)):
        a, b = pts[i - 1], pts[(i + 1) % n]
        if r <= 0:
            segs.append((p, None, p)); continue
        d1 = (a[0] - p[0], a[1] - p[1]); l1 = math.hypot(*d1); d1 = (d1[0] / l1, d1[1] / l1)
        d2 = (b[0] - p[0], b[1] - p[1]); l2 = math.hypot(*d2); d2 = (d2[0] / l2, d2[1] / l2)
        phi = math.acos(max(-1, min(1, d1[0] * d2[0] + d1[1] * d2[1])))
        t = r / math.tan(phi / 2)
        assert t < l1 and t < l2, "fillet too large for profile"
        bis = (d1[0] + d2[0], d1[1] + d2[1]); lb = math.hypot(*bis); bis = (bis[0] / lb, bis[1] / lb)
        cdist = r / math.sin(phi / 2)
        c = (p[0] + bis[0] * cdist, p[1] + bis[1] * cdist)
        m = (c[0] - bis[0] * r, c[1] - bis[1] * r)
        segs.append(((p[0] + d1[0] * t, p[1] + d1[1] * t), m, (p[0] + d2[0] * t, p[1] + d2[1] * t)))
    return segs

def profile_wp(segs):
    w = cq.Workplane("YZ").moveTo(*segs[0][2])
    for t1, m, t2 in segs[1:] + segs[:1]:
        w = w.lineTo(*t1)
        if m is not None:
            w = w.threePointArc(m, t2)
    return w.close()

def _xz_wire(segs):
    w = cq.Workplane("XY").moveTo(*segs[0][2])
    for t1, m, t2 in segs[1:] + segs[:1]:
        w = w.lineTo(*t1)
        if m is not None:
            w = w.threePointArc(m, t2)
    return w.close()

def hous_slab(y0, y1, inset=0.0):
    """Display-housing outline (optionally offset inward) as a slab from y0 to y1.
    Outline: left edge straight down to the fins, body-width neck, concave curve out to the overhang, three rounded corners."""
    pts = [(0, Z_H0), (body_w, Z_H0), (body_w, Z_SCR0), (HOUS_W, Z_SCR0), (HOUS_W, Z_H1), (0, Z_H1)]
    w = _xz_wire(rounded_profile(pts, [0, 0, hous_r, hous_r, hous_r, hous_r]))
    if inset: w = w.offset2D(-inset)
    return w.extrude(y1 - y0).rotate((0, 0, 0), (1, 0, 0), 90).translate((0, y1, 0))

def rbox(x0, x1, y0, y1, z0, z1, r):
    """Box with its four Y-parallel edges rounded."""
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0)).edges("|Y").fillet(r)

def body_profile_pts():
    e = (math.cos(TAU), math.sin(TAU)); n = (-math.sin(TAU), math.cos(TAU))
    A = (0.0, Z_A)
    E0 = (A[0] + e[0] * foot_len, A[1] + e[1] * foot_len)
    E1 = (E0[0] + n[0] * foot_t, E0[1] + n[1] * foot_t)
    s = (depth + foot_t * math.sin(TAU)) / math.cos(TAU)
    B = (A[0] + n[0] * foot_t + e[0] * s, A[1] + n[1] * foot_t + e[1] * s)
    return [A, E0, E1, B, (depth, -rear_bevel), (depth - rear_bevel, 0.0), (0.0, 0.0)], [r_front, r_foot_end, r_foot_end, r_rear, 0, 0, 0]

def desk_z(y):
    """Body-frame Z of the desk plane at depth y."""
    return Z_A + y * math.tan(TAU)

def desk_d(y, z):
    """Height above the desk plane of body-frame point (y,z)."""
    return (z - Z_A) * math.cos(TAU) - y * math.sin(TAU)

def _desk_pt(s_, h):
    """Body-frame (y,z) of a point s_ along the desk from the virtual front corner, h above the desk."""
    return (s_ * math.cos(TAU) - h * math.sin(TAU), Z_A + s_ * math.sin(TAU) + h * math.cos(TAU))

def _desk_slab(s0, s1, h0, h1, x0, x1):
    pts = [_desk_pt(s0, h0), _desk_pt(s1, h0), _desk_pt(s1, h1), _desk_pt(s0, h1)]
    return cq.Workplane("YZ").polyline(pts).close().extrude(x1 - x0).translate((x0, 0, 0))

PLUG_EAR = 2.5                            # the slot mouth and the plug are this much wider than the plate on each side
PLUG_LEN = 6.9                            # depth of the widened mouth; its inner shoulders stop the plug

def ballast_slot():
    """Slot parallel to the desk, open at the rear edge of the foot; the plate slides in from behind.
    The last PLUG_LEN is wider than the plate: the shoulders where it narrows are the plug's stops."""
    w, L, t = ballast; hh = t + ballast_clr; h0 = (foot_t - hh) / 2
    s = _desk_slab(ballast_front, foot_len + 1, h0, h0 + hh, (body_w - w) / 2 - 0.6, (body_w + w) / 2 + 0.6)
    return s.union(_desk_slab(foot_len - PLUG_LEN, foot_len + 1, h0, h0 + hh, (body_w - w) / 2 - 0.6 - PLUG_EAR, (body_w + w) / 2 + 0.6 + PLUG_EAR))

def make_ballast():
    w, L, t = ballast; h0 = (foot_t - t) / 2
    assert ballast_front + 1 + L <= foot_len - PLUG_LEN + 0.01, "plate would sit under the plug"
    return _desk_slab(ballast_front + 1, ballast_front + 1 + L, h0, h0 + t, (body_w - w) / 2, (body_w + w) / 2)

def make_ballast_plug():
    """Strip that closes the slot mouth behind the plate. Its ends are wider than the plate slot, so it stops on the
    mouth's shoulders 0.3 mm in, whether or not the plate is there to stop it."""
    w, L, t = ballast; hh = t + ballast_clr - 0.15; h0 = (foot_t - hh) / 2
    return _desk_slab(foot_len - PLUG_LEN + 0.3, foot_len - 0.6, h0, h0 + hh, (body_w - w) / 2 - 0.3 - PLUG_EAR, (body_w + w) / 2 + 0.3 + PLUG_EAR)

class PtSel(cq.Selector):
    def __init__(self, fn): self.fn = fn
    def filter(self, objs): return [o for o in objs if self.fn(o.Center())]

def _rear_chain(c):   # rear face, foot fillet and foot-top edges of the side profile
    return c.y > depth - 0.01 and desk_d(c.y, c.z) > foot_t - 0.01

def _other_chain(c):  # front face, front curve, underside, foot end
    return (not _rear_chain(c)) and c.z < -rear_bevel - 0.01

def _tri_prism(p3, vec):
    f = cq.Face.makeFromWires(cq.Wire.makePolygon([cq.Vector(*p) for p in p3], close=True))
    return cq.Workplane(obj=cq.Solid.extrudeLinear(f, cq.Vector(*vec)))

def rear_bevel_cutter():
    """45deg bevel of size rear_bevel along the LEFT side's rear chain: rear face -> concave foot fillet -> foot top."""
    b = rear_bevel; r = r_rear
    yc = depth + r; zc = Z_A + (foot_t + r + yc * math.sin(TAU)) / math.cos(TAU)        # fillet axis (parallel to X)
    rear = _tri_prism([(-1, depth + 1, zc), (b + 1, depth + 1, zc), (-1, depth - b - 1, zc)], (0, 0, 60 - zc))
    ring = cq.Workplane("XY").polyline([(-1, r - 1), (b + 1, r - 1), (-1, r + b + 1)]).close().revolve(360, (0, 0, 0), (1, 0, 0)).translate((0, yc, zc))
    yt, zt = yc + r * math.sin(TAU), zc - r * math.cos(TAU)                                # tangent point on the foot top
    s0 = yt * math.cos(TAU) + (zt - Z_A) * math.sin(TAU)
    P = lambda x, h: (x,) + _desk_pt(s0, h)
    L = foot_len + 5 - s0
    foot = _tri_prism([P(-1, foot_t + 1), P(b + 1, foot_t + 1), P(-1, foot_t - b - 1)], (0, L * math.cos(TAU), L * math.sin(TAU)))
    return rear.union(ring).union(foot)

def _bevel_prism(x_out, sign):
    """Cutter for a rear_bevel on the vertical rear edge at X=x_out (sign=+1: material lies toward +X)."""
    b = rear_bevel
    pts = [(x_out - sign, depth - b - 1), (x_out - sign, depth + 1), (x_out + sign * (b + 1), depth + 1)]
    return cq.Workplane("XY").polyline(pts).close().extrude(240).translate((0, 0, -180))

def try_chamfer(wp, sel, c):
    try:
        return sel(wp).chamfer(c)
    except Exception as ex:
        print("  (chamfer skipped:", str(ex)[:60], ")")
        return wp

# ----------------------------------------------------------------------------- parts
def make_lower_body():
    pts, rr = body_profile_pts()
    b = profile_wp(rounded_profile(pts, rr)).extrude(body_w)
    for f in ("<X", ">X"):
        b = try_chamfer(b, lambda w: w.faces(f).edges(PtSel(_other_chain)), chamfer)
    left = rear_bevel_cutter()                # rear face + foot fillet + foot top, both sides (boolean: robust where chamfer() is not)
    b = b.cut(left).cut(left.mirror("YZ", (body_w / 2, 0, 0)))
    # cavity: open to the right (inset side cap); rear opening starts above the sill
    b = b.cut(box(wall, body_w + 1, wall, Y_SEAT, Z_FLOOR, Z_CEIL))
    b = b.cut(box(wall, body_w + 1, Y_SEAT - 1, depth + 1, Z_OPEN, Z_CEIL))
    # left wall thickened behind the rear bevel (the bevel would otherwise thin the 3 mm wall to nothing)
    b = b.union(box(wall - 0.5, wall + side_thick, Y_SEAT - 4, depth, Z_OPEN - 0.5, Z_CEIL + 0.5).cut(_bevel_prism(0, 1)))
    xr = body_w - wall - tab_len              # ribs stop here; side-cap tabs continue
    for (y0, z0, x1) in [(wall, Z_CEIL - rib_h, xr), (wall, Z_FLOOR, RIB_X1), (RIB_Y0, Z_CEIL - rib_h, RIB_X1)]:
        b = b.union(box(wall - 0.5, x1, y0 - (0.5 if y0 == wall else 0), y0 + (rib_front if y0 == wall else rib), z0 - (0.5 if z0 == Z_FLOOR else 0),
                        z0 + rib_h + (0.5 if z0 != Z_FLOOR else 0)))
    b = b.cut(ballast_slot())
    # module bosses: 45deg diamonds so they print support-free with the body on its left side
    for (x, z) in MOD_SCREW:
        bs = 8.0 if any(xa - 7 < x < xb + 7 for (xa, xb) in FLOPPY_X) else 9.0      # smaller boss next to a floppy slot so it stays out of view
        d = cq.Workplane("XY").box(bs, tray_boss_h + 1, bs).rotate((0, 0, 0), (0, 1, 0), 45)
        b = b.union(d.translate((x, wall + tray_boss_h / 2 - 0.5, z)))
        b = b.cut(cyl((x, wall + tray_boss_h + 0.01, z), (0, -1, 0), insert_d, insert_depth))
    for (xa, xb) in FLOPPY_X:                 # dummy floppy slots: straight through the front wall, black Pi-module plate shows behind
        b = b.cut(box(xa, xb, -1, wall + 1, floppy_z - floppy[1] / 2, floppy_z + floppy[1] / 2))
    # SD-card access slot through the left wall, with a finger/tweezer scoop on the outside
    yc = PI_Y - 1.0
    b = b.cut(box(-1, wall + 1, yc - sd_slot[1] / 2, yc + sd_slot[1] / 2, SD_Z - sd_slot[0] / 2, SD_Z + sd_slot[0] / 2))
    t = 2.0                                   # 45deg funnel on the outside instead of a stepped scoop: prints left-side-down with no supports
    b = b.cut(cq.Workplane("YZ").center(yc, SD_Z).rect(sd_slot[1] + 2 * t, sd_slot[0] + 2 * t).extrude(t, taper=45).translate((-0.01, 0, 0)))
    b = b.cut(box(-1, 0.01, yc - sd_slot[1] / 2 - t, yc + sd_slot[1] / 2 + t, SD_Z - sd_slot[0] / 2 - t, SD_Z + sd_slot[0] / 2 + t))
    # rear rib notched behind the second module screw
    # V notch (45deg sides) so the rib stays one piece and prints without supports with the body on its side
    zb = Z_CEIL - rib_h; nd = 4.5
    vp = [(MOD_NOTCH_X - nd - 1, zb - 1), (MOD_NOTCH_X + nd + 1, zb - 1), (MOD_NOTCH_X, zb + nd)]
    b = b.cut(cq.Workplane("XZ").polyline(vp).close().extrude(-(Y_SEAT + 0.5 - (RIB_Y0 - 1))).translate((0, RIB_Y0 - 1, 0)))
    # ledge along the bottom edge of the side opening: the side cap's inner face presses against it (45deg underside for printing)
    h = 3.0; xi = body_w - wall
    b = b.union(cq.Workplane("XZ").polyline([(xi, Z_FLOOR - 0.5), (xi, Z_FLOOR + h), (xi - h - 0.5, Z_FLOOR - 0.5)]).close().extrude(-(Y_SEAT + 0.5 - (wall - 0.5))).translate((0, wall - 0.5, 0)))
    # top clamp wall: cable passage, bolts, blind pin holes, hidden side-cap screw
    b = b.cut(box(PASS_X0, PASS_X1, PASS_Y0, PASS_Y1, Z_CEIL - 1, 1))
    for (x, y) in BOLT_XY:
        b = b.cut(cyl((x, y, Z_CEIL - 1), (0, 0, 1), bolt_clear, clamp_wall + 2))
    for (x, y) in PIN_XY:
        b = b.cut(cyl((x, y, 0.01), (0, 0, -1), pin_d + pin_clear, pin_engage + 0.5))
    b = b.cut(csk((CAP_TOP_SCREW[0], CAP_TOP_SCREW[1], 0), (0, 0, -1), clamp_wall))
    for zc in HOOK_Z:                         # wedges the side cap hooks under
        b = b.union(body_hook(zc))
    for (x, z) in COVER_SCREW:                # rear-cover inserts in the top rear rib
        if x < RIB_X1:
            b = b.cut(cyl((x, Y_SEAT + 0.01, z), (0, -1, 0), insert_d, insert_depth))
    return b

# ---- side-cap front hooks: the cap hooks onto the front wall, swings shut, and the rear-cover screws lock it.
# No fastener is needed under the fins, so the cap can go on last.
HOOK_Z = [-20.0, -88.0]                   # hook centres (clear of the buck converter and the rear tabs)
HOOK_P = 1.6                              # how far the body's wedge stands off the front wall
HOOK_XT = body_w - wall - 2.0             # flat top of the wedge (toward the cap)
HOOK_LEN = 10.0

def body_hook(zc):
    """Wedge on the inside of the front wall. Flat face toward the cap, 45deg face away from it: prints with the
    body on its left side without supports, and the 45deg face is what the cap's finger catches under."""
    pts = [(HOOK_XT - HOOK_P, wall), (HOOK_XT, wall + HOOK_P), (HOOK_XT, wall - 0.4), (HOOK_XT - HOOK_P, wall - 0.4)]
    return cq.Workplane("XY").polyline(pts).close().extrude(HOOK_LEN).translate((0, 0, zc - HOOK_LEN / 2))

def cap_hook(zc):
    """Arm reaching in from the cap with a 45deg finger that sits under the body's wedge."""
    k = HOOK_XT - HOOK_P - wall - 0.35       # finger face: x = y + k (0.25 mm normal gap to the wedge)
    y0, y1 = wall + clr + 0.1, wall + HOOK_P + 0.3
    xa = HOOK_XT - HOOK_P - 1.2
    L = HOOK_LEN - 0.6
    f = cq.Workplane("XY").polyline([(xa, y0), (y0 + k, y0), (y1 + k, y1), (xa, y1)]).close().extrude(L).translate((0, 0, zc - L / 2))
    return f.union(box(xa, body_w - wall + 0.5, y1 - 0.01, y1 + 2.8, zc - L / 2, zc + L / 2))

def make_side_cap():
    c = clr
    s = box(body_w - wall, body_w, wall + c, depth, Z_OPEN + c, Z_CEIL - c)
    s = s.union(box(body_w - wall, body_w, wall + c, Y_SEAT - c, Z_FLOOR + c, Z_OPEN + c + 0.5))   # steps around the body sill
    s = s.union(box(X_COV1, body_w - wall + 0.5, Y_SEAT - 4, depth, Z_OPEN + c, Z_CEIL - c))        # thickening behind the bevel
    s = s.cut(_bevel_prism(body_w, -1))
    x0 = body_w - wall - tab_len + c
    tabs = [(RIB_Y0, Y_SEAT, Z_CEIL - rib_h, Z_CEIL - c), (RIB_Y0, Y_SEAT, Z_SCR_LOW - rib_h / 2, Z_SCR_LOW + rib_h / 2),
            (wall + c, wall + rib, Z_CEIL - rib_h, Z_CEIL - c)]
    for (y0, y1, z0, z1) in tabs:
        s = s.union(box(x0, body_w - wall + 0.5, y0, y1, z0, z1))
    for zc in HOOK_Z:
        s = s.union(cap_hook(zc))
    for (x, z) in COVER_SCREW:
        if x > RIB_X1:
            s = s.cut(cyl((x, Y_SEAT + 0.01, z), (0, -1, 0), insert_d, insert_depth))
    s = s.cut(cyl((CAP_TOP_SCREW[0], CAP_TOP_SCREW[1], Z_CEIL - c + 0.01), (0, 0, -1), insert_d, insert_depth))
    return s

def make_pi_module():
    """Removable Pi tray and port recess as one part. Prints plate-down; recess walls rise from the plate.
    The Pi's USB/Ethernet cluster shows through a window in the recess LEFT wall; plugs go in sideways."""
    s = box(TRAY_X0, REC_X0 + 1, TRAY_Y0, TRAY_Y0 + tray_t, TRAY_Z[0], TRAY_Z[1])
    s = s.union(box(REC_X0, REC_X1, TRAY_Y0, depth, rec_z[0], rec_z[1]))
    s = s.cut(box(REC_X0 + rec_wall, REC_X1 - rec_wall, TRAY_Y0 + tray_t, depth + 1, rec_z[0] + rec_wall, rec_z[1] - rec_wall))
    s = s.cut(box(REC_X0 - 1, REC_X0 + rec_wall + 1, WIN_Y[0], WIN_Y[1], WIN_Z[0], WIN_Z[1]))            # port window
    # USB-C PD trigger board cradle (PROVISIONAL): pedestal + side rails; receptacle pokes through the wall slot
    bl, bw, bt = trig_board; yb = TRAY_Y0 + tray_t + trig_ped; yp = TRAY_Y0 + tray_t - 0.2
    xe = REC_X0 - 0.3                                           # connector-end board edge, against the recess wall
    xh = xe - trig_hole_end
    for sg in (-1, 1):                                          # two screw posts through the board's own 3 mm holes
        zc = usbc_z + sg * trig_hole_pitch / 2
        s = s.union(cyl((xh, yp, zc), (0, 1, 0), 6.4, yb - yp))
        s = s.union(box(xh, REC_X0 + 0.5, yp, yb, zc - 1.5, zc + 1.5))                         # web to the recess wall
        s = s.cut(cyl((xh, yb + 0.01, zc), (0, -1, 0), 2.2, 7.0))
    s = s.union(box(xe - bl + 0.3, xe - bl + 4.0, yp, yb, usbc_z - 4, usbc_z + 4))             # rest under the wire end
    yc = yb + bt + 1.6                                          # receptacle centre
    s = s.cut(box(REC_X0 - 1, REC_X0 + rec_wall + 1, yb + bt - 0.2, yb + bt + usbc_slot[1], usbc_z - usbc_slot[0] / 2, usbc_z + usbc_slot[0] / 2))
    s = s.cut(box(REC_X0 + 1.0, REC_X0 + rec_wall + 1, yc - 3.75, yc + 3.75, usbc_z - 6.5, usbc_z + 6.5))   # counterbore so the plug's overmold can seat
    s = s.union(box(REC_X1 - 0.3, FLOPPY_X[1][1] + 2.0, TRAY_Y0, TRAY_Y0 + tray_t, floppy_z - 4.0, floppy_z + 4.0))   # black backing behind the end of the right floppy slot
    # buck-converter mount: two pilasters on the outside of the recess wall (print as vertical bars, no supports)
    yc, zc = buck_pi_c
    for sz in (-1, 1):
        z = zc + sz * _bdx / 2
        s = s.union(box(REC_X1 - 0.3, REC_X1 + buck_pi_stand, TRAY_Y0, yc + buck_hole_dy / 2 + 4.0, z - 3.5, z + 3.5))
        for sy in (-1, 1):
            s = s.cut(cyl((REC_X1 + buck_pi_stand + 0.01, yc + sy * buck_hole_dy / 2, z), (-1, 0, 0), 2.5, buck_pi_stand + rec_wall - 0.6))
    s = s.cut(box(pi_x0 + 12, pi_x0 + 52, TRAY_Y0 - 1, TRAY_Y0 + tray_t + 1, pi_z0 + 12, pi_z0 + 44))    # airflow window
    for (hx, hz) in PI_HOLES:
        s = s.union(cyl((pi_x0 + hx, TRAY_Y0 + tray_t - 0.2, pi_z0 + hz), (0, 1, 0), 6.0, pi_standoff + 0.2))
        s = s.cut(cyl((pi_x0 + hx, TRAY_Y0 - 1, pi_z0 + hz), (0, 1, 0), 2.2, tray_t + pi_standoff + 2))
    for (x, z) in MOD_SCREW:
        s = s.cut(cyl((x, TRAY_Y0 - 1, z), (0, 1, 0), bolt_clear, tray_t + 2))
    return s

def make_lower_cover():
    c = clr
    s = box(X_COV0 + c, X_COV1 - c, Y_SEAT, depth, Z_OPEN + c, Z_CEIL - c)
    s = s.cut(box(REC_X0 - c, REC_X1 + c, Y_SEAT - 1, depth + 1, rec_z[0] - c, rec_z[1] + c))   # frames the recess rim
    for (x, z) in COVER_SCREW:
        s = s.cut(csk((x, depth, z), (0, -1, 0)))
    x = 26.0                                   # vent slots behind the Pi / cooler
    while x < 64:
        s = s.cut(box(x, x + 3, Y_SEAT - 1, depth + 1, pi_z0 + 12, pi_z0 + 50)); x += 7
    # bottom hooks: drop behind the sill, then the cover swings shut and is screwed where a driver can reach
    zt = Z_OPEN + c; d = 2.7
    for (xa, xb) in HOOK_X:
        pts = [(Y_SEAT + 0.3, zt + 6), (Y_SEAT + 0.3, zt), (Y_SEAT, zt), (Y_SEAT - d, zt - d), (Y_SEAT - d - 2.0, zt - d), (Y_SEAT - d - 2.0, zt + 6)]
        s = s.union(cq.Workplane("YZ").polyline(pts).close().extrude(xb - xa).translate((xa, 0, 0)))
    return s

def make_fin():
    s = cq.Workplane("XY").box(body_w, depth, fin_t, centered=False)
    s = try_chamfer(s, lambda w: w.edges("|Z"), 2.0)
    return _stack_holes(s, fin_t)

def make_spacer():
    """Rectangular skeleton frame: perimeter wall, solid end blocks around bolt + pin, centre web."""
    i = spacer_inset
    s = box(i, body_w - i, i, depth - i, 0, spacer_t)
    return _stack_holes(s, spacer_t)

def make_fin_unit():
    """One fin with its spacer frame fused on top: prints fin-down, no supports. Stack 4 of these + 1 plain fin."""
    return _fuse_unit()

def _fuse_unit():
    blank = cq.Workplane("XY").box(body_w, depth, fin_t, centered=False)
    blank = try_chamfer(blank, lambda w: w.edges("|Z"), 2.0)
    i = spacer_inset
    blank = blank.union(box(i, body_w - i, i, depth - i, fin_t - 0.01, fin_t + spacer_t))
    return _stack_holes(blank, fin_t + spacer_t)

def _stack_holes(s, t):
    for (x0, x1) in SKEL_X:
        s = s.cut(box(x0, x1, SKEL_Y[0], SKEL_Y[1], -1, t + 1))
    for (x, y) in BOLT_XY:
        s = s.cut(cyl((x, y, -1), (0, 0, 1), bolt_clear, t + 2))
    for (x, y) in PIN_XY:
        s = s.cut(cyl((x, y, -1), (0, 0, 1), pin_d + pin_clear, t + 2))
    return s

def make_front_housing():
    s = hous_slab(0, Y_LCDW)
    s = try_chamfer(s, lambda w: w.faces("<Y").edges(), 1.5)
    ix0, ix1, iz0 = wall, HOUS_W - wall, Z_H0 + clamp_wall
    ledge_y = wall + lcd_pocket_d
    cav = hous_slab(ledge_y, depth + 1, inset=wall).cut(box(-1, HOUS_W + 1, 0, depth + 2, Z_H0 - 1, iz0))
    s = s.cut(cav)                                                                             # main cavity (follows the outline)
    s = s.cut(box(PKT_X0, PKT_X1, wall, ledge_y + 1, PKT_Z0, PKT_Z1))                          # LCD pocket: side walls only
    s = s.cut(rbox(OPN[0], OPN[1], -1, wall + 0.01, OPN[2], OPN[3], bez_r))                    # opening filled by the black bezel
    s = s.cut(_bez_flange(OPN[3], 1, grow=0.3)).cut(_bez_flange(OPN[2], -1, grow=0.3))         # 45deg seats for the bezel's flanges
    lw, lh, ld = logo; lz = (Z_H0 + OPN[2]) / 2                                                # centred between the fins and the black bezel
    s = s.cut(rbox(OPN[0], OPN[0] + lw, -1, ld, lz - lh / 2, lz + lh / 2, logo_r))
    for (x, z) in LCDCOV_SCREW:                                                                # cover-screw columns on the side ledges
        xa, xb = (ix0 - 0.5, PKT_X0) if x < AP_CX else (PKT_X1, ix1 + 0.5)
        s = s.union(box(xa, xb, ledge_y - 0.5, Y_LCDW, z - 4.75, z + 4.75))
        s = s.cut(cyl((x, Y_LCDW + 0.01, z), (0, -1, 0), insert_d_v, insert_depth))
    for (za, zb) in (ZONE_B, ZONE_T):                                                          # reliefs for the panel's side tabs
        s = s.cut(box(PKT_X0 - lcd_tab_out, PKT_X0 + 1, wall, ledge_y + 1, za, zb))
        s = s.cut(box(PKT_X1 - 1, PKT_X1 + lcd_tab_out, wall, ledge_y + 1, za, zb))
    for x in RET_X:
        for z in RET_Z:
            s = s.cut(cyl((x, ledge_y + 0.01, z), (0, -1, 0), insert_d_v, 5.2))
    pm = (PASS_X0 + PASS_X1) / 2
    s = s.cut(box(PASS_X0, pm - 2, PASS_Y0, PASS_Y1, Z_H0 - 1, iz0 + 1))
    s = s.cut(box(pm + 2, PASS_X1, PASS_Y0, PASS_Y1, Z_H0 - 1, iz0 + 1))
    for (x, y) in BOLT_XY:
        s = s.cut(cyl((x, y, Z_H0 - 1), (0, 0, 1), bolt_clear, clamp_wall + 2))
    for (x, y) in PIN_XY:
        s = s.cut(cyl((x, y, Z_H0 - 0.01), (0, 0, 1), pin_d + pin_clear, pin_engage + 0.5))
    return s

def _bez_flange(zedge, sign, grow=0.0):
    """45deg wedge along the top (sign=+1) or bottom (sign=-1) edge of the bezel ring, x across the pocket."""
    f = bez_flange_w + grow
    pts = [(LCD_Y0 - f, zedge), (LCD_Y0 + (0.01 if grow else 0), zedge), (LCD_Y0 + (0.01 if grow else 0), zedge + sign * f)]
    x0, x1 = OPN[0] + bez_r, OPN[1] - bez_r
    return cq.Workplane("YZ").polyline(pts).close().extrude(x1 - x0).translate((x0, 0, 0))

def make_inner_bezel():
    """Black inner bezel. A ring fills the ivory opening flush with the front; 45deg flanges along its top and bottom
    catch behind the ivory, and the LCD sits on its back, so it needs no fasteners. Prints front-face-down, no supports."""
    c = bez_clr
    s = rbox(OPN[0] + c, OPN[1] - c, 0, LCD_Y0, OPN[2] + c, OPN[3] - c, bez_r - c)
    s = s.union(_bez_flange(OPN[3] - c, 1)).union(_bez_flange(OPN[2] + c, -1))
    s = s.cut(box(AP_CX - active_w / 2, AP_CX + active_w / 2, -1, LCD_Y0 + 1, AP_CZ - active_h / 2, AP_CZ + active_h / 2))
    inner = lambda p: p.y < 0.01 and abs(p.x - AP_CX) < active_w / 2 + 0.01 and abs(p.z - AP_CZ) < active_h / 2 + 0.01
    return try_chamfer(s, lambda w: w.edges(PtSel(inner)), 1.5)                                # stepped look toward the screen

def make_lcd_cover():
    """Bevelled rear cap following the housing outline: sits on the wall ends; 3 mm skin inside a perimeter frame."""
    c = clr
    s = hous_slab(Y_LCDW, depth)
    s = try_chamfer(s, lambda w: w.faces(">Y").edges(), rear_bevel)
    pocket = hous_slab(Y_LCDW - 1, Y_SEAT, inset=wall + 3).cut(box(-1, HOUS_W + 1, 0, depth + 1, Z_H0 - 1, Z_H0 + clamp_wall + 3))
    for (x, z) in LCDCOV_SCREW:                                    # keep pads under the screws
        pocket = pocket.cut(box(x - 7, x + 7, Y_LCDW - 2, Y_SEAT + 1, z - 7, z + 7))
    s = s.cut(pocket)
    for (xa, xb, za, zb) in [(wall + c, wall + 2.5, AP_CZ - 30, AP_CZ + 30), (HOUS_W - wall - 2.5, HOUS_W - wall - c, AP_CZ - 30, AP_CZ + 30),
                             (40, 90, Z_H1 - wall - 2.5, Z_H1 - wall - c), (150, 200, Z_H1 - wall - 2.5, Z_H1 - wall - c),
                             (body_w + hous_r + 6, HOUS_W - hous_r - 6, Z_SCR0 + wall + c, Z_SCR0 + wall + 2.5)]:
        s = s.union(box(xa, xb, Y_LCDW - 1.5, Y_LCDW + 0.3, za, zb))                                   # registration bars
    for (x, z) in LCDCOV_SCREW:
        s = s.cut(csk((x, depth, z), (0, -1, 0), lcd_cap_t))
    for (hx, hz) in BUCK_HOLES:                                    # buck converter: two diagonal standoffs
        p = (BUCK_C[0] + hx, Y_SEAT + 0.2, BUCK_C[1] + hz)
        s = s.union(cyl(p, (0, -1, 0), 6.5, buck_standoff + 0.2))
        s = s.cut(cyl((p[0], Y_SEAT + 1.5, p[2]), (0, -1, 0), 2.5, buck_standoff + 1.6))
    x = AP_CX - 56
    while x < AP_CX + 56:
        s = s.cut(box(x, x + 3, Y_LCDW - 1, depth + 1, Z_H1 - 45, Z_H1 - 15)); x += 8
    return s

def make_retainer(x, z):
    """Side clip (4x identical): screws to the ledge, finger reaches down to lcd_clip_h above the pocket floor.
    Bears on the thin side edge of the panel through a pad and traps the side shim beneath it. Prints top-face-down."""
    side = 1 if x < AP_CX else -1
    pk = PKT_X0 if side == 1 else PKT_X1                       # pocket wall this clip sits beside
    y0 = wall + lcd_pocket_d
    xa, xb = sorted((pk - side * (LEDGE_MIN - 0.3), pk + side * 7.5))
    s = box(xa, xb, y0, y0 + 2.5, z - 4, z + 4)
    fa, fb = sorted((pk + side * 0.4, pk + side * 7.5))
    s = s.union(box(fa, fb, LCD_Y0 + lcd_clip_h, y0 + 0.5, z - 4, z + 4))
    return s.cut(cyl((x, y0 - 1, z), (0, 1, 0), bolt_clear, 5))

def make_shim(length, height, n):
    """Loose spacer, thickness n*shim_step, lying flat (thickness up). n notches along one edge identify it."""
    s = cq.Workplane("XY").box(length, height, n * shim_step, centered=False)
    for k in range(n):
        s = s.cut(box(2.0 + 2.0 * k, 3.0 + 2.0 * k, height - 0.7, height + 1, -1, n * shim_step + 1))
    return s

SHIM_SIDE = (24.0, 2.6)       # length, height (fits under the clip finger)
SHIM_BOT = (30.0, 5.5)
def make_shim_set(kind):
    """All thicknesses on one plate for printing: 2 of each (4 of the middle size for the side set)."""
    L, H = SHIM_SIDE if kind == "side" else SHIM_BOT
    out = None; row = 0
    for n in range(1, N_SHIM + 1):
        for c in range(4 if (kind == "side" and n == N_SHIM // 2) else 2):
            p = make_shim(L, H, n).translate((c * (L + 3), row * (H + 3), 0))
            out = p if out is None else out.add(p)
        row += 1
    return out

def _shim_in_place(x0, x1, y0, y1, z0, z1):
    return box(x0, x1, y0, y1, z0, z1)

# visualisation-only envelopes (NOT printed)
def make_lcd_glass():
    w, h, t = lcd_panel; bh, bt, bf = lcd_bottom
    s = box(PANEL_CX - w / 2, PANEL_CX + w / 2, LCD_Y0, LCD_Y0 + t, PANEL_CZ - h / 2, PANEL_CZ + h / 2)
    return s.union(box(PANEL_CX - bf * w / 2, PANEL_CX + bf * w / 2, LCD_Y0, LCD_Y0 + bt, PANEL_CZ - h / 2, PANEL_CZ - h / 2 + bh))

def make_pi_envelope():
    px, pz, y = pi_x0, pi_z0, PI_Y
    s = box(px, px + 85, y, y + 1.6, pz, pz + 56)
    s = s.union(box(px + 66, px + 85 + pi_usb_overhang, y + 1.6, y + 17.6, pz + 2, pz + 54))   # USB/Ethernet cluster
    s = s.union(box(px + 8, px + 62, y + 1.6, y + 11.6, pz + 10, pz + 50))                       # active cooler (PROVISIONAL)
    s = s.union(box(px - 2.3, px + 13, y - 1.5, y, pz + 22.5, pz + 33.5))                        # microSD card
    return s

def make_trigger_envelope():
    bl, bw, bt = trig_board; yb = TRAY_Y0 + tray_t + trig_ped + 0.05; xe = REC_X0 - 0.3
    s = box(xe - bl, xe, yb, yb + bt, usbc_z - bw / 2, usbc_z + bw / 2)
    for sg in (-1, 1):
        s = s.cut(cyl((xe - trig_hole_end, yb - 1, usbc_z + sg * trig_hole_pitch / 2), (0, 1, 0), 3.0, bt + 2))
    s = s.union(box(xe - 7.5, xe + trig_overhang, yb + bt, yb + bt + 3.2, usbc_z - 4.5, usbc_z + 4.5))      # receptacle
    return s.union(box(xe - bl + 1, xe - 12, yb + bt, yb + bt + 4.0, usbc_z - bw / 2 + 1, usbc_z + bw / 2 - 1))   # DIP switch / parts

def make_buck_envelope():
    """On the LCD rear cover, long axis vertical, components facing the LCD."""
    L, W, H = buck_board; y1 = Y_SEAT - buck_standoff
    s = box(BUCK_C[0] - W / 2, BUCK_C[0] + W / 2, y1 - 1.6, y1, BUCK_C[1] - L / 2, BUCK_C[1] + L / 2)
    return s.union(box(BUCK_C[0] - W / 2 + 1, BUCK_C[0] + W / 2 - 1, y1 - 1.6 - H, y1 - 1.6, BUCK_C[1] - L / 2 + 1, BUCK_C[1] + L / 2 - 1))

def make_buck_pi_envelope():
    """Buck converter on the Pi module: board on edge against the recess wall pilasters, parts toward the side cap."""
    L, W, H = buck_board; yc, zc = buck_pi_c; x0 = REC_X1 + buck_pi_stand + 0.05
    s = box(x0, x0 + 1.6, yc - W / 2, yc + W / 2, zc - L / 2, zc + L / 2)
    return s.union(box(x0 + 1.6, x0 + H, yc - W / 2 + 1, yc + W / 2 - 1, zc - L / 2 + 1, zc + L / 2 - 1))

def make_ctl_envelope():
    """LCD controller taped to the back of the panel (builder's choice: keeps the fragile flex off the removable cover).
    Position is nominal: left of the buck converter, above the thick bottom strip. Board 1.6 + 10 mm of parts (PROVISIONAL)."""
    y0 = LCD_Y0 + lcd_panel[2] + 1.0                           # 1 mm foam tape
    z0 = PANEL_CZ - lcd_panel[1] / 2 + lcd_bottom[0] + 8
    x0 = PANEL_CX - ctl_board[0] / 2 - 20
    s = box(x0, x0 + ctl_board[0], y0, y0 + 1.6, z0, z0 + ctl_board[1])
    return s.union(box(x0 + 2, x0 + ctl_board[0] - 2, y0 + 1.6, y0 + 11.6, z0 + 2, z0 + ctl_board[1] - 2))

def make_bolt(x, y):
    z0 = Z_CEIL - washer_t - shcs_head_h
    s = cyl((x, y, z0), (0, 0, 1), shcs_head_d, shcs_head_h)
    return s.union(cyl((x, y, z0 + shcs_head_h - 0.01), (0, 0, 1), 3.0, BOLT_LEN))

def make_pin(x, y):
    return cyl((x, y, -pin_engage), (0, 0, 1), pin_d, PIN_LEN)

# coupons
def make_coupon_holes():
    s = cq.Workplane("XY").box(62, 14, fin_t, centered=False)
    for i, d in enumerate((3.0, 3.1, 3.2, 3.3, 3.4, 3.5)):
        s = s.cut(cyl((7 + i * 9.5, 7, -1), (0, 0, 1), d, fin_t + 2))
    return s

def make_coupon_inserts():
    s = cq.Workplane("XY").box(40, 12, 8, centered=False)
    for i, d in enumerate((3.8, 4.0, 4.2)):
        s = s.cut(cyl((8 + i * 12, 6, 8.01), (0, 0, -1), d, insert_depth))
        s = s.cut(cyl((-1, 6, 4) if i == 0 else (41, 6, 4), (1, 0, 0) if i == 0 else (-1, 0, 0), insert_d, insert_depth + 1)) if i != 1 else s
    return s

def make_coupon_lcd_corner():
    """One corner of the LCD pocket + aperture + ledge, to check panel fit before the 10 h print."""
    h = make_front_housing()
    return h.intersect(box(-1, 45, -1, wall + lcd_pocket_d + 0.01, Z_H0 - 1, Z_H0 + 50))

# ----------------------------------------------------------------------------- assembly table
def rot_world(v):
    x, y, z = v
    return (x, y * math.cos(TAU) + z * math.sin(TAU), -y * math.sin(TAU) + z * math.cos(TAU))

_A_w = rot_world((0, 0, Z_A))
def to_world(wp):
    return wp.rotate((0, 0, 0), (1, 0, 0), -tilt).translate((0, -_A_w[1], -_A_w[2]))

CHARCOAL = (0.12, 0.12, 0.13)   # viz only: spacers print in the same black as the fins
IVORY, BLACK, GLASS, PCB, STEEL = (0.93, 0.89, 0.78), (0.045, 0.045, 0.05), (0.03, 0.035, 0.05), (0.05, 0.32, 0.16), (0.6, 0.6, 0.62)
# print orientations: (axis, angle) applied to the body-frame part, then dropped to Z=0
ORI = dict(tiltflat=((1, 0, 0), -tilt), front=((1, 0, 0), 90), rear=((1, 0, 0), -90), flat=None, left=((0, 1, 0), -90), right=((0, 1, 0), 90))

def build():
    """name -> dict(shape(body frame), color, printed, group(print file), ori, explode segments)"""
    EX = 140.0
    parts = {}
    def add(name, shape, color, group=None, ori=None, ex=()):
        parts[name] = dict(shape=shape, color=color, group=group, ori=ori, ex=list(ex))
    add("lower_body", make_lower_body(), IVORY, "lower_body", "left")
    back = lambda d: (0, d * math.cos(TAU), d * math.sin(TAU))   # straight back along the desk
    add("viz_ballast_plate", make_ballast(), STEEL, None, None, [(back(150), .45, .80)])
    add("ballast_plug", make_ballast_plug(), BLACK, "ballast_plug", "tiltflat", [(back(185), .55, .90)])
    add("side_cap", make_side_cap(), IVORY, "side_cap", "right", [((75, 0, 0), .10, .45)])
    mv = ((0, 110, 0), 0, .35)
    add("pi_module", make_pi_module(), BLACK, "pi_module", "front", [mv])
    add("viz_pi", make_pi_envelope(), PCB, None, None, [mv])
    add("viz_usbc_trigger", make_trigger_envelope(), PCB, None, None, [mv])
    add("viz_buck_converter_pi", make_buck_pi_envelope(), PCB, None, None, [mv])
    add("lower_rear_cover", make_lower_cover(), IVORY, "lower_rear_cover", "rear", [((0, 200, 0), .60, 1.0)])
    for i, (x, y) in enumerate(BOLT_XY):
        add(f"hw_bolt_{i+1}", make_bolt(x, y), STEEL)
    for i, (x, y) in enumerate(PIN_XY):
        add(f"hw_pin_{i+1}", make_pin(x, y), STEEL)
    unit, fin = make_fin_unit(), make_fin()
    for i in range(n_fins - 1):
        add(f"fin_unit_{i+1}", unit.translate((0, 0, i * (fin_t + spacer_t))), BLACK, "fin_spacer_unit", "flat", [((0, 0, 20 + 26 * i), .30, .75)])
    add("fin_top", fin.translate((0, 0, (n_fins - 1) * (fin_t + spacer_t))), BLACK, "fin_top", "flat", [((0, 0, 20 + 26 * (n_fins - 1)), .30, .75)])
    up = ((0, 0, EX), .30, .75)
    add("lcd_front_housing", make_front_housing(), IVORY, "lcd_front_housing", "front", [up])
    add("lcd_inner_bezel", make_inner_bezel(), BLACK, "lcd_inner_bezel", "front", [up, ((0, 45, 0), .05, .38)])
    add("viz_lcd_glass", make_lcd_glass(), GLASS, None, None, [up, ((0, 70, 0), 0, .35)])
    k = 0
    for x in RET_X:
        for z in RET_Z:
            k += 1
            add(f"lcd_retainer_{k}", make_retainer(x, z), BLACK, "lcd_retainer", "rear", [up, ((0, 105, 0), .22, .50)])
    w_, h_, _t = lcd_panel; k = 0
    for z in RET_Z:                                            # side shims, trapped under the clip fingers (nominal = middle size)
        for (xa, xb) in ((PKT_X0, PANEL_CX - w_ / 2), (PANEL_CX + w_ / 2, PKT_X1)):
            k += 1
            add(f"lcd_shim_side_{k}", _shim_in_place(xa, xb, LCD_Y0, LCD_Y0 + SHIM_SIDE[1], z - SHIM_SIDE[0] / 2, z + SHIM_SIDE[0] / 2), BLACK, None, None, [up, ((0, 85, 0), .12, .42)])
    add("lcd_rear_cover", make_lcd_cover(), IVORY, "lcd_rear_cover", "rear", [up, ((0, 190, 0), .60, 1.0)])
    add("viz_lcd_controller", make_ctl_envelope(), PCB, None, None, [up, ((0, 70, 0), 0, .35)])
    add("viz_buck_converter", make_buck_envelope(), PCB, None, None, [up, ((0, 190, 0), .60, 1.0)])
    return parts

if __name__ == "__main__":
    import export_all
    export_all.main()
