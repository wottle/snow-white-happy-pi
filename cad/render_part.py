#!/usr/bin/env python3
"""Render one print STL on its own: render_part.py in.stl out.png"""
import sys, vtk
r = vtk.vtkSTLReader(); r.SetFileName(sys.argv[1])
n = vtk.vtkPolyDataNormals(); n.SetInputConnection(r.GetOutputPort()); n.SetFeatureAngle(35); n.SplittingOn()
m = vtk.vtkPolyDataMapper(); m.SetInputConnection(n.GetOutputPort())
a = vtk.vtkActor(); a.SetMapper(m); p = a.GetProperty(); p.SetColor(0.16, 0.16, 0.17); p.SetAmbient(0.35); p.SetDiffuse(0.9); p.SetSpecular(0.3); p.SetSpecularPower(20)
ren = vtk.vtkRenderer(); ren.SetBackground(0.87, 0.875, 0.885); ren.AddActor(a); ren.UseFXAAOn()
win = vtk.vtkRenderWindow(); win.SetOffScreenRendering(1); win.SetMultiSamples(0); win.AddRenderer(ren); win.SetSize(1920, 1080)
c = ren.GetActiveCamera(); c.SetFocalPoint(85, 18, 2); c.SetPosition(85 - 150, 18 - 260, 190); c.SetViewUp(0, 0, 1); c.SetViewAngle(28); ren.ResetCameraClippingRange()
win.Render(); f = vtk.vtkWindowToImageFilter(); f.SetInput(win); f.SetInputBufferTypeToRGB(); f.ReadFrontBufferOff(); f.Update()
w = vtk.vtkPNGWriter(); w.SetFileName(sys.argv[2]); w.SetInputConnection(f.GetOutputPort()); w.Write()
