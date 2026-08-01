"""
Преобразование COCO-аннотаций в формат YOLO.
Использует структуру папок из скрипта restructure_coco.
"""

import json
import os
import shutil
import argparse
from collections import defaultdict

def load_coco(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description='Преобразование COCO в YOLO')
    parser.add_argument('--input_json', default='updated_annotations.json',
                        help='Путь к обновлённому COCO JSON')
    parser.add_argument('--image_dir', default='images',
                        help='Корневая папка с изображениями (структура из скрипта 1)')
    parser.add_argument('--output_dir', default='yolo_dataset',
                        help='Папка для сохранения YOLO-датасета')
    args = parser.parse_args()

    coco = load_coco(args.input_json)
    images = coco['images']
    annotations = coco['annotations']
    categories = coco['categories']

    # Создаём словарь category_id -> индекс (порядковый номер в categories)
    # Сортируем категории по id для стабильности
    categories_sorted = sorted(categories, key=lambda x: x['id'])
    cat_id_to_idx = {cat['id']: idx for idx, cat in enumerate(categories_sorted)}

    # Группируем аннотации по image_id
    anns_by_image = defaultdict(list)
    for ann in annotations:
        anns_by_image[ann['image_id']].append(ann)

    # Создаём словарь изображений по id
    images_by_id = {img['id']: img for img in images}

    # Создаём выходную папку
    os.makedirs(args.output_dir, exist_ok=True)

    # Обрабатываем каждое изображение
    for img in images:
        img_id = img['id']
        file_name = img['file_name']  # например, "car_dog/image.jpg"
        width = img['width']
        height = img['height']

        # Путь к исходному изображению
        src_path = os.path.join(args.image_dir, file_name)
        if not os.path.exists(src_path):
            print(f"Предупреждение: {src_path} не найден, пропускаем")
            continue

        # Определяем подпапку (первая часть пути)
        subfolder = os.path.dirname(file_name)  # например, "car_dog"
        dest_subfolder = os.path.join(args.output_dir, subfolder)
        os.makedirs(dest_subfolder, exist_ok=True)

        # Копируем изображение
        dest_img = os.path.join(dest_subfolder, os.path.basename(file_name))
        shutil.copy2(src_path, dest_img)
        print(f"Скопировано: {src_path} -> {dest_img}")

        # Создаём YOLO-аннотацию
        ann_list = anns_by_image.get(img_id, [])
        txt_path = os.path.join(dest_subfolder, os.path.splitext(os.path.basename(file_name))[0] + '.txt')

        with open(txt_path, 'w') as f:
            for ann in ann_list:
                cat_idx = cat_id_to_idx.get(ann['category_id'])
                if cat_idx is None:
                    print(f"Предупреждение: category_id {ann['category_id']} не найден, пропускаем аннотацию {ann.get('id')}")
                    continue

                bbox = ann['bbox']  # [x, y, width, height]
                x, y, w, h = bbox
                # Нормализация
                x_center = (x + w / 2) / width
                y_center = (y + h / 2) / height
                box_w = w / width
                box_h = h / height

                # Ограничим значения (на случай выхода за границы)
                x_center = max(0.0, min(1.0, x_center))
                y_center = max(0.0, min(1.0, y_center))
                box_w = max(0.0, min(1.0, box_w))
                box_h = max(0.0, min(1.0, box_h))

                f.write(f"{cat_idx} {x_center:.6f} {y_center:.6f} {box_w:.6f} {box_h:.6f}\n")

        print(f"Создан {txt_path}")

    print("Преобразование завершено.")

if __name__ == '__main__':
    main()
