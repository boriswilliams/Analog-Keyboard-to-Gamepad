# Analog Keyboard to Gamepad

Turns the analog (Hall effect) key travel of an Aula Win 60 HE keyboard into a virtual Xbox 360 controller joystick, so games like Trackmania get smooth analog steering from `A` / `D`.

The keyboard sends its key travel as raw HID reports. These scripts read those reports and feed them into a virtual gamepad through [vgamepad](https://github.com/yannbouteiller/vgamepad).

## Requirements

- Windows (the device path format and vgamepad's ViGEmBus driver are Windows-only)
- Python 3.12+
- [ViGEmBus](https://github.com/nefarius/ViGEmBus/releases) (the vgamepad installer normally sets this up)
- Python packages:

  ```
  pip install hidapi vgamepad
  ```

  `tools/decoder.py` also needs `pip install PyQt6 pyqtgraph`.

Run every command from the repository root with `python -m`.

## 1. Put the keyboard into analog reporting mode

The keyboard only streams key travel data after the Aula software asks it to. Do this every time the keyboard is plugged in or the PC restarts:

1. Open [hed.aulacn.com](https://hed.aulacn.com) in Chrome or Edge and connect the keyboard.
2. Open the **Actuation** tab at the bottom left.
2. Enable the **Travel Test**.
3. Close the tab or browser to exit the software.

## 2. Find the device path

The keyboard exposes several HID interfaces and only one of them carries the travel reports. To find it:

```
python -m tools.find_path
```

It tries each interface that matches `VENDOR_ID` / `PRODUCT_ID` in `values.py` and stops at the first one that returns data.

Spam keyboard inputs to ensure that the script can pick up each attempt, when it can it will print a green success message.

Copy that raw string into `PATH` in `values.py`:

```python
PATH = b'\\\\?\\HID#VID_2E3C&PID_C365&MI_02#a&778027b&0&0000#{4d1e55b2-f16f-11cf-88cb-001111000030}'
```

The path usually stays the same until you plug the keyboard into a different USB port.

If `find_path` finds nothing, check that step 1 was done. If you have a different keyboard, run `python -m tools.check_device_ids` to list the vendor and product IDs of connected HID devices and update `VENDOR_ID` / `PRODUCT_ID` in `values.py`.

## 3. Play Trackmania

```
python -m trackmania
```

`A` and `D` now drive the left stick of a virtual Xbox 360 controller. Set steering to the controller in Trackmania's input settings. Stop with `Ctrl+C`.

Tuning constants at the top of `trackmania.py`:

| Constant | Meaning |
| --- | --- |
| `DEADZONE` | Fraction of stick travel skipped at the start, so a light press already registers |
| `CURVE_COEFFICIENT` | Response curve; above `1` gives finer control near the centre |
| `MAX_IN` | Raw travel value of a fully pressed key |
| `MAX_JS` | Maximum joystick value to map to |

To check the virtual controller is working, open `joy.cpl` (Win+R) and watch the X axis move as you press `A` / `D`.

## Other scripts

| Script | What it does |
| --- | --- |
| `he_controller_bridge.py` | The full version that `trackmania.py` was trimmed down from. Adds a live terminal readout (poll rate, per-key travel, stick values, raw report bytes) and optional `W` / `S` on the stick's Y axis (`WASD = True`). Useful for testing and tuning; set `SHOW_PRINT = False` to hide the readout. |
| `tools/decoder.py` | Live bar chart of all 64 bytes of each report. Useful for working out which bytes change when a key is pressed. |
| `tools/check_device_ids.py` | Lists vendor ID, product ID and name of every connected HID device. |
| `tools/hex_dump_to_array.py` | Converts a Wireshark hex dump into a Python byte list (used to produce `WAKE` in `values.py`). |

## Report format

Each 64-byte report describes one key:

- bytes `7` and `8` identify the key: `(2, 2)` = W, `(3, 2)` = A, `(3, 3)` = S, `(3, 4)` = D
- bytes `9` and `10` are the travel: `report[10] * 255 + report[9]`, from `0` up to `339` when fully pressed

## Notes

- `WAKE` in `values.py` is a packet captured from the Aula software that was meant to switch the keyboard into analog mode without the website. Sending it is currently disabled in `shared/connect.py`, this method has proved inconsistent.
- `docs/` has notes on capturing the Aula software's USB traffic (browser console hooks, Wireshark filters).
