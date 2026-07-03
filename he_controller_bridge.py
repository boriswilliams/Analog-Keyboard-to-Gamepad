import hid
import time
import vgamepad as vg

# Find your keyboard's exact hardware footprint
# You can find these in Windows Device Manager -> Details -> Hardware IDs
VENDOR_ID = 0x2e3c   # Common Aula/Algear manufacturer ID
PRODUCT_ID = 0xc365  # Change to your exact Win 60 HE product ID

OPEN_PATH = b'\\\\?\\HID#VID_2E3C&PID_C365&MI_01&Col03#7&2f14141f&0&0002#{4d1e55b2-f16f-11cf-88cb-001111000030}'

if True:
    if True:
        # Open connection directly to the keyboard's analog packet stream
        device = hid.device()
        device.open_path(OPEN_PATH)
        device.set_nonblocking(1)
        print("Connected! Win 60 HE analog data linked successfully.")
        
        # --- NEW: WAKE UP THE ANALOG STREAM ---
        # Aula/Algear firmware requires a handshake report to start streaming.
        # We send an array starting with 0x00 (Report ID) followed by initialization bytes.
        wake_up_packet = [0x00] + [0x01, 0x02, 0x00, 0x00] + [0x00]*60 
        try:
            device.send_feature_report(wake_up_packet)
            print("Wake-up packet transmitted to interface.")
        except Exception as e:
            print(f"Feature report notice: {e}. Trying standard write instead...")
            # Fallback if your specific firmware version prefers standard write endpoints:
            device.write([0x00, 0x01, 0x02] + [0x00]*61)
        # --------------------------------------

        # Initialize the virtual Xbox controller interface
        gamepad = vg.VX360Gamepad()
        
        while True:
            # Read raw reports sent from the keyboard's hall-effect sensors
            report = device.read(64)
            
            # Only run code if the keyboard actually sent a data array back
            if report and len(report) > 0:
                print(f"Raw Data Recieved: {list(report)}")
                
                # Once this prints, we will see which index numbers move when you hit A and S!
                # For now, safe-check length to prevent out-of-index errors
                if len(report) >= 5:
                    raw_left = report[3]  
                    raw_right = report[4] 
                    
                    # Convert raw magnetic depth bytes into joystick values
                    left_joystick_x = 0
                    if raw_left > 10: 
                        left_joystick_x -= int((raw_left / 255.0) * 32767)
                    if raw_right > 10:
                        left_joystick_x += int((raw_right / 255.0) * 32767)
                    
                    gamepad.left_joystick(x_value=left_joystick_x, y_value=0)
                    gamepad.update()
                
            time.sleep(0.001) # 1ms response polling loop
