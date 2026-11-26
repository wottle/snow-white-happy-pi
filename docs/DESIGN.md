# Snow White Happy Pi — design notes

## Coordinate system
Design (body) frame, un-tilted: **+X = viewer's right** facing the screen, **+Y = depth** (front face Y=0, rear Y=36), **+Z = up**; Z=0 is the top of the lower body. Left edges of housing, fins and body are all at X=0; the display overhangs to +X by 62.6.
World frame (assembly STEP, renders): body frame rotated 7° back about X, desk at Z=0.

## What was checked (CAD/maths only — see `validation_report.txt`, 62 checks pass)
Fin/spacer count and 18 mm stack; 18 mm bezel on all four sides probed on the solid; 4:3 aperture; +X overhang 62.6 with aligned left edges; 36 mm depth throughout; flat desk-plane face under the foot at 7°; gauge-rod check through every bolt/pin hole; pairwise boolean interference of all 32 bodies incl. provisional envelopes; Pi port cluster inside the recess window; SD card in line with its slot; every printed part one valid solid, watertight STL on Z=0 inside the bed; bolt length from grip; estimated tip angles.

Stability estimate (assumed masses: LCD 200 g, Pi+cooler 75 g, controller 40 g, cables 90 g, plate 683 g, PLA at 85 % / lower body 45 %): total ≈ 1.77 kg; tip angle ≈ 17° forward, 43° back, 43° left, 38° right. **Without the plate the forward angle is only about 5°** — the slim body puts the weight close to the front edge, so the ballast is no longer optional.
