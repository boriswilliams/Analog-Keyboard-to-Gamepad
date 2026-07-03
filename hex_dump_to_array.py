HEX_DUMP = '''
0000   1b 00 e0 65 80 25 8f a0 ff ff 00 00 00 00 09 00
0010   01 01 00 10 00 04 01 00 00 00 00
'''

results = []

for line in HEX_DUMP.split('\n')[1:-1]:
  for byte in line[7:].split(' '):
    results.append(f'0x{byte}')

print(', '.join(results))
