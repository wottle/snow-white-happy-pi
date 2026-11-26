# Snow White Happy Pi — software notes (Raspberry Pi 5, iPad 3/4 panel)

What worked on one build. This is not a general recipe, and it does not cover installing Raspberry Pi OS or building the emulators.

**To set a Pi up from scratch** (Raspberry Pi OS, six emulators, the kiosk launcher and boot splash), use the separate [`lisa-mini-pi`](https://github.com/wottle/lisa-mini-pi) repo. Its `scripts/provision.sh` runs the setup and its `docs/software-setup.md` explains each step. You supply your own ROMs and disk images. It builds LisaEm from the `pi4-lisa-fixes` branch of [`wottle/lisaem`](https://github.com/wottle/lisaem), which carries the fixes below.

The Happy Pi case has no built-in sound, external power switch or case-mounted shutdown button. The companion project's GPIO button and LED scripts are for builds that include that hardware.

How to read it: **measured** means a value read from the Pi or timed during the session of 2026-11-21. **Reported** means what I saw on the panel myself. **Not tested** is listed at the end. Nothing here was run on any other Pi or panel.

## The build as tested

| Item | Value | Source |
|---|---|---|
| Computer | Raspberry Pi 5, 4 GB (4045 MiB) | measured |
| OS | Raspberry Pi OS 64-bit, Debian 13 "trixie", kernel 6.18 (`rpt-rpi-2712`) | measured |
| Panel | iPad 3/4 class LCD, 2048 × 1536 native | me; EDID confirms the mode |
| LCD controller board | HDMI controller from the same kit as the LCD | [AliExpress kit used in my build](https://www.aliexpress.us/item/3256808575148848.html) |
| Link | HDMI. The panel is on the Pi 5's second HDMI connector (`HDMI-A-2`); the first is unused | measured |
| Graphics | X11 (Xorg, `modesetting`, glamor acceleration on V3D 7.1.7) under Openbox, started by a kiosk launcher service | measured |
| `config.txt` | Raspberry Pi OS defaults (`vc4-kms-v3d`, `max_framebuffers=2`); no `hdmi_*` overrides | measured |
| Storage | microSD: 93 MB/s sequential read, 0.3 ms median 4 KB random read (uncached) | measured |

An older iPad 1/2 LCD (1024 × 768) also works for the build. The CAD dimensions come from an iPad 1 panel. See the [BOM](BOM.md#3-electronics) for the display options.

## Display mode

The panel's EDID prefers its native 2048 × 1536 @ 60.37 Hz (205 MHz pixel clock). It also lists 1024 × 768 at 60 Hz (65 MHz) and 75 Hz, along with the usual lower modes.

**What the build uses: 1024 × 768 @ 60 Hz, with the LCD controller doing the upscaling.** Reasons:

- Every emulator in my stack is configured for 1024 × 768, so they render 1:1 with no software scaling.
- The Pi pushes a quarter of the pixels.
- I looked at it on the panel and it looks good to me. I did not record edge cropping, sharpness against the native mode, or whether the board scales or only centres.

**Trial at the panel's native 2048 × 1536 (measured).** With `frameskip 1`, Basilisk II held about 60 updates per second at 2048 × 1536 in all three modes tried: the default 2× upscale, nearest-neighbour with integer scaling (crisp, looks like the 1024 × 768 layout doubled), and a guest running at native size (a very small UI with a lot of workspace, with some 33 ms gaps). The default upscale looked slightly softer. So the slowness described below was not caused by the resolution. I tried native on the panel and **went back to 1024 × 768**: the UI is too small at native. Mini vMac (a fixed 1024 × 684 build) showed as a small centred window, and LisaEm's Fill mode (a 1024 × 728 bitmap, scaled) left margins of 40 px above and below at native, in which the pointer stops controlling the Lisa (measured; the same code leaves 20 px at 1024 × 768, where the mouse was not tested).

It is set by one `xrandr --output <connected output> --mode 1024x768 --rate 60` line in the kiosk's X session script, run before the launcher starts. To go back to native, remove that line (or run `xrandr --output <output> --mode 2048x1536`). The console and boot splash appear at 2048 × 1536 before X starts. A kernel `video=` setting would change that; it was **not tried**.

## What was slow, and what fixed it

Starting symptoms (reported): the launcher screen did not fill the panel, and all emulators ran poorly.

**Ruled out (measured):**

| Suspect | Finding |
|---|---|
| Throttling or undervoltage | `vcgencmd get_throttled` = `0x0` in every sample; 47–57 °C |
| CPU clock | `ondemand` governor: 1.9 GHz idle, 2.4 GHz within seconds under a one-core load |
| HDMI mode | Native mode was driven correctly; the problem was not the output |
| GPU acceleration | glamor active on V3D; Basilisk II logs `SDL_Renderer driver: opengl` |
| Disk | 93 MB/s and 0.3 ms random reads (see table above) |
| Renderer, vsync, windowed vs. fullscreen, `idlewait` (Basilisk II) | No effect on frame rate |

**Found and fixed:**

1. **Launcher layout.** The launcher draws a fixed 1024 × 768 design. On a 2048 × 1536 screen it filled a small part of it. It now scales the design by the largest whole number that fits and centres it (2× at 2048 × 1536, 1× at 1024 × 768), so bitmap text and borders stay crisp. At the 1024 × 768 output the factor is 1.
2. **Launcher idle CPU.** It redrew the whole frame 30 times a second with nothing changing: about 48.5% of one core (17 ms per frame at 2048 × 1536, measured). It now redraws only when something visible changes, plus once a second as a safety refresh. After the change: about 3% at 2048 × 1536 and about 2% at 1024 × 768 (measured).
3. **Basilisk II refresh rate.** Its `frameskip` preference defaults to 0, which in this build gave only **about 11 screen updates per second** (measured, with the pointer moving). Mouse pointer and drawing both felt jerky because the pointer is drawn by the guest. `frameskip 1` gave **about 61 per second**; `frameskip 6` gave 11 again. Only 0, 1 and 6 were tried. The software renderer, vsync off, `idlewait` and windowed mode all stayed at about 11. Add `frameskip 1` to `~/.config/BasiliskII/prefs`.
4. **LisaEm showed a quarter of the screen.** `~/.lisaem` had `hidpi_scale=200`, which renders at twice the size. At a 1024 × 768 output the correct value is `100`. LisaEm rewrites this file when it exits, so edit it while LisaEm is not running.
5. **LisaEm picture offset and "escaping" pointer.** On about half of launches (3 of 6 in a virtual 1024 × 768 test) the Lisa picture sat 43 px down with its bottom rows clipped, and the pointer, once in the black margin, showed the host arrow and stopped controlling the Lisa. Cause: LisaEm's Fill mode centred the picture from the frame rectangle, which intermittently reads 815 px tall instead of 768, and it only delivered the mouse while the pointer was over the picture. Fix: a 30-line patch to LisaEm's source that centres from the window's client area and, in Fill mode, clamps the pointer to the picture edge. After the patch, 4 of 4 launches were centred, the Lisa cursor stays pinned to the top and bottom edges, and it lands 2–4 px from the pointer (same as unpatched). This was tested on a virtual display only.

How the Basilisk II rate was measured: a small `LD_PRELOAD` shim counted calls to `SDL_RenderPresent` per second while injected mouse motion circled on the guest, on a scratch copy of the disk image so the real one was untouched. The numbers are presents per second, not a measure of perceived smoothness.

## How each emulator behaves now (reported)

| Emulator | My report |
|---|---|
| Basilisk II (System 7.5.3) | "System 7 looked great" after `frameskip 1` and the 1024 × 768 output |
| Mini vMac (System 6) | "seems better" at 1024 × 768 |
| Previous (NeXTSTEP 3.3) | "working well" |
| LisaEm (Lisa Office System 3.1) | Fill mode displays correctly with `hidpi_scale=100`. It still feels less smooth than I'd like, and I plan to work on the software side soon. |
| LinApple (Apple II) | launches, and F12 closes it (checked 2026-11-25); not otherwise assessed |
| GSplus (Apple IIgs, GS/OS) | boots to the Finder fullscreen at 1024 × 768; mouse and keyboard work; F12 closes it (2026-11-25). No speaker fitted, so sound is untested |

These are impressions, not benchmark scores.

## Not verified

- **Panel and controller.** The kit is linked above. The shim sizes used in this build and the controller's scaling behaviour at 1024 × 768 are still undocumented.
- **Thermal and power.** `throttled=0x0` was read during light use only. There is no sustained-load test with the case closed, and the 5 V supply module has not been checked against a heavy load. Pi 5 cooler clearance is still unchecked (see `KNOWN_ISSUES.md`).
- **Speedometer.** A guest disk image includes Speedometer 4.02, but no scores were obtained. The one run, driven with synthetic mouse input, left the guest unresponsive for over a minute while the emulation thread was idle; the cause is unknown and may have been the test harness.
- **The LisaEm centring and pointer patch.** The measurements above were on a virtual 1024 × 768 display. I later built and ran the patch from the `pi4-lisa-fixes` branch on this Pi 5 with the iPad 3/4 panel and confirmed Fill mode. I did **not** re-check the pointer at the top and bottom picture edges, Fit to Window, or clicks in the margins.
- **75 Hz, Previous at native, and the kernel `video=` route** were not tested on this build.
- **Pi 4 and LinApple, elsewhere.** On 2026-11-23 I ran the `lisa-mini-pi` setup from a blank card on a separate 2 GB Pi 4 (Raspberry Pi OS Lite, on the bench, not in this case or on this panel). All five systems, LinApple included, launched and worked. A Lisa disk image that had already been installed elsewhere needed its hardware identity copied over (LisaEm Error 10738): see the `lisa-mini-pi` docs. That says nothing about a Pi 4 in this case.
- **LisaEm speed menu.** On a Pi 4, changing the emulated CPU speed from the menu can freeze the window for a while before it recovers. I saw it on both the old and the merged builds and don't know the cause. I did not measure it on the Pi 5.

## Reading the same numbers on your own build

All read-only:

```
vcgencmd get_throttled ; vcgencmd measure_temp     # 0x0 = no throttling or undervoltage seen
xrandr ; kmsprint                                    # output name, mode, refresh
cat /sys/class/drm/card*-HDMI-A-*/modes              # modes the panel advertises (from its EDID)
dd if=<image> of=/dev/null bs=1M count=256 iflag=direct   # raw card read speed
```
