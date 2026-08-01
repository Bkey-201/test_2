
"""
Реструктуризация COCO-датасета с авто-поиском расширений и гибкими путями.
"""

import json
import os
import shutil
import argparse
from collections import defaultdict

EXTENSIONS = ['.jpg', '.png', '.jpeg', '.JPG', '.PNG', '.JPEG']

def find_file(base_dir, base_name_without_ext):
    """
    Ищет файл с именем base_name_without_ext + любое расширение из EXTENSIONS.
    Сначала в base_dir, затем в текущей папке (если base_dir отличается).
    Возвращает (полный_путь, расширение) или (None, None).
    """
    # Пробуем в указанной папке
    for ext in EXTENSIONS:
        path = os.path.join(base_dir, base_name_without_ext + ext)
        if os.path.exists(path):
            return path, ext
    # Если не нашли, пробуем в текущей папке (на случай, если файлы не в подпапке)
    for ext in EXTENSIONS:
        path = base_name_without_ext + ext
        if os.path.exists(path):
            return path, ext
    return None, None

def load_coco(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_coco(data, json_path):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_json', default='instances_train.json')
    parser.add_argument('--image_dir', default='images',
                        help='Папка, где лежат изображения (может быть "." для текущей)')
    parser.add_argument('--output_json', default='updated_annotations.json')
    args = parser.parse_args()

    coco = load_coco(args.input_json)
    images = coco['images']
    annotations = coco['annotations']
    categories = coco['categories']

    cat_id_to_name = {cat['id']: cat['name'] for cat in categories}
    anns_by_image = defaultdict(list)
    for ann in annotations:
        anns_by_image[ann['image_id']].append(ann)

    updated_images = []

    for img in images:
        img_id = img['id']
        img_file = img['file_name']  # например, "1.png" или "sub/1.png"
        old_path = os.path.join(args.image_dir, img_file)

        # Определяем классы
        classes = set()
        for ann in anns_by_image.get(img_id, []):
            cat_id = ann['category_id']
            if cat_id in cat_id_to_name:
                classes.add(cat_id_to_name[cat_id])

        folder = 'empty'
        if classes:
            folder = list(classes)[0] if len(classes) == 1 else '_'.join(sorted(classes))

        base_name = os.path.basename(img_file)
        base_without_ext = os.path.splitext(base_name)[0]
        # Сохраняем относительную подпапку, если есть
        dir_part = os.path.dirname(img_file)  # может быть "sub" или пусто

        # Пытаемся найти файл
        found_path, found_ext = None, None
        if os.path.exists(old_path):
            found_path = old_path
            found_ext = os.path.splitext(old_path)[1]
        else:
            # Ищем в папке, указанной в --image_dir
            # Если в img_file есть подпапка, то ищем внутри неё
            search_dir = os.path.join(args.image_dir, dir_part) if dir_part else args.image_dir
            found_path, found_ext = find_file(search_dir, base_without_ext)
            # Если не нашли, пробуем искать просто в args.image_dir (без подпапки)
            if not found_path:
                found_path, found_ext = find_file(args.image_dir, base_without_ext)

        if not found_path:
            print(f"Предупреждение: файл {old_path} не найден, пропускаем")
            updated_images.append(img)  # оставляем как есть, но не перемещаем
            continue

        # Определяем новый путь с папкой класса
        new_base = base_without_ext + found_ext
        # Если был dir_part, сохраняем его? Нет, мы перемещаем в images/<folder>/new_base
        new_file = os.path.join(folder, new_base)
        new_path = os.path.join(args.image_dir, new_file)

        os.makedirs(os.path.dirname(new_path), exist_ok=True)

        shutil.move(found_path, new_path)
        print(f"Перемещён: {found_path} -> {new_path}")

        img['file_name'] = new_file
        updated_images.append(img)

    coco['images'] = updated_images
    save_coco(coco, args.output_json)
    print(f"Обновлённый JSON сохранён в {args.output_json}")

if __name__ == '__main__':
    main()
