"""Query the project-local landscape material catalog (Python standard library)."""
from pathlib import Path
import argparse,json,sys

ROOT=Path(__file__).resolve().parent.parent

def main():
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description='查询四套彩平素材：P 乡村 / R 住宅 / M 现代景观 / U 城市公园')
    parser.add_argument('--style',choices=['rural','residential','landscape','park'])
    parser.add_argument('--role',choices=['grass','tree','water','paving','wood','planting','furniture','vehicle','person','water_detail','reference'])
    parser.add_argument('--id',dest='asset_id')
    parser.add_argument('--references',action='store_true',help='包括原图组合参考（不能自动贴入目标图）')
    parser.add_argument('--json',action='store_true',help='输出全部元数据')
    parser.add_argument('--workflow',action='store_true',help='查询部位完整工序与对应风格的处理方法')
    args=parser.parse_args()
    if args.workflow:
        if not args.style or not args.role or args.asset_id:
            parser.error('--workflow 需要 --style 和 --role，不能与 --id 同用。')
        workflows=json.loads((ROOT/'standards/material-workflows.json').read_text('utf-8'))
        profile=workflows['profiles'][args.style]
        if args.role not in profile['roles']:
            print('该风格没有登记此部位工序；按目标功能复核，不自动补充设施。')
            return 1
        recipe=profile['roles'][args.role]
        result={'workflow_id':recipe['workflow_id'],'style':args.style,'role':args.role,
                'common_operations':workflows['common_operations'][args.role],
                'style_adaptation':recipe,'finishing':profile['finishing'],
                'evidence':workflows['evidence'],'completion_record':workflows['completion_record']}
        if args.json:print(json.dumps(result,ensure_ascii=False,indent=2))
        else:
            print(result['workflow_id'])
            for step in result['common_operations']:print(f"  {step['id']}：{step['operation']}")
            for step in recipe['adaptation']:print('  风格处理：'+step)
            print('  合成收尾：'+'；'.join(profile['finishing']['operations']))
        return 0
    records=json.loads((ROOT/'library/asset-index.json').read_text('utf-8'))['assets']
    result=[r for r in records if (not args.style or r['style']==args.style) and (not args.role or args.role in r['roles']) and (not args.asset_id or r['id']==args.asset_id) and (r['approved'] or args.references or args.role=='reference' or args.asset_id)]
    if args.json:print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        for r in result:
            print(f"{r['id']} | {r['name']} | {r['pixel_size'][0]} x {r['pixel_size'][1]} px | {r['kind']}")
            print(f"  用于：{r['use']}\n  规则：{r['rule']}")
            print(f"  文件：{ROOT/'library'/r['file']}")
            if r['kind']!='reference':print(f"  源不透明度：{r['source_opacity_pct']}% | 模式：{r['source_blend'].strip()} | 效果未烘焙：{[e['type'] for e in r['source_effects']]}")
            if r['kind']!='reference':print(f"  源填充：{r.get('source_fill_opacity_pct','未登记')}% | 样式总开关：{r.get('source_effects_master_enabled','未登记')} | 完整工序：--style {r['style']} --role {r['roles'][0]} --workflow")
        print(f'共 {len(result)} 项。')
    return 0 if result else 1

if __name__=='__main__':raise SystemExit(main())
