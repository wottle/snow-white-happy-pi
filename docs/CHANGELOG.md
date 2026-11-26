# Snow White Happy Pi — changelog (working name SlimCase)

Newest first. Entries up to v0.9 were written while the design was still a CAD-only draft; read them as history, not as the current state (see `BOM.md`, `ASSEMBLY.md` and `KNOWN_ISSUES.md` for that).

## v0.9f (print file, 250 mm bed)
- Added `print/SnowWhiteConcept.3mf`, a four-plate Bambu Studio project (the author's layout). Its display housing and ballast plug were refreshed to match v0.9e (the housing's badge recess, and the plug with stops); everything else already matched the STLs. The Bambu account ID in it was blanked. Its plate thumbnails predate that refresh.
- Added photos of the finished build (`media/photos/`) and the filament links. Re-rendered the assembly animation: it now starts from the rear of the exploded stack, zooms in as the parts come together and swings round to the front view to reveal the finished unit (plus an inline GIF for the README), shows retro-platinum instead of ivory, and leaves out the unused buck-converter placeholders. `render_vtk.py` changed; the CAD did not.
- Documented and checked that every part fits a 250 × 250 × 250 mm bed (was checked against 350 mm). Nothing in the geometry changed.

## v0.9e (square badge recess)
- The badge recess is now square to suit a 9.92 × 9.92 mm badge plate (0.5 mm plate, raised logo, 1.5 mm overall): 10.3 × 10.3 mm with rounded corners (1.4 mm radius), 1.6 mm deep, still aligned with the left edge of the screen opening and centred in the light band below it.
- 1.4 mm of the 3 mm front wall is left behind it. Reprint `lcd_front_housing` only; nothing else changed.
- Checked against the badge's actual mesh: no part of it enters the housing, with 0.19 mm clearance per side.

## v0.9d (side cap goes on last)
- **Why:** in practice the display and fins have to be bolted on before the Pi module goes in, and the side stays open for wiring, so the screw down through the body top into the side cap (hidden under the bottom fin) can never be fitted.
- **Front hooks:** two 10 mm wedges on the inside of the lower body's front wall (20 and 88 mm below the body top), and two matching arms with 45° fingers on the side cap. Hook the cap's front edge on, swing the rear in (it needs about 16° of swing), then the lower rear cover's two right-hand screws lock it. With the bottom ledge, the cap is now held along the front, bottom and rear.
- Both hook faces are 45°, so both parts still print without supports. A hard pull on the cap's front edge is turned into a rearward push, which the rear-cover screws resist.
- The screw hole under the fin and its tab are still there but are now optional.
- **Lower rear cover screw vs buck converter:** the lower right screw and the side-cap tab it goes into were already moved down in v0.8, to 84 mm below the body top (was 60); the tab clears the converter by 6 mm. A side cap or lower rear cover printed before v0.8 has the old position and must be reprinted.
- Reprint: `lower_body`, `side_cap`. `lower_rear_cover` only if yours predates v0.8.

## v0.9c (ballast plug stops)
- The last 6.9 mm of the ballast slot (the mouth) is now 2.5 mm wider on each side than the plate slot, and `ballast_plug` is wider to match (158 mm). The shoulders where the slot narrows stop the plug after 0.3 mm of travel, whether or not the plate is behind it. The plate (152.4 wide) still slides straight through. 6 mm of foot remains outside each end of the plug.
- Reprint: `lower_body`, `ballast_plug`.

