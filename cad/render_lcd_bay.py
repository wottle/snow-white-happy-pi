#!/usr/bin/env python3
"""Rear view into the display housing with the rear cover removed: pocket, tab reliefs, panel placeholder, side clips."""
import json, sys, vtk
man = {p["name"]: p for p in json.load(open("out/viz/manifest.json"))}
show = ["lcd_front_housing", "viz_lcd_glass"] + [f"lcd_retainer_{k}" for k in range(1, 5)] + [f"lcd_shim_side_{k}" for k in range(1, 5)] + ["lcd_inner_bezel", "lcd_rear_cover_none"][:1]
if len(sys.argv) > 2 and sys.argv[2] == "nopanel": show = [n for n in show if n in ("lcd_front_housing", "lcd_inner_bezel")]
ren = vtk.vtkRenderer(); ren.SetBackground(0.87, 0.875, 0.885); ren.UseFXAAOn()
for nme in show:
    r = vtk.vtkSTLReader(); r.SetFileName(f"out/viz/{nme}.stl")
    n = vtk.vtkPolyDataNormals(); n.SetInputConnection(r.GetOutputPort()); n.SetFeatureAngle(35); n.SplittingOn()
    m = vtk.vtkPolyDataMapper(); m.SetInputConnection(n.GetOutputPort()); a = vtk.vtkActor(); a.SetMapper(m)
    c = man[nme]["color"]; c = (0.75, 0.3, 0.1) if nme.startswith("lcd_retainer") else (0.1, 0.55, 0.75) if nme.startswith("lcd_shim") else (0.2, 0.2, 0.22) if nme == "lcd_inner_bezel" else ((0.25, 0.3, 0.38) if nme.startswith("viz") else c)
    p = a.GetProperty(); p.SetColor(*c); p.SetAmbient(0.3); p.SetDiffuse(0.85); ren.AddActor(a)
win = vtk.vtkRenderWindow(); win.SetOffScreenRendering(1); win.SetMultiSamples(0); win.AddRenderer(ren); win.SetSize(1920, 1440)
cam = ren.GetActiveCamera(); cam.SetFocalPoint(116, 55, 245); cam.SetPosition(116 - 120, 55 + 540, 245 + 150); cam.SetViewUp(0, 0, 1); cam.SetViewAngle(28); ren.ResetCameraClippingRange()
win.Render(); f = vtk.vtkWindowToImageFilter(); f.SetInput(win); f.SetInputBufferTypeToRGB(); f.ReadFrontBufferOff(); f.Update()
w = vtk.vtkPNGWriter(); w.SetFileName(sys.argv[1]); w.SetInputConnection(f.GetOutputPort()); w.Write()
