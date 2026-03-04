"""Remove UTF-8 BOM from all .md files in project (excluding .venv)."""
import os

count = 0
for root, dirs, files in os.walk('.'):
    if '.venv' in dirs:
        dirs.remove('.venv')
    if '.git' in dirs:
        dirs.remove('.git')
    for f in files:
        if f.endswith('.md'):
            path = os.path.join(root, f)
            with open(path, 'rb') as fh:
                data = fh.read()
            if data[:3] == b'\xef\xbb\xbf':
                with open(path, 'wb') as fh:
                    fh.write(data[3:])
                print(f"Removed BOM: {path}")
                count += 1
print(f"\nDone. Fixed {count} files.")
