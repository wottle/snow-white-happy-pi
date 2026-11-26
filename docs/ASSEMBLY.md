# Snow White Happy Pi — assembly guide

For design v0.9f, based on my completed Pi 5 build. See the [BOM](BOM.md) for parts and panel compatibility, and the [verification notes](KNOWN_ISSUES.md) for the fit checks on individual revisions.

This order comes from the CAD model and from the first real build. The display and fins go on **before** the Pi module, because the long bolts need a clear lower body; the side cap goes on **last**.

Directions: "left" and "right" are as you face the screen. Most work is done from behind.

## Before you start

1. **Check the controller's power input.** This wiring uses a 5 V LCD controller. Verify that your controller accepts 5 V and that the shared supply is rated for both the Pi and the display.
2. **Set the trigger board to 12 V.** Power the trigger on its own and confirm its output voltage and polarity with a multimeter.
3. Disconnect the charger. Wire the trigger output to the 12 V input of the 5 V supply module, matching positive and ground. Power it and check for 5 V on both USB outputs before connecting the Pi or the controller.
4. Disconnect the charger again. Connect the LCD to its controller, HDMI between the controller and Pi, and 5 V power from the supply module to both. Power up on the bench and confirm you get a picture. Shut the Pi down and disconnect the charger before transferring the parts to the case.
5. Cut two pieces from the 1" × 3/16" steel bar for the ballast (see Step 2). Deburr the ends.
6. Cut the heads off two M3 screws to make two pins about 25 mm long.

## Step 1 — Heat-set inserts (16)

- **Lower body, 6:** four in the diamond-shaped bosses on the inside of the front wall; two in the rail across the top of the rear opening.
- **Side cap, 2:** one in each tab on its rear edge. (A third hole, in the top tab, is optional and unused in this build order.)
- **Display housing, 8:** four in the tall columns on the side ledges; four in the side ledges themselves, for the LCD clips.

Press them in straight and flush. Let each cool before moving on.

## Step 2 — Ballast

The slot in the foot is open at the back edge and about 153 mm wide, 5.2 mm tall and 120 mm deep. This build fills it with two pieces of 1" × 3/16" steel bar rather than one wide plate.

1. Cut two pieces of bar. Each must be short enough that, with the plug fitted, nothing sticks out of the slot. For the endwise layout that is about 115 mm (120 mm at the very most); for the crosswise layout, about 150 mm so they fit inside the 153 mm slot width.
2. Wrap each piece with a couple of layers of electrical tape until it is a firm friction fit in the slot and won't shift. Test-fit before the plug goes on.
3. Both layouts have been tried and both work:
   - **Crosswise (preferred):** lay both pieces across the width of the rear foot, as close to the rear opening as the fitted ballast plug allows.
   - **Endwise:** slide them in lengthwise, side by side, so that looking into the slot you see only the 1" ends.
4. Press the ballast plug in behind them. It stops on the shoulders at the slot mouth. A dab of glue is fine if it is loose.

Two pieces were plenty to keep the first build stable in either layout. The ballast plug's stops hold it in place.

## Step 3 — Fin stack and display housing

1. Press the two pins into the two blind holes in the top of the lower body (the rear hole of each pair).
2. From inside the lower body, push the two M3 × 35 bolts, each with a washer, up through the front hole of each pair.
3. Stack the four fin-spacer units over the bolts and pins, **fin side down, frame side up**.
4. Add the plain top fin.
5. Lower the display housing onto the bolts and pins.
6. Reaching in through the open back of the housing, fit a washer and nyloc nut on each bolt. Hold the bolt head with the hex key from inside the lower body. Tighten until snug, no more: the frames carry the load, and over-tightening can crack them.

## Step 4 — LCD

1. Drop the black inner bezel into the housing from behind. It seats in the opening and sits flush with the front face.
2. Lay the LCD on the back of the bezel, screen forward, thick edge at the bottom. The metal tabs on its sides go into the notches in the pocket walls.
3. Drop a side shim into the gap on each side, level with each clip position (four shims). Start with 1.6 mm (four notches) all round.
4. Power the screen and check the picture against the bezel.
   - Left–right: swap shims. The left and right thicknesses must add up to 3.2 mm.
   - Up–down: slide the panel. There is no stop above or below it.
