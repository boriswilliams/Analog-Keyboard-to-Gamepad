import hid

VENDOR_ID = 0x2E3C
PRODUCT_ID = 0xC365

print("Scanning open Win 60 HE endpoints...")
for d in hid.enumerate():
    if d['vendor_id'] == VENDOR_ID and d['product_id'] == PRODUCT_ID:
        # Check if the device can actually be opened
        try:
            h = hid.device()
            h.open_path(d['path'])
            h.close()
            status = "🔓 OPEN / READY"
        except IOError:
            status = "🔒 LOCKED BY WINDOWS"
            
        print(f"Interface: {d['interface_number']} | Usage Page: {d['usage_page']} -> {status}")
        print(f"Path string to use: {d['path'].decode('utf-8')}")
        print("-" * 40)
