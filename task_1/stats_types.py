import sys
import os
import xml.etree.ElementTree as ET
from collections import Counter

DEFAULT_FILES = ['annotations.xml', 'annotations-2.xml', 'annotations-3.xml']

def main(files):
    type_counter = Counter()
    for f in files:
        if not os.path.isfile(f):
            print(f"Предупреждение: файл {f} не найден, пропускаем", file=sys.stderr)
            continue
        tree = ET.parse(f)
        root = tree.getroot()
        for img in root.findall('image'):
            for shape_tag in ('box', 'polygon', 'points'):
                shapes = img.findall(shape_tag)
                if shapes:
                    type_counter[shape_tag] += len(shapes)

    for t in ('box', 'polygon', 'points'):
        print(f"{t}: {type_counter.get(t, 0)}")

if __name__ == '__main__':
    files = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_FILES
    main(files)