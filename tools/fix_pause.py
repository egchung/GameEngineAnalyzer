p = r'D:\EG_dev\20260520_enginecheck\src\enginecheck.py'
with open(p, 'r', encoding='utf-8') as f:
    txt = f.read()
needle = 'Press any key to exit...'
idx = txt.find(needle)
if idx == -1:
    print('NOT_FOUND')
    raise SystemExit(2)
# find the start of the print( before the needle
start = txt.rfind('print', 0, idx)
if start == -1:
    print('PRINT_NOT_FOUND')
    raise SystemExit(3)
# find the end paren after needle
end = txt.find(')', idx)
if end == -1:
    print('END_NOT_FOUND')
    raise SystemExit(4)
# build replacement preserving indentation
line_start = txt.rfind('\n', 0, start) + 1
indent = txt[line_start:start]
replacement = indent + 'print("\\nPress any key to exit...")'
newtxt = txt[:line_start] + replacement + txt[end+1:]
with open(p, 'w', encoding='utf-8') as f:
    f.write(newtxt)
print('OK')
