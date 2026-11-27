# Snow White Happy Pi — verification status and known issues

## What has been done

- **CAD checks (automatic, 62 of them, in `cad/export_all.py`).** Solids are valid, parts don't overlap, bolt and pin holes line up, bezel and aperture dimensions, STLs are watertight and fit a 250 mm bed, and so on. The output is `validation_report.txt`. These are geometry and arithmetic checks only. They are not a slicer run and not a physical test.
- **Completed Pi 5 build.** I printed, assembled and ran the computer. The build informed the heat-set insert pilot sizes (4.0 mm for holes that print sideways, 4.2 mm for vertical), 3.3 mm pin holes, LCD pocket clearances, shim sizes and ballast layouts. Individual revision checks are listed below.
- **Ballast plug stops (v0.9c) have been printed and work.**
- **The square badge recess (v0.9e) is CAD-checked only,** against the badge's mesh. A 0.19 mm clearance per side may need adjusting for your printer (`logo` in `cad/slimcase.py`).
- **The side-cap hooks and ledge (v0.9d) have been printed and tested** on my build (reported 2026-11-26). The clearance parameters are at the top of `cad/slimcase.py` if your printer needs different ones.

## Not checked, or still open

- **250 mm bed.** The 250 × 250 × 250 mm fit is checked on the part sizes in CAD (largest footprint 232.6 × 197.4 mm), and the supplied plate layouts fit within 233 × 213 mm. It has not been tested on a 250 mm printer; the project file is set up for a 256 × 256 mm Bambu Lab A1, and a brim wider than 8 mm will not fit on the two biggest parts.

- **Stability.** Tip angles were calculated for a 152 × 120 × 4.76 mm steel plate (about 680 g). Both two-bar layouts were tried in an empty case. The endwise pair weighs about 230 g with 120 mm bars. The preferred crosswise layout puts the ballast near the rear opening. Tip angles for the two-bar layouts are still unknown. Forward tipping is the weak direction.
- **Fit depends on your panel.** The LCD outline and margins were measured on one iPad 1 panel with a tape measure (about ±0.8 mm). Tab positions and the thick strip along the bottom edge come from a description and a few photos. The side shims (0.4 mm steps) exist to absorb this, but if your panel differs you may need to change `lcd_panel`, `lcd_margin` or `lcd_adj`.
- **LCD margins.** Left and right margins were swapped together with top and bottom on the assumption the panel was just upside down. If a different panel turns out to need only top and bottom swapped, swap `lcd_margin` left/right.
- **No stop above or below the LCD.** Its height is held by clip pressure and tape on the panel.
- **Thin walls and slivers.** The side ledges of the display housing are 6.5 mm wide, leaving about 1.1–1.2 mm of plastic between an insert and the panel pocket. The ballast slot skins are about 2.4 mm over a 153 × 128 mm span.
- **Hooks and clips.** Engagement force and flex are still undocumented for the lower rear cover and side-cap hooks.
- **Fin skeleton.** No stress analysis. It carries a housing of roughly 0.5 kg in compression, which is light for it, but its stiffness against a sideways knock on the overhanging display is unknown.
- **Thermal.** The vents are openings only. There has been no thermal analysis, and the fins are decorative, not a heatsink. Pi 5 users should consider a cooler; the BOM notes 10 mm of headroom, not checked against a specific part.
- **Cables.** There are about 32 mm between the Pi's HDMI edge and the top of the body, and 51 mm of internal width in the port recess. Bulky or stiff cables may not fit. A micro-HDMI plug in the port nearest the USB end comes within 0.3 mm of the trigger board's wire end in X (the board is 6 mm higher).
- **Pi variants.** Same mounting holes for the Pi 4 and 5, but a particular cooler's height and the real overhang of the USB and Ethernet ports versus the recess wall are unchecked.
- **Sound and power controls.** The current build has no built-in sound, external power switch or case-mounted shutdown button. I use an optional [inline USB-C power switch](BOM.md#3-electronics) after shutting down the Pi. I may add built-in sound and a power switch in a future revision.
- **Electronics are not part of the design.** The 12 V trigger board, the dual-output 5 V supply and the HDMI controller are whatever you buy; check each one's voltage and current ratings before wiring. The controller's mounting is by double-sided tape, so its hole pattern is not modelled.
- **Buck-converter bars.** The pi module and display rear cover still carry mounts for a small buck converter (43 × 21 mm, holes 35 mm apart on a diagonal; the second hole pair is assumed). They are unused in the documented build.
- **The animation** shows an illustrative order of assembly, not a verified sequence. `blender_scene.py` has never been run.
- **Panel fit and controller.** My build uses an iPad 3/4 LCD (2048 × 1536, driven at 1024 × 768). Older iPad 1/2 LCDs also work. The CAD dimensions come from an iPad 1 panel. The [BOM](BOM.md#3-electronics) links to the LCD and controller kit I used. The shim sizes for my build are still undocumented.
- **LisaEm smoothness.** LisaEm works on my Pi 5, but it still feels less smooth than I'd like. I plan to work on the software side soon. See the [software notes](SOFTWARE.md).
- **Software.** Display mode, emulator settings and performance findings from my Pi 5 build are in `SOFTWARE.md`. Setting up a Pi from scratch (OS, the emulators, the kiosk launcher) is automated by the separate [`lisa-mini-pi`](https://github.com/wottle/lisa-mini-pi) project. I have run that from blank cards on two Pi 4 boards on the bench, and brought my Pi 5 build up to the same LisaEm and launcher, but I have not run it on a Pi 4 inside this case. Not tested: sustained load or temperature with the case closed, the 5 V supply under heavy load, and a Pi 4 in this case.

## Measurements that would still help

1. A second iPad 1 panel measured the same way, to see how much panels vary.
2. The lit-pixel margins with the screen on (the current numbers are to the edge of the black border).
3. Thickness and height of the thicker bottom strip on the panel, and the position of the top tab (the strip height of 20 mm is a guess).
4. Clearance to a real Pi 5 cooler.
