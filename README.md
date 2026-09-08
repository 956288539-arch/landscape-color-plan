# Landscape Color Plan · 景观彩平 Skill 与素材规范库

依据 CAD、总图或 PSD 的目标设计，组织空间主次、树群、草坪、材质与光影，完成可追溯的分层彩平。**不需要用户提供准确的效果参考图**：无参考时自主确定表达方向，有参考时提取适用特点，再以成图检验效果。

本仓库包含 skill、四套风格规范、**62 个材质 / 配景 PNG、16 个组合参考 JPG、4 张源图总览**，以及 **439 个图层及组**的来源与合成关系记录。

## 开始使用

完整克隆仓库，或从 GitHub 下载 ZIP 并解压。保留 `skills/`、`standards/`、`library/`、`tools/` 的相对关系。

在 Codex 中打开这个目录，或在已有项目中明确引用：

> 使用 `<仓库绝对路径>/skills/landscape-color-plan/SKILL.md`，根据当前 CAD 完成彩平。效果参考可选，请先自主确定主次、明暗与配色，并检查主要节点试铺。

也可把 `skills/landscape-color-plan` 链接到个人 skills 目录，链接应指向克隆仓库中的真实目录。若单独复制 skill，则需要在 `references/local-library.json` 中将 `library_root` 改为完整素材库的绝对路径。默认值 `../../..` 以该配置文件的真实位置为基准。

查询与尺度计划仅需要 Python 3 标准库：

```shell
python tools/materials.py --style park --role tree
python tools/materials.py --style landscape --role water --json
python tools/materials.py --style park --role grass --workflow --json
python skills/landscape-color-plan/scripts/visual_recipe.py --count 30 --medium-crown-px 80
```

上例的 80 px 只是演示输入，应按实际目标图确定中型可见冠幅。查询工具不操作 Photoshop，尺度脚本不布置树位、不生成彩平，也不自动判定视觉通过。

实际绘制由任务中的 Photoshop 或其他可用执行方式完成；原生 Photoshop 的操作说明见 skill。源 PSD 复核工具额外需要 `psd-tools`、`attrs` 和对应源文件；已登记素材的查询与使用不需要运行该工具。

## 规范入口

| 入口 | 内容 |
| --- | --- |
| [Skill](skills/landscape-color-plan/SKILL.md) | 完整工作方式、任务范围与参考路由 |
| [焦点、明暗与色彩](skills/landscape-color-plan/references/focus-and-color.md) | 无参考自主表达、成图平灰诊断、分区配色与合成复核 |
| [素材使用规范](standards/彩平素材使用规范.md) | 适用部位、尺度、来源、混合及边界 |
| [图文素材目录](standards/素材目录.md) | 每个素材的图片、用途与限制 |
| [四套 PSD 分层工艺](standards/四套PSD分层工艺拆解.md) | 原始图层、Fill、Opacity、剪贴、样式与调色的关系 |
| [自动调用约定](standards/自动调用约定.md) | 程序与代理的入口和交付记录 |
| [视觉验收](skills/landscape-color-plan/references/visual-review.md) | 园内主次、明暗分量、色彩、植物、材料和光影的实际判断 |
| [体积与光影](skills/landscape-color-plan/references/volume-and-lighting.md) | 按目标依据选择分层塑形、局部简模或混合表达 |

## 四种风格

| 风格 | 常见用途 | 表现方向 |
| --- | --- | --- |
| P / rural | 乡村、山地、自然河岸 | 自然植被连续性、橄榄绿、土褐与蓝灰水面 |
| R / residential | 住宅、宅间绿地、会客庭院 | 连续绿地、入口与停留节点、层次清楚的树群 |
| M / landscape | 曲线景观、建筑外场、水景 | 草地、浅色流线与水岸的衔接 |
| U / park | 城市公园、广场、花境花园 | 开敞面与活动节点对比、植物层次与局部强调色 |

按空间功能选择主风格，跨库补充遵循 [style-profiles.json](standards/style-profiles.json)。这些方向服务于目标设计，不决定场地几何，也不要求每个项目都高饱和或有明显投影。

## 当前质量控制

- 先安排主节点、次节点、衬托空间与颜色职责，再深化纹理。没有效果参考也需要自主完成这份判断。
- 树木先组织群落、冠幅角色和疏密；草坪先建立连续空间的大块明暗，避免每个绿岛复制同一亮斑。
- 检查最终合成中的明暗、色彩与投影贡献，防止继承的调色或父组透明度把已完成的层次压平。
- 功能、边界、单位和已有种植设计来自目标资料；参考中的建筑、球场和地形不直接移植。
- 默认目标为 L2。工序齐全、文件正常与视觉达标分别核验；用户指出的主要问题需实际修正后才能更新结论。

当前更新完成了规则、路径和素材查询检查。它不代表已经产出并验证了新的彩平成图；真实效果仍需由执行任务中的试铺与最终导出确认。

## 素材与记录

`library/assets/` 保存 28 个纹理取样和 34 个透明配景；`library/examples/` 保存组合参考与总览。`asset-index.json` / CSV 中共有 78 条记录，其中 62 条可调用，16 条用于参考。素材路径相对 `library/`，源和派生文件以 SHA256 追溯。

PNG 保留像素与透明通道，源图层不透明度、图层效果和全局调色不全部烘焙在内。依索引及工艺重新合成，按目标蒙版裁切，保留实际使用记录。普通纹理取样尚未验证无缝；冠幅单位与原素材像素上限应分别检查。

公开包保留源 PSD 的文件名、哈希和分层事实；大型原始 PSD、项目 CAD / 彩平交付文件与运行缓存保存在工作项目。公开包的 `sources.json` 中 `source-psd/` 表示按需提供的源文件位置。历史复核记录中的工程和缓存名称用于追溯，不是素材查询或 skill 使用的前置依赖。

需要 20 秒过程视频时，由实际执行任务记录成功绘制 / 合成步骤，不能用一张完成图的渐显动画替代。仅维护 skill 或做诊断时，不运行绘制程序。
