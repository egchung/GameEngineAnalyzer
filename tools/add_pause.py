import os
import sys
p = os.path.join(r'D:\EG_dev\20260520_enginecheck\src', 'enginecheck.py')
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()
old = 'if __name__ == "__main__":\n    main()\n'
new = ('if __name__ == "__main__":\n'
       '    try:\n'
       '        main()\n'
       '    finally:\n'
       '        # When running as a bundled executable (PyInstaller) on Windows,\n'
       '        # pause and wait for any key so the console window doesn\'t close immediately.\n'
       '        if os.name == "nt" and getattr(sys, "frozen", False):\n'
       '            try:\n'
       '                import msvcrt\n'
       '                print("\\nPress any key to exit...")\n'
       '                msvcrt.getch()\n'
       '            except Exception:\n'
       '                pass\n')
if old not in s:
    print('OLD_NOT_FOUND')
    sys.exit(2)
s = s.replace(old, new, 1)
with open(p, 'w', encoding='utf-8') as f:
    f.write(s)
print('OK')
