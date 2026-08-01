import sys
import os
import xml.etree.ElementTree as ET

DEFAULT_FILES = ['annotations.xml', 'annotations-2.xml', 'annotations-3.xml']

def modify_file(input_path):
    tree = ET.parse(input_path)
    root = tree.getroot()

 
    images = root.findall('image')
    if not images:
        print(f"Нет изображений в {input_path}, копируем без изменений")
        output_path = input_path.replace('.xml', '_modified.xml')
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        return

    # Сортируем по текущему id (числовому)
    images.sort(key=lambda e: int(e.get('id', 0)))
    n = len(images)

    # Переворачиваем: первый получает n, последний - 1
    for idx, img in enumerate(images):
        new_id = n - idx
        img.set('id', str(new_id))


        old_name = img.get('name', '')
        base = os.path.basename(old_name)
        name_without_ext = os.path.splitext(base)[0]
        new_name = name_without_ext + '.png'
        img.set('name', new_name)


    output_path = input_path.replace('.xml', '_modified.xml')
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"Сохранено: {output_path}")

def main(files):
    for f in files:
        if not os.path.isfile(f):
            print(f"Предупреждение: файл {f} не найден, пропускаем", file=sys.stderr)
            continue
        modify_file(f)

if __name__ == '__main__':
    files = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_FILES
    main(files)