## v0.9b
- **Rear-rib notch is now a V** (45° sides, 4.5 mm deep, 9 mm wide at the rib's lower edge) behind the X=44 Pi-module screw. The rib stays one piece, so there is no floating block to support when the body prints on its side. It clears a tool up to about 10 mm in diameter on the screw's axis.
- **Logo recess** on `lcd_front_housing`: 10 wide × 11 tall × 1.2 deep (`logo`). Its left edge is on the left edge of the opening in the ivory (the black bezel's outer edge, X=12.1); it is centred between the fins and the black bezel, with 7.6 mm of ivory above and below. Printed face-down it is a 10 mm bridge 1.2 mm above the bed.
- Reprint: `lower_body`, `lcd_front_housing`.

## v0.9 (fixes from the first real assembly)
- **Pi-module top screws moved down** out from behind the rear-cover rib: now 20 mm (left, X=11.5) and 17 mm (X=44) below the body top, was 9.5. The second one cannot go lower without its boss showing in the left floppy slot, so the rear rib is notched behind it (a V notch as of v0.9b). A straight 6 mm driver path from the rear to both is checked clear. Bosses and holes moved in both `lower_body` and `pi_module`.
- **SD-card opening** is now a 45° funnel (2 mm deep, slot 15 × 4 opening to 19 × 8 on the outside) instead of a stepped scoop, so it prints left-side-down without supports.
- **Ledge for the side cap:** a 3 mm triangular ledge (45° underside) runs along the bottom edge of the side opening, just inside the cap, so the cap's inner face has something to press against. `side_cap` itself is unchanged.
- Reprint: `lower_body`, `pi_module`. Unchanged: `side_cap`, `lower_rear_cover`, everything in the display half.
- Note: the X=44 screw sits under where an HDMI plug in the Pi's second HDMI port will be; fit the module screws before plugging cables.

## v0.8 (buck converter on the Pi module)
- **New mount on `pi_module`:** two vertical bars on the outside of the port-recess wall (the side facing the right-hand side panel). The 43 × 21 board stands on edge against them, parts toward the side panel, 2.4 mm clear of it and 4 mm clear of the rear cover. M3 thread-forming screws, 2.5 mm pilots about 4.4 mm deep.
- **Four holes, use two:** both diagonals are provided (here and on the LCD rear cover), because a diagonal pair is handed and I can't tell from the photo which way yours runs. Every diagonal is 35.0 mm.
- **Port recess narrowed 54 → 51 mm** (`rec_w`) to widen that bay from 15 to 18 mm. Less room for a plug and cable bend in the recess.
- **Lower-right rear-cover screw moved down** from 60 to 84 mm below the body top (`Z_SCR_LOW`) so its tab clears the converter. Driver clearance over the foot is by calculation only.
- A small black strip was added behind the right-hand end of the right floppy slot, which the narrower recess would otherwise have left open.
- The LCD rear cover keeps its buck mount (now four standoffs) as an alternative location.

## v0.7b
- **LCD controller is no longer mounted on the rear cover.** The builder fixes it to the back of the panel with double-sided tape so the fragile flex is never pulled when the cover comes off. The controller standoffs are removed from `lcd_rear_cover`; only the two buck-converter standoffs remain on it.
- There is 26.2 mm between the panel's back and the cover skin. Keep the controller to the left of the buck converter (which occupies X 174–196 around the screen's mid-height) and above the thick bottom strip.

## v0.7
**Display housing shape (per the design sketch)**
- A body-width **neck** (`neck_h` = 14 mm) now runs from the screen section down to the fins; the overhang to the right starts above it with a concave curve. Top-left, top-right and the overhang's lower-right corner are rounded to the same 8 mm radius (`hous_r`); the lower-left stays square and in line with the body. The rear cover follows the same outline. Overall height grows by 14 mm.
- The 18 mm bezel is still equal on all four sides of the screen rectangle; the neck is extra below it.

**Black inner bezel** (`lcd_inner_bezel`, new part)
- A black ring 5.9 mm wide fills an opening in the ivory front, flush with the face, leaving 12.1 mm of ivory outside it. Inner edge is chamfered toward the screen.
- It drops in from behind. 45° flanges along its top and bottom catch behind the ivory, and the LCD sits on its back, so it is captive with no fasteners. It is not a spring snap: a rigid captive fit is more reliable in a thin printed frame.
- Width is capped near 6 mm because the opening has to stay inside the LCD pocket on the right-hand side; wider needs supports under the side ledge (`bezel_black`).
- The LCD now sits 1 mm further back (on the bezel's back face); clips and shims moved with it.

**Dummy floppy slots**
- Two 60 × 4 mm slots through the lower-body front, side by side, centred 25 mm below the fins, 10 mm apart. The black Pi-module plate sits 4 mm behind them.
- To keep ivory out of view the Pi module's top two screws moved up into the front rib and one lower boss moved down; the module plate now reaches the body ceiling.

**LCD (corrected orientation and coupon results)**
- Margins turned 180° (left 5.0, right 2.5, bottom 6.0, top 9.5, to the edge of the dark border). The pocket moved 2.5 mm left and 3.5 mm up relative to v0.6.
- Thick strip: on the bottom, 5.5 mm thick, 85 % of the width. Its height (20 mm) is still a guess.
- **No top or bottom rims:** the pocket now runs the full inside height, so the panel slides freely up and down (about 7 mm of room below nominal, 3.6 above). Only the side walls and side shims locate it. The bottom shim set is now optional.
- Side-tab reliefs are 16 mm tall to follow that vertical movement. The bottom-left tab needs no relief any more.

**Fastener holes from the coupons**
- Heat-set pilots: 4.0 mm where the hole prints sideways (lower body, side cap), 4.2 mm where it prints vertically (display housing). Sized for M3 × 5 inserts.
- Alignment-pin holes opened to 3.3 mm so an M3 screw (head cut off, about 25 mm long) slides in as the pin. Bolt holes stay 3.4.

**Electronics**
- Trigger board: measured holes (3.2 mm, 14.8 mm apart, centres 3.15 mm from the socket-end edge).
- **Buck converter moved to the LCD rear cover.** At 43 × 21 × 13 mm it does not fit the 15 mm bay beside the port recess. It now sits on two diagonal standoffs on the inside of the LCD rear cover, right of the vents, components toward the panel, 3.4 mm clear of the LCD clips. 12 V already comes up the fin passage for the LCD controller; 5 V goes back down to the Pi. Hole pattern 31.1 × 16.0 mm is derived from the 35 mm diagonal and an **assumed** 16 mm spacing across the board.

## v0.6 (real USB-C trigger board)
- Mount rebuilt for the board in the seller's drawing: **40.7 × 20 mm**, two 3 mm holes **15 mm apart** flanking the USB-C socket (`trig_board`, `trig_hole_pitch`).
- The board screws to two posts on the Pi module through its own holes (M2.5 thread-forming, 2.2 pilot), socket end against the recess wall, wire end on a small rest. It sits 11 mm above the tray, 6.4 mm above the Pi's PCB, so it overhangs the Pi's top edge without touching anything (including a Pi 4 audio jack).
- The slot in the recess wall is counterbored from the recess side so a plug's overmold can seat fully.
- One Pi-module screw moved (to X=44) so it is not hidden under the board.
- **Still guessed:** the distance from the board's socket-end edge to the hole centres (3.5 mm, scaled from the photo) and how far the socket overhangs that edge (1.5 mm).
- **Buck converter:** unchanged placeholder. A 35 mm hole diagonal alone does not fix the hole pattern; the board's length and width, or one side spacing, is needed.

## v0.5b (measured panel + adjustable shims)
- **Panel size from measurement:** 8-3/16" × 6-9/16" = 207.96 × 166.69 mm excluding tabs, 2.8 mm thick at the sides (`lcd_panel`).
- **Off-centre image:** measured margins from panel edge to visible image, seen from the front: left 2.5, right 5.0, bottom 9.5, top 6.0 (`lcd_margin`). The pocket is shifted 1.25 mm right and 1.75 mm down so that this panel's image centres in the aperture.
- **Adjustment:** the pocket is 1.6 mm bigger than the panel on every side (`lcd_adj`). Loose printed shims fill the gaps, 0.4 to 3.2 mm thick in 0.4 mm steps; the number of notches on a shim's edge is its thickness in steps (3 notches = 1.2 mm).
  - **Side shims** (`lcd_shim_set_side`, 24 × 2.6 mm): one under each side clip, which traps it. Left + right thickness must add up to 3.2 mm; 1.6 + 1.6 is this panel's nominal. Moving the image 0.4 mm left means swapping to 1.2 on the left and 2.0 on the right.
  - **Bottom shims** (`lcd_shim_set_bottom`, 30 × 5.5 mm): two under the panel's bottom edge set its height (nominal 1.6) and carry its weight. Range ±1.6 mm.
  - The top gap is left open; the panel rests on the bottom shims and is held by the side clips and, where present, its own tape.
- The bottom ledge is gone: the pocket now runs down to the housing floor, which is only 1.6 mm below this panel's bottom edge.
- **Check this:** the measured margins imply a visible area of 200.5 × 151.2 mm, but the aperture is the nominal 196.6 × 147.45 mm, so the bezel would cover about 1.9 mm of it on every side. If the margins were measured to the edge of the dark border and not to lit pixels, that is expected. If lit pixels really span 200.5 × 151.2, change `active_w` / `active_h`.

## v0.5 (LCD mounting, from measurements of the panel)
- **Tab reliefs:** six notches in the pocket wall for the panel's metal tabs: both ends of each side and both ends of the top edge, each 5 mm outboard × 12 mm long (tabs reported as ~4 mm proud, within ~10 mm of the corners). None on the bottom edge. The pocket walls still locate the panel everywhere else.
- **Side-only clips:** the four retainers are on the left and right only. Each screws to the ledge and has a finger that reaches down to 3.0 mm above the pocket floor (`lcd_clip_h`), over the panel's 2.8 mm side edge, leaving 0.2 mm for a thin pad. Print top-face-down.
- **Thicker bottom edge:** nothing bears on it. The panel placeholder now has a 20 mm-tall, 5.8 mm-thick bottom strip; both numbers are guesses.
- **Rear-cover screws moved:** the four screw columns were in the corners, exactly where the side tabs need room, so they now sit about 19 mm in from each corner along the sides.
- `renders/10_lcd_bay_with_panel.png` and `11_lcd_bay_empty.png` show the display housing from behind with the cover off.

## v0.4
- **Fused fin + spacer:** each fin now prints with its spacer frame on top as one 4 mm part (`fin_spacer_unit`, print 4, fin face down). One plain 2 mm fin (`fin_top`, print 1) finishes the stack. Still five fin edges, four recessed gaps, 18 mm total; 5 prints instead of 9.
- **Hollow skeleton:** the solid plates are replaced by a rectangular frame: 4 mm perimeter wall, a 19 mm solid block at each end, and a 4 mm centre web that lines up with the mullion in the display-housing floor. Two 59 × 18 mm windows run through the whole stack (52 % of the frame footprint is open); cables use them.
- **Bolt and pin moved:** each end block now carries one through-bolt (toward the front) and one alignment pin (toward the rear) at the same X, 8 mm apart, instead of being spaced along the centreline. Hole positions in the lower body and display housing follow automatically.
- Load path: bolt tension clamps the end blocks; the frame walls sit on the solid parts of the body top and housing floor. Fin tips carry nothing.

## v0.3
- **Slimmer:** enclosure depth 48 → **36 mm** (`depth`). Fins are now 170×36, cable passage 80×16.
  - Lower body budget: 3 wall + 4 boss + 2.5 tray + 3 standoff + 1.6 PCB + 16 USB/Ethernet stack = 30.1 of 33 available. The Pi's USB stack sets the floor at roughly 34.
  - Display housing budget: LCD + retainers end at 12 mm; controller PCB sits at 27.4–29 mm, leaving about 15 mm for its components (unverified).
- **Lower rear cover:** the two bottom screws are gone. Two hooks on the cover's bottom edge drop behind a 4 mm sill; three screws along the top and one on the right at mid-height hold it. All four are well clear of the foot.
- **Pi module:** its low screw moved up for the same reason.
- **Foot:** 6 → **10 mm** thick (`foot_t`).
- **Ballast:** a steel plate slides into a slot in the foot from the rear edge, closed by a printed black strip. Modelled as 6" × 3/16" flat bar cut to 120 mm (152.4 × 120 × 4.76, about 680 g). The old floor pocket is removed.
- **Rear bevels:** 3 mm 45° bevel around the LCD rear cover (now a cap over the housing walls), down both rear edges of the lower body, round the foot fillet and along the foot's top edges. Rear inner curve radius 14.
- **Front curve** restored to radius 24 (was cut to 18 for stability; the heavier plate makes that unnecessary).
- **Power:** barrel jack replaced by a cradle and 9.4 × 3.6 slot for a USB-C PD trigger board (assumed 28 × 12 mm) in the recess wall above the Pi ports. 12 V splits to the LCD controller (up the fin passage) and to a buck converter in the bay right of the recess.
