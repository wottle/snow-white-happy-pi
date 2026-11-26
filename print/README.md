# Print project

[`SnowWhiteConcept.3mf`](SnowWhiteConcept.3mf) is a four-plate Bambu Studio project for a **Bambu Lab A1 (256 × 256 mm bed, 0.4 mm nozzle)**. It opens in Bambu Studio 02.07. Use the [individual STLs](../stl) for other slicers and the [shim sets](../stl) for the LCD fit. The widest plate layout is 233 × 213 mm before brims and any printer-specific keep-out areas.

| Plate | Name | Parts | Footprint (mm) |
|---|---|---|---|
| 1 | Lower Body and LCD Front | `lower_body` (on its side, standing inside the display housing's opening), `lcd_front_housing`, `side_cap`, `lower_rear_cover`, 4 × `lcd_retainer` | 233 × 197 |
| 2 | LCD Rear Panel and Ballast Plug | `lcd_rear_cover`, `ballast_plug` | 233 × 213 |
| 3 | Fins | 4 × `fin_spacer_unit`, `fin_top` | 170 × 188 |
| 4 | LCD Bezel and Pi Module | `lcd_inner_bezel`, `pi_module` | 208 × 163 |

The parts on plate 1 do not touch (checked with exact boolean intersections), and the lower body prints by layer inside the housing's opening, so use the project's *print by layer* sequence, not *by object*.

## Settings in the project

- Profile `0.20mm Standard @BBL A1`, 0.4 mm nozzle, textured PEI plate, 220 °C nozzle, 65 °C bed.
- 2 wall loops, 5 top and 3 bottom layers, 15 % grid infill, **no supports**, auto brim (5 mm), seam aligned, no ironing, elephant-foot compensation 0.075 mm.
- Two PLA filaments: slot 1 the light colour (Polar Filament Retro Platinum in the build; the preset is named PolyTerra), slot 2 black. Black: the fin units, `fin_top`, `lcd_inner_bezel`, `pi_module`. Everything else, including the retainers and ballast plug, uses the light colour.
- Not in the project: the LCD shims (print at 0.2 mm layers, thickness in 0.4 mm steps) and the fit-test coupons. They are in `stl/`.

## About this file

- It holds *copies* of the meshes. It was checked part by part against the STLs in `stl/` (matching volumes, every part sitting on Z=0, no overlaps). Two parts, `lcd_front_housing` and `ballast_plug`, were refreshed to the current version; if you change the CAD, re-import the changed parts.
- Its plate thumbnails were rendered before that refresh, so the badge recess and plug may look slightly different from the current models.
- Bambu account details were removed from the file; printer-specific G-code and machine settings from the A1 profile remain.
