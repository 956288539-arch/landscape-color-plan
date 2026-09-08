"""Read source PSD composition dependencies without modifying the source files."""
from pathlib import Path
import argparse
from collections import Counter
import gc
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'work/vendor'))
import attrs
from psd_tools import PSDImage
from psd_tools.api.layers import AdjustmentLayer
from psd_tools.constants import Resource


def plain(value):
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, bytes):
        return value.decode('latin1')
    if hasattr(value, 'items'):
        return {str(plain(k)): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if attrs.has(type(value)):
        return {a.name: plain(getattr(value, a.name)) for a in attrs.fields(type(value))}
    if hasattr(value, 'value'):
        return plain(value.value)
    return repr(value)


def audit_source(source):
    path = Path(source['path'])
    if not path.is_absolute():
        path = ROOT/path
    with path.open('rb') as stream:
        sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    if sha != source['sha256']:
        raise ValueError(f"Source changed; review registration first: {path}")
    psd = PSDImage.open(path)
    rows = []
    patterns = {}

    def walk(parent, indices=(), parent_ids=()):
        base_id = None
        for i, layer in enumerate(parent):
            index = indices+(i,)
            if not layer.clipping:
                base_id = layer.layer_id
            effects = layer.effects
            effect_rows = []
            for effect in effects:
                entry = {'type': type(effect).__name__, 'enabled': effect.enabled,
                         'active_in_saved_composite': bool(layer.is_visible() and effects.enabled and effect.enabled),
                         'descriptor': plain(effect.descriptor)}
                for key in ('opacity', 'angle', 'distance', 'size', 'use_global_light', 'blend_mode'):
                    if hasattr(effect, key):
                        entry[key] = plain(getattr(effect, key))
                pattern_descriptor = effect.descriptor.get(b'Ptrn')
                if pattern_descriptor is not None:
                    pattern_id = pattern_descriptor.get(b'Idnt').value.rstrip('\x00')
                    if pattern_id not in patterns:
                        pattern = psd._get_pattern(pattern_id)
                        patterns[pattern_id] = {
                            'id': pattern_id, 'name': pattern_descriptor.get(b'Nm  ').value.rstrip('\x00'),
                            'embedded': pattern is not None,
                            'declared_size': list(pattern.point) if pattern is not None else None,
                            'serialized_sha256': hashlib.sha256(pattern.tobytes()).hexdigest() if pattern is not None else None}
                    entry['pattern_resource_id'] = pattern_id
                effect_rows.append(entry)
            mask = None
            if layer.has_mask():
                m = layer.mask
                mask = {'bbox': list(m.bbox), 'disabled': m.disabled,
                        'background_color': m.background_color, 'parameters': plain(m.parameters)}
                pixels = m.topil()
                if pixels is not None:
                    hist = pixels.convert('L').histogram()
                    total = sum(hist)
                    mask['stored_pixel_range'] = list(pixels.convert('L').getextrema())
                    mask['stored_nonwhite_share'] = round((total-hist[255])/total, 6)
                    mask['stored_soft_value_share'] = round(sum(hist[1:255])/total, 6)
                    del pixels
            row = {'index': list(index), 'layer_id': layer.layer_id, 'name': layer.name,
                   'parent_layer_ids': list(parent_ids), 'kind': layer.kind,
                   'visible': layer.visible, 'effective_visible': layer.is_visible(),
                   'opacity_pct': round(layer.opacity/255*100, 3),
                   'fill_opacity_pct': round(layer.fill_opacity/255*100, 3),
                   'blend_mode': plain(layer.blend_mode.value), 'bbox': list(layer.bbox),
                   'clipping': layer.clipping,
                   'clipping_base_layer_id': base_id if layer.clipping else None,
                   'clip_layer_ids': [c.layer_id for c in layer.clip_layers],
                   'mask': mask, 'has_vector_mask': layer.has_vector_mask(),
                   'effects_master_enabled': effects.enabled,
                   'effects_scale_pct': effects.scale if len(effects) else None, 'effects': effect_rows}
            if isinstance(layer, AdjustmentLayer):
                row['adjustment_data'] = plain(layer._data)
            rows.append(row)
            if layer.is_group():
                walk(layer, index, parent_ids+(layer.layer_id,))
    walk(psd)
    active = [r for r in rows if r['effective_visible']]
    receipt = {'source_id': source['id'], 'source_path': str(path), 'source_sha256': sha,
               'canvas': list(psd.size), 'index_order': 'psd-tools, zero-based, bottom-to-top',
               'global_angle': plain(psd.image_resources.get_data(Resource.GLOBAL_ANGLE)),
               'patterns': list(patterns.values()),
               'summary': {'layers_and_groups': len(rows), 'effective_visible': len(active),
                           'visible_adjustments': sum('adjustment_data' in r for r in active),
                           'visible_clipped_layers': sum(r['clipping'] for r in active),
                           'visible_masked_layers': sum(r['mask'] is not None for r in active),
                           'active_effects': dict(Counter(e['type'] for r in rows for e in r['effects'] if e['active_in_saved_composite'])),
                           'visible_non_normal_blends': dict(Counter(r['blend_mode'] for r in active if r['blend_mode'] not in ('norm', 'pass')))},
               'layers': rows}
    del psd
    gc.collect()
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', choices=['rural', 'residential', 'landscape', 'park'])
    parser.add_argument('--output', type=Path, required=True, help='New JSON path; existing audit is not overwritten')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output already exists; choose a new audit path.')
    sources = json.loads((ROOT/'library/sources.json').read_text('utf-8'))
    result = {'schema': 'landscape-source-composition/v1',
              'scope': 'Saved PSD structure, settings and mask pixels. Not an editing-history reconstruction.', 'sources': []}
    for source in sources:
        if args.source and source['id'] != args.source:
            continue
        receipt = audit_source(source)
        result['sources'].append(receipt)
        print(json.dumps({'source': source['id'], **receipt['summary']}, ensure_ascii=False), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    print(str(args.output.resolve()), flush=True)


if __name__ == '__main__':
    main()
