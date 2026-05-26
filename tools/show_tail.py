import os
p = r'D:\EG_dev\20260520_enginecheck\src\enginecheck.py'
with open(p, 'rb') as f:
    data = f.read()
print(repr(data[-200:]))
print('\n--- TEXT ---\n')
print(data[-200:].decode('utf-8', errors='replace'))
