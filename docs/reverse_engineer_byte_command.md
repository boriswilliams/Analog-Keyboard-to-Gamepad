To reverse engineer the exact byte command your web driver uses to wake up the keyboard, you need to capture the USB traffic while the browser talks to the keyboard. Because the driver runs in a web browser using WebHID, you can use built-in browser developer tools or a dedicated USB packet sniffer to intercept the exact hex values being sent down the wire.Here are the two best ways to sniff out the wake-up command.

## Method 1: The Browser Console (Easiest Method)

Since your Aula software runs entirely inside Google Chrome or Microsoft Edge via the WebHID API, the browser handles the USB connection. You can intercept the raw data by overriding the browser's built-in `HIDDevice.prototype.sendFeatureReport` or `HIDDevice.prototype.write` functions via the Developer Console.

1. Close the Aula web software tab completely.
2. Open a fresh, empty tab in Chrome or Edge and press **F12** (or `Ctrl + Shift + I`) to open **Developer Tools**.
3. Click on the **Console** tab.
4. Paste the following snippet into the console and hit **Enter**. This script creates a hook that forces the browser to print every single byte array it transmits to a USB device:
    ### javascript
    ```
    (function() {
        const originalSend = HIDDevice.prototype.sendFeatureReport;
        const originalWrite = HIDDevice.prototype.write;

        HIDDevice.prototype.sendFeatureReport = function(reportId, data) {
            console.log(`%c[Feature Report] ID: 0x${reportId.toString(16).padStart(2, '0')}`, "color: #00ff00; font-weight: bold;");
            console.log("Bytes Sent:", Array.from(new Uint8Array(data.buffer || data)));
            return originalSend.apply(this, arguments);
        };

        HIDDevice.prototype.write = function(reportId, data) {
            console.log(`%c[Standard Write] ID: 0x${reportId.toString(16).padStart(2, '0')}`, "color: #00ffff; font-weight: bold;");
            console.log("Bytes Sent:", Array.from(new Uint8Array(data.buffer || data)));
            return originalWrite.apply(this, arguments);
        };
        
        console.log("USB Interceptor Active! Waiting for keyboard connection...");
    })();
    ```
5. In that same browser window, navigate to your Aula Web Driver URL.
6. Click the "**Connect**" button in the web application and pair your Win 60 HE.
7. Look back at your Developer Tools console. You will see a flood of green and blue logs. The very first 2 or 3 lines that appear the exact moment you hit connect are your **wake-up packets**. Note down those arrays of numbers.

## Method 2: Wireshark with USBPcap (Advanced Method)

If the web app uses a compiled WebAssembly module that hides its low-level calls from JavaScript hooks, you can sniff the hardware packets at the Windows kernel level using the open-source tool Wireshark.

1. Download and install **Wireshark**. Make sure you check the box during installation to install **USBPcap** (the USB packet capture driver).
2. Restart your PC to allow the USBPcap driver to initialize.
3. Open Wireshark. You will see a list of network interfaces, along with names like `USBPcap1`, `USBPcap2`, etc.
4. To find which USBPcap interface your keyboard is on, open your command prompt and run your `scan_keyboard.py` script from earlier. Look at the path string it printed:
    - Example: `\\?\HID#VID_2E3C&PID_C365&...`
    - Open Windows Device Manager, find your keyboard, go to **Properties** -> **Details** -> **Location paths**. It will show you which root USB Hub it is plugged into (e.g., Hub 1 corresponds to `USBPcap1`).
5. Double-click the correct `USBPcap` interface in Wireshark to start capturing.
6. To filter out all other USB noise (like your mouse), type this into the Wireshark display filter bar at the top and hit Enter:
    ### text
    ```
    usb.idVendor == 0x2e3c && usb.idProduct == 0xc365
    ```
7. Open your Aula web driver page and click **Connect**.
8. In Wireshark, look for packets where the "Info" column says `SET_REPORT Request` or `URB_INTERRUPT out`.
9. Click on that packet, expand the **Setup Data** or **Leftover Capture Data** tab in the bottom panel, and you will see the exact hex string sent to the keyboard.

## How to use the discovered bytes in your Python script

Once you find the sequence (for example, if the browser console prints `[10, 1, 5, 0, 0...]`), you plug those exact numbers directly into your `he_controller_bridge.py` script:

### python
```
# If the report ID was 0x00, put 0x00 first.
wake_up_packet = [0x00] + [10, 1, 5, 0, 0] + [0x00]*59 
device.send_feature_report(wake_up_packet)
```
With the authentic handshake packet transmitted, the firmware will accept the command, break its silence, and begin sending the continuous analog reports directly to your Python loop.
