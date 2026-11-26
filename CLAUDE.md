# CLAUDE.md — Snow White Happy Pi (working name: SlimCase)

Guidance for Claude (or any contributor) working in this repo. Read this first; the detail lives in `docs/`.

## What this is

A thin, retro-styled desktop computer for FDM printing: an iPad 1 9.7" 4:3 LCD plus a Raspberry Pi 4/5. Light-coloured housing overhanging to the viewer's **right**, a stack of black fins (5 fins, 4 spacers, 18 mm tall) between the display housing and the lower body, a lower body that curves into a thin rear foot, 7° backward tilt, equal 18 mm bezel on all four sides, 36 mm deep. Inspired by a frog design concept from Apple's Snow White era (believed to be one of the "Happy" designs; the author hedges on which). The electronics are modern; the design effort is printability: **no supports by design**, every part fits a 250 × 250 mm bed (`BED` in `cad/export_all.py`; the largest footprint is the display housing and rear cover at 233 × 197 mm).

Everything is generated from one parametric CadQuery script. The STL, STEP, renders and animation in the repo are build outputs that have been copied in.

## Status — be honest about it

- An earlier revision has been printed, assembled and run with a Pi 5. The ballast plug stops (v0.9c) have been printed and work. The badge recess (v0.9e) and the older-slot badge work. **The side-cap hooks and ledge (v0.9d) are CAD-checked only.**
- The 62 checks in `cad/export_all.py` are geometry and arithmetic: valid solids, pairwise boolean interference, hole alignment, STL watertightness, bed fit, tip angles. They are not a slicer run and not a physical test.
- **Never describe the design as "print-ready" or "validated" without saying CAD-checked vs physically tested.** Keep `docs/KNOWN_ISSUES.md` accurate when anything gets tested.
- `cad/blender_scene.py` has never been run. The animation shows an illustrative order, not a verified sequence.

## Layout

| Path | What |
|---|---|
| `cad/slimcase.py` | All parameters (dict `P`, at the top) and every part builder; `build()` returns the part table |
| `cad/export_all.py` | Builds everything, runs the checks, writes STEP/STL/viz meshes/coupons and `validation_report.txt` into `out/` (override with `SLIMCASE_OUT`) |
| `cad/render_vtk.py` | Stills (`stills`) and animation frames (`anim 1920 1080 24`, into `out/frames/`); `render_part.py <stl> <png>`, `render_pi_bay.py <png>`, `render_lcd_bay.py <png>` |
| `stl/`, `stl/coupons/`, `step/`, `step/parts/`, `media/` | Committed copies of the build outputs |
| `print/SnowWhiteConcept.3mf` | Bambu Studio project: four plates, Bambu Lab A1 profile. **It holds copies of the STLs**, so when a part changes it must be refreshed (re-import that part and keep its plate position) |
| `docs/` | `BOM.md`, `ASSEMBLY.md`, `KNOWN_ISSUES.md`, `DESIGN.md`, `CHANGELOG.md`, `validation_report.txt` |

Run everything from the repo root (the scripts use relative `out/...` paths): `pip install -r cad/requirements.txt`, then `python cad/export_all.py`. Add `manifold3d`, `shapely` and `rtree` if you do mesh booleans or slicing with trimesh (they are not needed for the main build).

**Output sync after a change** (nothing is automatic): `out/stl_print/*` → `stl/`; `out/stl_coupons/*` → `stl/coupons/`; `out/step_parts/*` → `step/parts/`; `out/slimcase_assembly.step` → `step/`; `out/renders/*` and the two mp4s → `media/`; the README's inline animation is `media/slimcase_assembly.gif` (`ffmpeg -i <1080p mp4> -vf "fps=12,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=4" slimcase_assembly.gif`); `out/docs/validation_report.txt` → `docs/`. A rebuild reproduces the committed STLs byte for byte, so a diff in `stl/` means the geometry changed. Encode the animation with `ffmpeg -framerate 24 -i out/frames/f%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart` (1080p) and a 960×540 copy.

## Conventions

- **Body frame (un-tilted):** +X = viewer's right facing the screen, +Y = depth (front Y=0, rear Y=36), +Z = up; **Z=0 is the top of the lower body** (bottom of the fin stack); everything below is negative Z. Left edges of housing, fins and body are at X=0; the display overhangs +X by 62.6 mm. Screws and features are quoted as (X, Z) in this frame.
- **World frame** (assembly STEP, renders): body frame rotated 7° about X, desk at Z=0. Use `to_world` / `rot_world`; `_desk_pt` and `_desk_slab` build things in desk coordinates (the foot, ballast slot).
- **Print orientation** is per part in dict `ORI` (`front`, `rear`, `left`, `right`, `flat`, `tiltflat`); STLs sit on Z=0 and the file name carries the quantity (`__x4`).
- Units are mm. Useful helpers: `box`, `rbox` (rounds the four Y-parallel edges), `cyl`, `hous_slab`, `profile_wp`, `rounded_profile`, `PtSel` (point selector).
- Add a `chk(...)` in `export_all.py` for every new feature, with the numbers in its message, then rebuild and expect "ALL PASS".

