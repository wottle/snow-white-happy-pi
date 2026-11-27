# Snow White Happy Pi — bill of materials

Parts for one v0.9f case, with a Pi 5 and a 12 V to 5 V supply module. Printed-part quantities come from the CAD model. Where available, links identify example parts.

## 1. Printed parts

**Filament:** the light parts are printed in [Polar Filament Retro Platinum PLA](https://polarfilament.com/products/retro-platinum-pla-1kg-1-75mm) and the black parts in [Sunlu Hi-Speed black PLA](https://a.co/d/00ZGnC01). The fins, inner bezel, Pi module and shims are black PLA. (The clips and the ballast plug are hidden and are printed in the light colour in the supplied project, but either works.)

All parts fit a **250 × 250 mm** bed (the biggest footprint is 233 × 197 mm, for the display housing and its rear cover; the tallest part is the lower body at 170 mm) and are exported in print orientation, sitting on Z=0, in `stl/`. The file name carries the quantity. None needs supports by design, but check each one in the slicer preview.

| Part | Qty | Colour | Lay it down on | Size on bed (mm) | Notes |
|---|---|---|---|---|---|
| `lower_body` | 1 | retro platinum | its left side | 129 × 149 × 170 | The long print. About 15 % infill is enough. |
| `lcd_front_housing` | 1 | retro platinum | front face | 233 × 197 × 31 | Two 38 mm bridges over the cable openings; 10.3 mm bridge over the badge recess. |
| `lcd_rear_cover` | 1 | retro platinum | outer face | 233 × 197 × 6 | Four small standoffs inside for an optional buck-converter position (unused in the as-built). |
| `lower_rear_cover` | 1 | retro platinum | outer face | 159 × 98 × 8 | Hooks point up. |
| `side_cap` | 1 | retro platinum | outer face | 100 × 33 × 15 | Right-hand side panel. |
| `fin_spacer_unit` | 4 | black | fin face | 170 × 36 × 4 | Fin and spacer frame in one piece. |
| `fin_top` | 1 | black | flat | 170 × 36 × 2 | Plain top fin. |
| `pi_module` | 1 | black | flat plate | 148 × 91 × 29 | Pi tray, port recess, trigger-board posts, optional buck-converter bars (unused in the as-built). 54 mm bridge over the port window. |
| `lcd_inner_bezel` | 1 | black | front face | 208 × 163 × 4 | Thin frame; handle gently until installed. |
| `lcd_retainer` | 4 | retro platinum | top face | 14 × 8 × 5 | Side clips for the LCD. |
| `lcd_shim_set_side` | 1 plate | black | flat | 18 loose shims | 0.4 to 3.2 mm in 0.4 mm steps; notches on the edge = thickness ÷ 0.4. Use 0.2 mm layers. |
| `lcd_shim_set_bottom` | optional | black | flat | 16 loose shims | Only if you want a hard stop under the panel. |
| `ballast_plug` | 1 | retro platinum | flat | 158 × 6 × 5 | Closes the slot in the foot. |

The [four-plate Bambu Studio project](../print/README.md) contains the main case parts. Print the LCD shims separately from [the STLs](../stl).

Fit-test coupons are in `stl/coupons/`: `coupon_hole_fit`, `coupon_insert_fit`, `coupon_lcd_pocket_corner`. Print the first two before anything large if you change printer, filament or inserts.

**Filament (rough estimate, not weighed):** about 520 g retro platinum and 130 g black, assuming 3 walls and mostly-solid small parts.

## 2. Fasteners and hardware

| Item | Qty | Where it goes | Link |
|---|---|---|---|
| M3 × 5 mm heat-set insert | 16 (+1) | 6 in `lower_body`, 2 in `side_cap`, 8 in `lcd_front_housing`; +1 optional in the top of `side_cap` | |
| M3 × 35 socket-head cap screw | 2 | Through-bolts for the fin stack | |
| M3 washer, 7 mm OD | 4 | Under each bolt head and each nut | |
| M3 nyloc nut | 2 | On the through-bolts, inside the display housing | |
| M3 screw or 3 mm rod, about 25 mm, no head | 2 | Alignment pins for the fin stack (cut the head off an M3 screw) | |
| M3 × 10 countersunk | 4 | `lcd_rear_cover` | |
| M3 × 8 countersunk | 4 (+1) | `lower_rear_cover`; +1 optional for the side cap under the bottom fin | |
| M3 × 6 pan head | 8 | 4 LCD clips, 4 `pi_module` to lower body | |
| M3 × 6 thread-forming (self-tapping for plastic) | 2 (optional) | Only if you mount a buck converter on the Pi module's bars; not used in the as-built | |
| M2.5 × 6 thread-forming | 6 | 4 Pi to its standoffs, 2 trigger board to its posts | |
| Steel flat bar, 1" × 3/16" (25.4 × 4.8 mm), 3 ft length | 2 pieces cut from it | Ballast in the foot, about 150 mm each crosswise (preferred), or 115–120 mm each endwise. The case tips forward without ballast. | |
| Electrical tape | 1 roll | A couple of layers around each ballast bar for a friction fit | |
| Hot glue | — | Holds the supply module to the back of the LCD | |
| Thin felt or foam tape, about 0.3 mm | small strip | Pads under the four LCD clip fingers | |
| Double-sided foam tape | small strip | LCD controller to the back of the panel | |

Heat-set insert locations, for counting:
- `lower_body`: 4 in the bosses on the inside of the front wall (Pi module), 2 in the rail across the top of the rear opening (rear cover).
- `side_cap`: 2 in its rear tabs (rear cover), 1 optional in its top tab.
- `lcd_front_housing`: 4 in the tall columns on the side ledges (rear cover), 4 in the side ledges (LCD clips).

## 3. Electronics

**Display compatibility.** My completed build uses an iPad 3/4 LCD. Older iPad 1/2 LCDs also work. The CAD uses measurements from an iPad 1 panel. Match the HDMI controller and panel cable to the exact LCD model before buying.

The power wiring in the [assembly guide](ASSEMBLY.md#before-you-start) uses a **5 V LCD controller**. Confirm the exact controller's input voltage and the supply module's combined output rating for both loads. Raspberry Pi documents 5 V/3 A as the Pi 5 minimum and 5 V/5 A for the full USB peripheral power budget. The shared supply in this build has only been checked in light use. [Raspberry Pi power documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply)

| Item | Qty | Notes | Link |
|---|---|---|---|
| 9.7" iPad LCD | 1 | **iPad 3/4 (2048 × 1536)** in my build, driven at 1024 × 768. **iPad 1/2 (1024 × 768)** also works. The reference iPad 1 panel measures 207.96 × 166.69 mm without tabs and 2.8 mm thick at the sides. | [iPad 3/4 LCD and controller used in my build](https://www.aliexpress.us/item/3256808575148848.html) · [iPad 1 LCD and controller](https://www.aliexpress.us/item/3256801532761537.html) |
| HDMI controller and matching panel cable | 1 set | Use the controller matched to the panel. Confirm 5 V input for the documented wiring. | Included in the listings above |
| Raspberry Pi 5 | 1 | A Pi 4 shares the mounting pattern. In-case fit and port clearances still need a physical check. | |
| Pi cooler / heatsink | 1 | Up to about 10 mm tall above the board (not verified against a specific cooler). | |
| microSD card | 1 | Reachable through the slot in the left side. | |
| USB-C PD trigger board, 40.7 × 20 mm | 1 | Two 3.2 mm holes 14.8 mm apart at the socket end. Set to 12 V. | [Amazon](https://www.amazon.com/dp/B0DBHGMW33) |
| 12 V to 5 V supply module with USB-C and USB-A outputs | 1 | Wired to the trigger board's 12 V; USB-C feeds the Pi, USB-A feeds the LCD controller. Must give a steady 5 V; check its current rating against the Pi you use (a Pi 5 draws more than a Pi 4). | [AliExpress](https://www.aliexpress.us/item/3256808543956539.html) |
| USB-C PD charger and cable | 1 | Must offer a 12 V output; not every PD charger does. | |
| Inline USB-C power switch | optional | The case has no master power switch. This sits in line with the USB-C power cable that feeds the case: after I shut the Pi down, I flip it to cut power to the LCD and the supply board. | [Amazon](https://a.co/d/0borm2n2) |
| Mini HDMI to micro HDMI cable, short | 1 | LCD controller to the Pi, through the fin tunnel. About 32 mm of room above the Pi's HDMI edge. | |
| USB-C cable, short | 1 | Supply module to the Pi, through the fin tunnel | |
| USB-A to USB-C cable, short | 1 | Supply module to the LCD controller | |
| Hook-up wire, about 20–22 AWG | — | 12 V from the trigger board up the fin tunnel to the supply module | |
| Heat-shrink tubing or electrical tape | — | Insulates the 12 V joints | |
| Square badge, 9.92 × 9.92 mm plate, 1.5 mm overall | optional | Supply your own badge for the 10.3 × 10.3 × 1.6 mm recess. The reference badge has a 0.5 mm plate, 1.25 mm corner radius, 0.4 mm underside chamfer and 1.0 mm raised detail. | |

## 4. Tools

Soldering iron with a heat-set insert tip, 2.5 mm hex key, 5.5 mm nut driver or small pliers, small Phillips screwdriver, multimeter, hacksaw (steel bar, screw heads), hot glue gun, flush cutters, wire strippers, tweezers.
