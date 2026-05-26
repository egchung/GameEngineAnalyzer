import os
p = r'D:\EG_dev\20260520_enginecheck\src\enginecheck.py'
with open(p, 'rb') as f:
    data = f.read()
text = data.decode('utf-8')
marker = 'if __name__ == "__main__":'
pos = text.find(marker)
if pos == -1:
    print('MARKER_NOT_FOUND')
    raise SystemExit(2)
# detect newline
nl = '\r\n' if '\r\n' in text else '\n'
new_block = (
    marker + nl +
    '    try:' + nl +
    '        main()' + nl +
    '    finally:' + nl +
    "        # When running as a bundled executable (PyInstaller) on Windows," + nl +
    "        # pause and wait for any key so the console window doesn't close immediately." + nl +
    '        if os.name == "nt" and getattr(sys, "frozen", False):' + nl +
    '            try:' + nl +
    '                import msvcrt' + nl +
    '                print("' + nl + 'Press any key to exit...")' + nl +
    '                msvcrt.getch()' + nl +
    '            except Exception:' + nl +
    '                pass' + nl
)
new_text = text[:pos] + new_block
with open(p, 'w', encoding='utf-8') as f:
    f.write(new_text)
print('OK')
