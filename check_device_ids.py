import hid

arr = []

for device in hid.enumerate():
  arr.append((device['product_string'], f'{device['vendor_id']:04x} {device['product_id']:04x} {device['product_string']}'))
    
arr.sort()

for i in range(len(arr)):
  if i == 0 or arr[i] != arr[i-1]:
    print(arr[i][1])
