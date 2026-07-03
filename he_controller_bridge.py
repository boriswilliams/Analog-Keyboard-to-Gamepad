import hid
import time
import vgamepad as vg

# Find your keyboard's exact hardware footprint
# You can find these in Windows Device Manager -> Details -> Hardware IDs
VENDOR_ID = 0x2E3C   # Common Aula/Algear manufacturer ID
PRODUCT_ID = 0xC365  # Change to your exact Win 60 HE product ID

def main():
    print("Searching for Win 60 HE hardware stream...")
    try:
        # Open connection directly to the keyboard's analog packet stream
        device = hid.device()
        device.open(VENDOR_ID, PRODUCT_ID)
        device.set_nonblocking(1)
        print("Connected! Win 60 HE analog data linked successfully.")
        
        # Initialize the virtual Xbox controller interface
        gamepad = vg.VX360Gamepad()
        
        while True:
            # Read raw reports sent from the keyboard's hall-effect sensors
            report = device.read(64)
            if report:
                # Aula reports typically store key depth values sequentially.
                # Assuming index 3 is your 'A' depth and index 4 is 'D' or 'S'
                # Raw depths usually scale from 0 (untouched) to 255 (bottomed out)
                raw_left = report[3]  
                raw_right = report[4] 
                
                # Convert raw magnetic depth bytes into joystick values (-32768 to 32767)
                left_joystick_x = 0
                if raw_left > 10: # Deadzone buffer
                    left_joystick_x -= int((raw_left / 255.0) * 32767)
                if raw_right > 10:
                    left_joystick_x += int((raw_right / 255.0) * 32767)
                
                # Update the virtual joystick positioning instantly
                gamepad.left_joystick(x_value=left_joystick_x, y_value=0)
                gamepad.update()
                
            time.sleep(0.001) # 1ms response polling loop (1000Hz)

    except Exception as e:
        print(f"Error handling device: {e}")
        print("Ensure the web driver page is closed so it isn't locking the USB port.")

if __name__ == "__main__":
    main()
