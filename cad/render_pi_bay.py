#!/usr/bin/env python3
"""Rear view of the Pi module with the Pi, USB-C trigger board and buck-converter placeholders (covers and body hidden)."""
import json, sys, vtk
man = {p["name"]: p for p in json.load(open("out/viz/manifest.json"))}
col = {"pi_module": (0.2, 0.2, 0.22), "viz_pi": (0.05, 0.4, 0.2), "viz_usbc_trigger": (0.8, 0.35, 0.1), "viz_buck_converter_pi": (0.15, 0.4, 0.75)}
ren = vtk.vtkRenderer(); ren.SetBackground(0.87, 0.875, 0.885); ren.UseFXAAOn()
for nme, c in col.items():
    r = vtk.vtkSTLReader(); r.SetFileName(f"out/viz/{nme}.stl")
    n = vtk.vtkPolyDataNormals(); n.SetInputConnection(r.GetOutputPort()); n.SetFeatureAngle(35); n.SplittingOn()
    m = vtk.vtkPolyDataMapper(); m.SetInputConnection(n.GetOutputPort()); a = vtk.vtkActor(); a.SetMapper(m)
    p = a.GetProperty(); p.SetColor(*c); p.SetAmbient(0.35); p.SetDiffuse(0.85); ren.AddActor(a)
win = vtk.vtkRenderWindow(); win.SetOffScreenRendering(1); win.SetMultiSamples(0); win.AddRenderer(ren); win.SetSize(1920, 1440)
ren.ResetCamera(); cam = ren.GetActiveCamera(); f = cam.GetFocalPoint()
cam.SetPosition(f[0] - 60, f[1] + 330, f[2] + 190); cam.SetViewUp(0, 0, 1); cam.SetViewAngle(28); ren.ResetCameraClippingRange()
win.Render(); w2 = vtk.vtkWindowToImageFilter(); w2.SetInput(win); w2.SetInputBufferTypeToRGB(); w2.ReadFrontBufferOff(); w2.Update()
w = vtk.vtkPNGWriter(); w.SetFileName(sys.argv[1]); w.SetInputConnection(w2.GetOutputPort()); w.Write()