## Printability rules (do not break these)

- No supports: overhangs ≤ 45° (bevels, funnels, diamond bosses, a V notch instead of a floating block), bridges ≤ ~38 mm (the pi_module port window is 54 mm, the exception to watch; the badge recess is a 10.3 mm bridge).
- **Use boolean cutters, not `chamfer()`** on rear edges. `chamfer()` silently failed once; `rear_bevel_cutter()` replaced it.
- Heat-set inserts M3×5: pilot **4.0 mm** for holes that print sideways, **4.2 mm** for holes that print vertically (`insert_d`, `insert_d_v`; from the coupons). Alignment pins are M3 screws with the heads cut off: hole 3.3 mm (`pin_d` 3.0 + `pin_clear` 0.3). Bolt holes 3.4 mm.
- General sliding clearance `clr` = 0.2. **Fit values were set from the author's coupons; do not change them without a new coupon result.**
- LCD shims are 0.4 mm steps; print at 0.2 mm layers.

## Design intent worth remembering

- **Fin stack:** four `fin_spacer_unit` (fin and spacer fused, hollow skeleton) plus one `fin_top`. Two M3×35 bolts (bolt toward the front, pin toward the rear in a shared end block) plus two ~25 mm pins; the 80 × 16 mm passage through the stack carries cables.
- **LCD:** the pocket is the panel plus `lcd_adj` (1.6) per side, taken up by side shims; four side clips 3 mm above the datum, no top or bottom rims. The black inner bezel drops in from behind, is trapped by the panel, and has no fasteners (45° wedge flanges). The datum is `LCD_Y0 = wall + bez_flange_t`. The panel's margins were first entered with top/bottom **and** left/right swapped (it was upside down): the current `lcd_margin` is the corrected one.
- **Assembly order matters:** display and fins go on **before** the Pi module (the long bolts need a clear lower body). The side cap therefore goes on **last**: two 45° hooks on the front wall plus a floor ledge, locked by the lower rear cover's two side-cap screws. The old hidden screw into the side cap under the fins is optional.
- **Power architecture as built:** USB-C PD charger → PD trigger board (12 V) → 12 V leads up the fin tunnel to a dual-output 12 V→5 V supply module hot-glued to the back of the LCD → USB-C to the Pi and USB-A to the LCD controller (also taped to the back of the panel, with the HDMI cable down the tunnel). The two buck-converter mounts (Pi module outer wall, LCD rear cover) remain but are **unused**. The case has no master power switch; the author uses an inline USB-C power switch in the power cable (link in `docs/BOM.md`), flipped after shutting the Pi down, to cut power to the LCD and the supply board.
- **Ballast:** two 1" × 3/16" steel bars in the foot slot, crosswise at the back of the foot works best (both layouts tested, empty case), held by friction (electrical tape) and the printed plug. The plug's stops: the last 6.9 mm of the slot mouth is 2.5 mm wider per side (`PLUG_EAR`, `PLUG_LEN`). Tip angles in `docs/DESIGN.md` were calculated for a single 152 × 120 × 4.76 mm plate (≈680 g), not the lighter two-bar fill; **forward tipping is the weak direction.**
- **Badge:** the front recess is **10.3 × 10.3 × 1.6 mm, 1.4 mm corner radius** (param `logo`, `logo_r`) for a 9.92 × 9.92 × 1.5 mm badge (0.5 mm chamfered plate plus raised logo). Left edge on the screen opening's left edge, centred vertically between the fins and the black bezel. The older 10 × 11 mm square-cornered slot took a 9.92 × 10.9 mm rectangular badge plate. **Do not commit the badge STL**: it carries a trademarked logo.

## Parts and hardware

13 printed parts: `lower_body`, `lcd_front_housing`, `lcd_rear_cover`, `lower_rear_cover`, `side_cap`, `pi_module`, `lcd_inner_bezel`, `fin_top`, `fin_spacer_unit` ×4, `lcd_retainer` ×4, `lcd_shim_set_side` (optional `_bottom`), `ballast_plug`; plus three coupons. Hardware, electronics and links are in `docs/BOM.md`; it counts 16 heat-set inserts (plus one optional), and the build steps are in `docs/ASSEMBLY.md`. Light parts: Polar Filament Retro Platinum PLA; black parts: black PLA.

## Provisional or assumed values (CAD says they are fine; reality may not)

`lcd_pocket_d`, `lcd_bottom` strip height (20 mm is a guess), tab zones, `trig_overhang`, `buck_hole_dy`, `ctl_board` / `ctl_holes` (the controller is taped, not mounted), `lcd_margin` (±0.8 mm tape-measure accuracy, measured on one panel), cooler headroom for a Pi 5. See `docs/KNOWN_ISSUES.md` for the full list and what would help to measure.

