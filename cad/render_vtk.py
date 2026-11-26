#!/usr/bin/env python3
"""Render stills and the exploded-assembly animation from the SAME tessellated CAD (out/viz/*.stl).
Usage: render_vtk.py stills | anim [W H FPS]     (VTK off-screen, EGL/OSMesa software GL is fine)"""
import sys, os, json, math, subprocess
import vtk
OUT = os.environ.get("SLIMCASE_OUT", "out"); VIZ = f"{OUT}/viz"
man = json.load(open(f"{VIZ}/manifest.json"))
C = (116, 60, 165)   # look-at centre of assembled model (world mm)

def ease(u):
    u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)

def offset(part, s):
    o = [0.0, 0.0, 0.0]
    for seg in part["explode"]:
        k = 1 - ease((s - seg["t0"]) / (seg["t1"] - seg["t0"]))
        for i in range(3): o[i] += seg["vec"][i] * k
    return o

PLATINUM = (0.84, 0.84, 0.82)       # Polar Filament Retro Platinum, approximately
LIGHT_NAMES = ("ballast_plug", "lcd_retainer")
HIDE = ("viz_buck_converter", "viz_buck_converter_pi")   # unused in the documented build

def scene(w, h, caption=None):
    ren = vtk.vtkRenderer(); ren.SetBackground(0.87, 0.875, 0.885)
    actors = {}
    for p in man:
        if p["name"] in HIDE: continue
        if tuple(p["color"]) == (0.93, 0.89, 0.78) or p["name"].startswith(LIGHT_NAMES): p = dict(p, color=list(PLATINUM))
        r = vtk.vtkSTLReader(); r.SetFileName(f"{VIZ}/{p['file']}")
        n = vtk.vtkPolyDataNormals(); n.SetInputConnection(r.GetOutputPort()); n.SetFeatureAngle(35); n.SplittingOn()
        m = vtk.vtkPolyDataMapper(); m.SetInputConnection(n.GetOutputPort())
        a = vtk.vtkActor(); a.SetMapper(m); pr = a.GetProperty(); pr.SetColor(*p["color"])
        dark = sum(p["color"]) < 0.5
        pr.SetAmbient(0.22 if not dark else 0.35); pr.SetDiffuse(0.85); pr.SetSpecular(0.25 if dark else 0.08); pr.SetSpecularPower(25)
        ren.AddActor(a); actors[p["name"]] = a
    pl = vtk.vtkPlaneSource(); pl.SetOrigin(-30000, -30000, -0.3); pl.SetPoint1(30000, -30000, -0.3); pl.SetPoint2(-30000, 30000, -0.3)
    pm = vtk.vtkPolyDataMapper(); pm.SetInputConnection(pl.GetOutputPort()); fa = vtk.vtkActor(); fa.SetMapper(pm)
    fa.GetProperty().SetColor(0.87, 0.875, 0.885); fa.GetProperty().LightingOff(); ren.AddActor(fa)
    ren.RemoveAllLights(); ren.AutomaticLightCreationOff()
    for pos, inten in (((-0.5, -1.0, 0.9), 0.70), ((1.0, -0.45, 0.5), 0.45), ((-0.6, 1.0, 0.7), 0.50), ((1.0, 0.6, 0.3), 0.25), ((0, 0, 1), 0.12)):
        L = vtk.vtkLight(); L.SetLightTypeToSceneLight(); L.SetPositional(False)
        L.SetPosition(*[C[i] + 1000 * pos[i] for i in range(3)]); L.SetFocalPoint(*C); L.SetIntensity(inten); ren.AddLight(L)
    ren.UseSSAOOn(); ren.SetSSAORadius(22); ren.SetSSAOBias(0.6); ren.SetSSAOKernelSize(64); ren.SSAOBlurOn()
    ren.UseFXAAOn()
    win = vtk.vtkRenderWindow(); win.SetOffScreenRendering(1); win.SetMultiSamples(0); win.AddRenderer(ren); win.SetSize(w, h)
    if caption:
        t = vtk.vtkTextActor(); t.SetInput(caption); tp = t.GetTextProperty(); tp.SetFontSize(max(12, h // 48)); tp.SetColor(0.25, 0.25, 0.27)
        t.SetDisplayPosition(int(w * 0.02), int(h * 0.025)); ren.AddActor2D(t)
    return ren, win, actors, fa

def cam(ren, direction, dist=None, ortho=None, focal=C, up=(0, 0, 1), angle=28):
    c = ren.GetActiveCamera(); c.SetFocalPoint(*focal)
    d = math.sqrt(sum(k * k for k in direction)); u = [k / d for k in direction]
    D = dist or 1500
    c.SetPosition(*[focal[i] + u[i] * D for i in range(3)]); c.SetViewUp(*up)
    if ortho: c.ParallelProjectionOn(); c.SetParallelScale(ortho)
    else: c.ParallelProjectionOff(); c.SetViewAngle(angle)
    c.SetClippingRange(50, 90000)

def shot(win, path):
    win.Render(); f = vtk.vtkWindowToImageFilter(); f.SetInput(win); f.SetInputBufferTypeToRGB(); f.ReadFrontBufferOff(); f.Update()
    w = vtk.vtkPNGWriter(); w.SetFileName(path); w.SetInputConnection(f.GetOutputPort()); w.Write()

def set_state(actors, s):
    for p in man:
        if p["name"] in actors: actors[p["name"]].SetPosition(*offset(p, s))

NOTE = "Rendered from the CAD tessellation. Dark LCD glass, PCBs and steel hardware are visualisation placeholders."
def stills():
    os.makedirs(f"{OUT}/renders", exist_ok=True)
    ren, win, A, floor = scene(1920, 1440, NOTE); set_state(A, 1.0)
    floor.VisibilityOff(); ren.UseSSAOOff()
    cam(ren, (0, -1, 0), ortho=205, focal=(116, 60, 172)); shot(win, f"{OUT}/renders/01_front_ortho.png")
    cam(ren, (1, 0, 0), ortho=205, focal=(116, 75, 172)); shot(win, f"{OUT}/renders/02_side_ortho_right.png")
    floor.VisibilityOn(); ren.UseSSAOOn()
    cam(ren, (0.75, -1, 0.42), dist=1050); shot(win, f"{OUT}/renders/03_front_three_quarter.png")
    cam(ren, (0.8, 1, 0.42), dist=1050, focal=(116, 75, 160)); shot(win, f"{OUT}/renders/04_rear_three_quarter.png")
    cam(ren, (0.75, 1, 0.35), dist=430, focal=(105, 70, 62)); shot(win, f"{OUT}/renders/06_rear_port_recess_closeup.png")
    cam(ren, (-1, 0.25, 0.2), dist=520, focal=(0, 40, 60)); shot(win, f"{OUT}/renders/07_left_side_sd_slot.png")
    cam(ren, (-0.55, 1, 0.5), dist=520, focal=(85, 95, 40)); shot(win, f"{OUT}/renders/08_rear_foot_ballast_slot.png")
    set_state(A, 0.0)
    cam(ren, *EXCAM[0], **EXCAM[1]); shot(win, f"{OUT}/renders/05_exploded.png")

EXCAM = (((1.0, -1, 0.42),), dict(dist=1450, focal=(130, 120, 205)))

def lerp(a, b, u): return [a[i] + (b[i] - a[i]) * u for i in range(len(a))]

def anim(w=1920, h=1080, fps=24, hold0=1.5, move=7.0, hold1=3.5):
    """Landscape frame: start on the exploded stack seen from the rear, zoom in as it assembles, and swing round
    to the front 3/4 view once most parts are home, so the finished front is revealed at the end."""
    fd = f"{OUT}/frames"; os.makedirs(fd, exist_ok=True)
    ren, win, A, floor = scene(w, h, "Illustrative assembly order (not a mechanically verified sequence). " + NOTE)
    EXD, EXF = 1330.0, (130.0, 120.0, 200.0)          # exploded framing
    ASD, ASF = 980.0, (116.0, 62.0, 168.0)            # assembled framing
    AZ_REAR, AZ_FRONT = math.radians(141), math.radians(29)
    def view(az, d, f, el=0.42):
        cam(ren, (math.sin(az), -math.cos(az), el), dist=d, focal=tuple(f))
    n0, n1, n2 = round(hold0 * fps), round(move * fps), round(hold1 * fps)
    k = 0
    def emit():
        nonlocal k
        pth = f"{fd}/f{k:04d}.png"
        if not os.path.exists(pth): shot(win, pth)
        k += 1
    for _ in range(n0): set_state(A, 0.0); view(AZ_REAR, EXD, EXF); emit()
    for i in range(1, n1 + 1):
        s = i / n1; u = ease(s)
        ua = ease((s - 0.45) / 0.50)                    # the swing to the front starts once most parts are together
        set_state(A, s); view(AZ_REAR + (AZ_FRONT - AZ_REAR) * ua, EXD + (ASD - EXD) * u, lerp(EXF, ASF, u)); emit()
        if i % 24 == 0: print("frame", k, flush=True)
    set_state(A, 1.0)
    for i in range(1, n2 + 1):                          # slow settle on the front view
        view(AZ_FRONT - math.radians(6) * ease(i / n2), ASD, ASF); emit()
    print("frames:", k, "duration", k / fps)

if __name__ == "__main__":
    if sys.argv[1] == "stills": stills()
    else: anim(*[int(v) for v in sys.argv[2:5]])
