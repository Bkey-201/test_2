"""
Валидация обновлённого COCO-датасета:
- Проверяет существование всех файлов
- Проверяет целостность ссылок (image_id, category_id)
- Формирует отчёт в JSON
"""

import json
import os
import argparse
from collections import defaultdict

def load_coco(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_report(report, report_path):
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description='Валидация COCO датасета')
    parser.add_argument('--input_json', default='updated_annotations.json',
                        help='Путь к обновлённому COCO JSON')
    parser.add_argument('--image_dir', default='images',
                        help='Корневая папка с изображениями')
    parser.add_argument('--report_json', default='dataset_report.json',
                        help='Путь для сохранения отчёта')
    args = parser.parse_args()

    coco = load_coco(args.input_json)
    images = coco.get('images', [])
    annotations = coco.get('annotations', [])
    categories = coco.get('categories', [])

    image_ids = {img['id'] for img in images}
    category_ids = {cat['id'] for cat in categories}

    # Проверка существования файлов
    missing_files = []
    for img in images:
        file_path = os.path.join(args.image_dir, img['file_name'])
        if not os.path.exists(file_path):
            missing_files.append({
                'image_id': img['id'],
                'file_name': img['file_name'],
                'error': 'File not found'
            })

    # Проверка image_id в аннотациях
    invalid_image_ids = []
    ann_image_ids = {ann['image_id'] for ann in annotations}
    for ann in annotations:
        if ann['image_id'] not in image_ids:
            invalid_image_ids.append({
                'annotation_id': ann.get('id', None),
                'image_id': ann['image_id'],
                'error': 'Image id not found'
            })

    # Проверка category_id
    invalid_category_ids = []
    for ann in annotations:
        if ann['category_id'] not in category_ids:
            invalid_category_ids.append({
                'annotation_id': ann.get('id', None),
                'category_id': ann['category_id'],
                'error': 'Category id not found'
            })

    # Подсчёт пустых изображений (без аннотаций)
    empty_images = [img['id'] for img in images if img['id'] not in ann_image_ids]

    # Сбор ошибок
    errors = missing_files + invalid_image_ids + invalid_category_ids

    report = {
        'total_images': len(images),
        'total_annotations': len(annotations),
        'total_categories': len(categories),
        'empty_images': len(empty_images),
        'errors': errors,
        'errors_count': len(errors)
    }

    save_report(report, args.report_json)
    print(f"Отчёт сохранён в {args.report_json}")
    print(f"Найдено ошибок: {len(errors)}")

    # Вывод краткой информации
    print(f"Изображений: {len(images)}")
    print(f"Аннотаций: {len(annotations)}")
    print(f"Категорий: {len(categories)}")
    print(f"Пустых изображений: {len(empty_images)}")

if __name__ == '__main__':
    main()
