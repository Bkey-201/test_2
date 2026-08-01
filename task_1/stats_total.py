import sys
import os
import xml.etree.ElementTree as ET

DEFAULT_FILES = ['annotations.xml', 'annotations-2.xml', 'annotations-3.xml']

def parse_images(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    images = []
    for img in root.findall('image'):
        img_id = img.get('id')
        name = img.get('name', '')
        width = int(img.get('width', 0))
        height = int(img.get('height', 0))
        shapes = []
        for shape_tag in ('box', 'polygon', 'points'):
            shapes.extend(img.findall(shape_tag))
        images.append({
            'id': img_id,
            'name': name,
            'width': width,
            'height': height,
            'shapes': shapes,
            'area': width * height
        })
    return images

def main(files):
    all_images = []
    for f in files:
        if not os.path.isfile(f):
            print(f"Предупреждение: файл {f} не найден, пропускаем", file=sys.stderr)
            continue
        all_images.extend(parse_images(f))

    total = len(all_images)
    labeled = sum(1 for img in all_images if img['shapes'])
    unlabeled = total - labeled
    total_shapes = sum(len(img['shapes']) for img in all_images)

    print(f"Общее количество изображений: {total}")
    print(f"Размеченных: {labeled}")
    print(f"Неразмеченных: {unlabeled}")
    print(f"Всего фигур: {total_shapes}\n")

    if total == 0:
        return

    max_area = max(img['area'] for img in all_images)
    min_area = min(img['area'] for img in all_images)

    max_images = [img for img in all_images if img['area'] == max_area]
    min_images = [img for img in all_images if img['area'] == min_area]

    ex_max = max_images[0]
    ex_min = min_images[0]

    print(f"Самое большое изображение (площадь {ex_max['width']}x{ex_max['height']}):")
    print(f"  Название: {ex_max['name']}")
    print(f"  Количество таких же: {len(max_images)}\n")

    print(f"Самое маленькое изображение (площадь {ex_min['width']}x{ex_min['height']}):")
    print(f"  Название: {ex_min['name']}")
    print(f"  Количество таких же: {len(min_images)}")

if __name__ == '__main__':
    files = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_FILES
    main(files)