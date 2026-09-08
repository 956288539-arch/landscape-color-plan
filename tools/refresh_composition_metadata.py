"""Attach verified PSD composition facts to existing asset records; keep asset pixels."""
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parent.parent


def refresh():
    folder = ROOT/'library'
    data = json.loads((folder/'asset-index.json').read_text('utf-8'))
    audit = json.loads((folder/'composition-audit.json').read_text('utf-8'))
    sources = {s['id']: s for s in json.loads((folder/'sources.json').read_text('utf-8'))}
    by_source = {}
    for source in audit['sources']:
        assert source['source_sha256'] == sources[source['source_id']]['sha256'], 'Audit source changed'
        by_source[source['source_id']] = {r['layer_id']: r for r in source['layers']}
    for asset in data['assets']:
        if asset['kind'] == 'reference':
            continue
        rows = by_source[asset['style']]
        row = rows[asset['source_layer_id']]
        assert row['index'] == asset['source_index'], asset['id']
        assert asset['source_reference']['source_sha256'] == sources[asset['style']]['sha256'], asset['id']
        asset['source_fill_opacity_pct'] = row['fill_opacity_pct']
        asset['fill_opacity_baked'] = False
        asset['source_effects_master_enabled'] = row['effects_master_enabled']
        asset['source_effects'] = [{k: v for k, v in e.items() if k != 'descriptor'} for e in row['effects']]
        asset['source_parent_opacities'] = [
            {'layer_id': pid, 'name': rows[pid]['name'], 'opacity_pct': rows[pid]['opacity_pct'],
             'fill_opacity_pct': rows[pid]['fill_opacity_pct'], 'blend_mode': rows[pid]['blend_mode']}
            for pid in reversed(row['parent_layer_ids'])]
        asset['source_composition'] = {
            'audit': 'library/composition-audit.json', 'source_id': asset['style'],
            'layer_id': row['layer_id'], 'clipping_base_layer_id': row['clipping_base_layer_id'],
            'clip_layer_ids': row['clip_layer_ids'], 'parent_layer_ids': row['parent_layer_ids']}
        asset['source_effects_note'] = '完整颜色、图案资源、比例、相位及调整参数见 source_composition 指向的核验记录；效果总开关和单项开关分别保留。'
    data['version'] = '1.1'
    data.setdefault('notes', {})['composition'] = 'PNG 不含 Opacity、Fill、父组、剪贴基底、原蒙版及样式的完整合成关系。按 source_composition 和部位工序重建。'
    csv_path = folder/'asset-index.csv'
    with csv_path.open(encoding='utf-8-sig', newline='') as stream:
        fields = next(csv.reader(stream))
    for key in ('source_fill_opacity_pct', 'source_effects_master_enabled', 'source_composition'):
        if key not in fields:
            fields.append(key)
    (folder/'asset-index.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with csv_path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for asset in data['assets']:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in asset.items() if k in fields})
    print('Updated composition metadata for', sum(a['kind'] != 'reference' for a in data['assets']), 'assets.')


if __name__ == '__main__':
    refresh()