## Working agreements

1. **Change flow:** edit `cad/slimcase.py` → add or update a check → `python cad/export_all.py` (expect ALL PASS) → re-render affected stills → update `docs/CHANGELOG.md`, `KNOWN_ISSUES.md`, `BOM.md` and `ASSEMBLY.md` as needed → sync outputs (see above) → bump the version note.
2. **Say what needs a reprint** for each change (usually one or two parts), and prefer small targeted changes over regenerating everything.
3. The author prints and assembles real parts and reports fit findings; treat those as the ground truth and record them in `KNOWN_ISSUES.md`. Past corrections have included the LCD orientation, pin and insert hole sizes, blocked screws, cantilevered SD opening, and the need for a side-cap ledge.
4. **Licensing and trademarks:** CC BY-NC-SA 4.0. The project is not affiliated with or endorsed by Apple or frog design; do not add Apple logos or artwork to the repo.
5. **Privacy:** no email addresses or personal paths in files or commits. Commits use the GitHub no-reply address (`wottle@users.noreply.github.com`); history was rewritten on 2026-11-25 to remove a personal address, and git's global identity was changed to match. The author does his own `git commit` and `push`; do not push or publish unless asked.
6. **Software** setup (Pi OS, emulators, the kiosk launcher) lives in the separate `lisa-mini-pi` repo; this repo's `docs/SOFTWARE.md` records what worked on the author's Pi 5 / iPad 3/4 build. See "Software" below.
7. **Honesty about what the author has and has not told us:** record only what he has stated or measured. If a software fact is unknown (emulator, OS image, panel model, config.txt), ask him or have him run the command; do not guess and write it into the docs.

## History and decisions (how the repo got here)

The design started as a request for a thin, printable desktop computer around an iPad 1 panel and a Pi, and was refined over many rounds of the author's real prints. Decisions and corrections that are not obvious from the code:

- **Naming:** public project name is **Snow White Happy Pi**; the code and file names still say SlimCase (a working name). Keep both.
- **Licence:** CC BY-NC-SA 4.0 (share-alike, non-commercial), copyright "Michael Wottle". Do not overwrite `LICENSE` (it holds the full legal text).
- **Colours:** light parts are Polar Filament Retro Platinum PLA ([link](https://polarfilament.com/products/retro-platinum-pla-1kg-1-75mm)), black parts Sunlu Hi-Speed black PLA ([link](https://a.co/d/00ZGnC01)). The old "ivory" is gone from docs; `render_vtk.py` renders the light parts as platinum.
- **Retired or removed:** the flanged ballast plug (deleted; the stepped-mouth plug replaced it); temporary glue-on pieces made so the author could retrofit his older lower body (deliberately not in the repo); the buck-converter power plan (mounts left, unused).
- **Print file:** `print/SnowWhiteConcept.3mf` is the author's own Bambu Studio layout (A1, 256 × 256 mm bed; all parts also fit 250 × 250). Two of its meshes were refreshed to the current STLs (housing with the square badge recess, the stepped plug); its plate thumbnails are stale. His Bambu account ID was blanked. See `print/README.md`.
- **250 mm bed:** documented and checked in CAD only (largest footprint 232.6 × 197.4 mm, about 8 mm margin each side; avoid wide brims on the housing and rear cover). Not tested on a 250 mm printer.
- **Media:** `media/photos/` has photos of the finished build (front, side, rear, running); `media/renders/` the CAD stills; `media/slimcase_assembly_1080p.mp4`, `_preview_540p.mp4` and the README GIF are the animation: it starts from the rear of the exploded stack, zooms in as parts come together, and swings to the front. A side-by-side image the author supplied contains the original concept photo and is **not** in the repo (not his to republish).
- **Release state:** repo is private on GitHub (`wottle/snow-white-happy-pi`), going public later. Before that: review the build instructions, fill the remaining BOM links (generic parts have none), and decide about printing the v0.9d side-cap hooks (the README labels them CAD-checked only). History and the 3MF were checked for anything personal on 2026-11-25.
- **Source of truth for status:** `docs/KNOWN_ISSUES.md` (verified vs not), `docs/CHANGELOG.md` (v0.9f is current: print file, 250 mm bed, photos, filament links, new animation).

## Software

The software side is documented separately: `docs/SOFTWARE.md` (display mode, emulator settings, performance, and what was and was not verified, for the author's Pi 5 + iPad 3/4 build) and the `lisa-mini-pi` repo (`scripts/provision.sh` and its docs set up a Pi from scratch).

Physical limits that matter to software: no power button or speaker on this case, the SD card slot is on the left side, the Pi's USB and Ethernet are in the rear recess, and cooling is passive vents only.

If a different panel or controller means different dimensions, margins, mounting or connector positions, that is a **CAD** change: record it in `KNOWN_ISSUES.md`, follow the change flow above, and do not edit fit values without the author's measurements.

Do not publish, push or commit unless asked; the author commits and pushes himself.
