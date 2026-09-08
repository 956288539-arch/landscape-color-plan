"""Produce a scale hierarchy proposal; never edit a drawing or place assets."""
from pathlib import Path
import argparse
import json
import math
import random
import sys


def quantile(values, fraction):
    values = sorted(values)
    pos = (len(values) - 1) * fraction
    lo = math.floor(pos)
    hi = math.ceil(pos)
    return values[lo] * (hi - pos) + values[hi] * (pos - lo) if hi != lo else values[lo]


def make_recipe(config, count, medium_crown_px, mode='natural', seed=0):
    if count < 1 or not math.isfinite(medium_crown_px) or medium_crown_px <= 0:
        raise ValueError('数量须为正整数，中型冠幅须为有限正数；单位是本图像素。')
    rng = random.Random(seed)
    if mode == 'formal':
        classes = [{'id': 'formal', 'role': '目标设计确定的规则序列',
                    'relative_crown_range': config['tree']['formal_relative_crown_range'], 'count_share': 1}]
    elif mode == 'natural':
        classes = config['tree']['natural_classes']
    else:
        raise ValueError('mode must be natural or formal')
    weights = [c['count_share'] for c in classes]
    if any(not math.isfinite(w) or w < 0 for w in weights) or not math.isclose(sum(weights), 1):
        raise ValueError('树冠数量占比必须非负且合计为 1。')
    for c in classes:
        low, high = c['relative_crown_range']
        if not (math.isfinite(low) and math.isfinite(high) and 0 < low <= high):
            raise ValueError('冠幅范围必须为有限正数且有序。')
    ideal = [count * w for w in weights]
    counts = [math.floor(n) for n in ideal]
    for i in sorted(range(len(classes)), key=lambda i: ideal[i] - counts[i], reverse=True)[:count-sum(counts)]:
        counts[i] += 1
    crowns = []
    for c, n in zip(classes, counts):
        for _ in range(n):
            factor = rng.uniform(*c['relative_crown_range'])
            width = medium_crown_px * factor
            if not math.isfinite(width) or width <= 0:
                raise ValueError('冠幅超出可表示范围，请按本图像素输入。')
            crowns.append({'size_class': c['id'], 'role': c['role'],
                           'relative_crown': round(factor, 4),
                           'target_visible_crown_px': float(format(width, '.8g'))})
    rng.shuffle(crowns)
    factors = [c['relative_crown'] for c in crowns]
    ratio = quantile(factors, .9) / quantile(factors, .1)
    applicable = mode == 'natural' and count >= config['tree']['diagnostic_min_sample']
    return {
        'schema': 'landscape-visual-recipe/v1', 'composition_version': config['version'],
        'mode': mode, 'seed': seed, 'medium_visible_crown_px': medium_crown_px,
        'class_counts': {c['id']: n for c, n in zip(classes, counts)}, 'crowns': crowns,
        'scale_diagnostic': {'p90_p10': round(ratio, 4), 'applicable': applicable,
                             'review_suggested': applicable and ratio < config['tree']['natural_p90_p10_review_below']},
        'grass': config['grass'], 'visual_review': config['review'],
        'street_tree_guidance': config['tree'].get('street', {}),
        'geometry_status': 'unplaced',
        'next_step': '结合本图角色安排树群与位置，核对素材有效像素、目标设计及边界；真实试铺后检查缩略图。'
    }


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description='生成树冠三档尺度与草坪色阶起调计划；不修改图像、不布置树位。')
    parser.add_argument('--library-root', type=Path, help='覆盖本机素材库位置')
    parser.add_argument('--count', type=int, required=True)
    parser.add_argument('--medium-crown-px', type=float, required=True, help='本图确定的中型可见冠幅，像素')
    parser.add_argument('--mode', choices=['natural', 'formal'], default='natural',
                        help='natural 为自然树群；formal 仅用于已确认的统一规格树阵。普通街树需另按路段指南组织。')
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--output', type=Path, help='新 JSON 路径；已有文件不覆盖，省略则写 stdout')
    args = parser.parse_args()
    config_path = Path(__file__).resolve().parents[1]/'references/local-library.json'
    location = json.loads(config_path.read_text('utf-8'))
    library = Path(location['library_root'])
    if not library.is_absolute():
        library = config_path.parent/library
    library = (args.library_root or library).resolve()
    config = json.loads((library/location['composition']).read_text('utf-8'))
    try:
        recipe = make_recipe(config, args.count, args.medium_crown_px, args.mode, args.seed)
    except ValueError as exc:
        parser.error(str(exc))
    result = json.dumps(recipe, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(result+'\n')
        print(str(args.output.resolve()))
    else:
        print(result)


if __name__ == '__main__':
    main()