5. Stick a thin pad on the side edge of the panel under each clip.
6. Fit the four side clips with M3 × 6 pan-head screws. They hold the panel and trap the shims.

## Step 5 — LCD controller, power module and display wiring

1. Connect the panel's flex cable to the controller.
2. Fix the controller to the back of the panel with double-sided foam tape, above the thick bottom strip.
3. Hot-glue the 12 V to 5 V supply module to the back of the LCD. There is plenty of room beside the controller.
4. Connect the controller to the supply module's USB-A output with a USB-A to USB-C cable.
5. Feed the following through the fin tunnel (the 80 × 16 mm passage through the fin stack) into the lower body, leaving enough length to reach the Pi module:
   - the supply module's second cable, a USB-C cable, for the Pi;
   - the mini HDMI to micro HDMI cable from the controller, for the Pi.
6. The supply module's 12 V input leads also come down the tunnel to the trigger board. They are connected in Step 7.

Leave the display's rear cover off until everything has been tested.

## Step 6 — Build up the Pi module (on the bench)

1. **Trigger board:** seat it on its two posts with the USB-C socket through the slot in the recess wall; two M2.5 × 6 screws.
2. **Pi:** slide its USB/Ethernet end into the window in the recess wall first, then lower it onto the four standoffs; four M2.5 × 6 screws.
3. With the charger disconnected, connect the pair of 12 V leads to the trigger board's output. Allow enough slack to reach the supply module through the fin tunnel.

The mounting bars for a buck converter on the Pi module are not used in this build. Leave them empty.

## Step 7 — Install the Pi module

1. Slide the module into the lower body from behind until its plate sits on the four bosses.
2. Fit the four M3 × 6 pan-head screws: two near the top right as seen from behind (below the rail; one sits behind the V notch), two in the floor of the port recess. **Do this before plugging in the cables**; a plug covers one of the top screws.
3. Run the 12 V leads from the trigger board up the fin tunnel and connect them to the supply module's input. Check polarity.
4. Plug the USB-C cable from the supply module into the Pi's power port, and the micro HDMI end of the HDMI cable into the Pi.
5. Insert the microSD card through the slot in the left side.
6. Power up and test before closing anything.

## Step 8 — Close up

1. **Side cap:** hook its front edge onto the two wedges inside the front wall, then swing its rear edge in until it is flush. Its bottom edge rests against the ledge on the floor.
2. **Lower rear cover:** drop the two hooks on its bottom edge behind the lip at the bottom of the opening, swing it shut around the port recess, and fit four M3 × 8 countersunk screws. The two on the side-cap side go into the side cap and lock it.
3. **Display rear cover:** fit with four M3 × 10 countersunk screws.
4. Optional. Glue your square badge into the recess below the screen, plate down and raised detail up. The recess is 0.1 mm deeper than the reference badge.

## Taking it apart

Reverse of the above. To reach the Pi: lower rear cover off, side cap off, unplug HDMI, four module screws. The SD card comes out through the side slot without opening anything.

## Known limits

- The side cap's hooks are 45° wedges, so the cap is only fully secure once the rear cover's screws are in.
- With no stop under the LCD, its height is held by clip pressure and any tape on the panel.
- Cable bend room is tight: 51 mm across the port recess, about 32 mm above the Pi for HDMI.
- The ballast in this build is two bars, about 230 g in total (for 120 mm lengths), against the 680 g plate the stability figures were calculated with. It was stable in practice in both layouts (crosswise the better), but the tip angles have not been recalculated for it.
- The fins are decorative. Cooling is by the vent slots in the two rear covers; no thermal testing has been done.
- This build has no built-in sound, external power switch or case-mounted shutdown button. I use an optional [inline USB-C power switch](BOM.md#3-electronics). Shut down the Pi from the operating system, wait for shutdown to finish, then use the inline switch or disconnect the power cable.

## Software

See [`SOFTWARE.md`](SOFTWARE.md) for the display mode and emulator settings I used on my Raspberry Pi 5 with an iPad 3/4 LCD. The companion [`lisa-mini-pi`](https://github.com/wottle/lisa-mini-pi) project sets up Raspberry Pi OS, the emulators and the kiosk launcher. You supply your own ROMs and disk images.
