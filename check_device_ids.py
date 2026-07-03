import hid

for device in hid.enumerate():
  print(f'{device['vendor_id']:04x} {device['product_id']:04x} {device['product_string']}')
