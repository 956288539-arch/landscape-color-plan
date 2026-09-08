# 一键彩平功能 - 项目约定

## 彩平素材与质量基准

本项目进行 CAD 总图填色、Photoshop 彩平、背景彩平合成时，先读取：

1. `standards/彩平素材使用规范.md`
2. `standards/style-profiles.json`
3. `library/asset-index.json`
4. `standards/自动调用约定.md`
5. `standards/visual-composition.json`
6. `standards/material-workflows.json` 对应风格 / 部位，以及 `standards/四套PSD分层工艺拆解.md` 对应风格

完整流程使用 `skills/landscape-color-plan/SKILL.md`。自由景观示意先做树冠大、中、小层级及群落疏密，再做草坪亮、中、暗的宏观过渡；局部试铺必须同时通过整图缩略预览和 100% 检查。已有明确种植设计优先。

效果参考可选。按 `skills/landscape-color-plan/references/focus-and-color.md`，从目标功能、空间结构和展示用途自主确定主次、明暗与配色；明确参考用于校准，大致意向只提取适用特点。最终独立检查园内焦点、明暗分量和色彩关系，不以新增树数、肌理或外围绿化代替整体改善。

按部位完整工序执行：底色与肌理之外，还核对局部塑形、边缘接触、配景投影与合成调色。分别读取 Opacity、Fill、父组、剪贴关系、样式总开关和图案资源，记录操作完成状态；素材已置入不等于该部位完成。

按 `skills/landscape-color-plan/references/visual-review.md` 打开样例并检查成图。关键分区先核对功能；试铺覆盖最影响主图的节点及邻接空间，边角小样不能替代主图。工序逐项保留执行证据，视觉观察另行记录；不能以父组存在、树冠统计或全部 done 自动判定 L2。主要视觉问题修正后再展开全图，明确的设计与风格要求优先。

目标强调体量、地形与明显投影时，读取 `skills/landscape-color-plan/references/volume-and-lighting.md`，按对象核对高度依据、选择实施方式并统一受光和落影；局部渲染须与 CAD 配准。规范完整、工具可用和实际成图已通过分别记录。

乡村与山地默认选 rural；住宅及配套景观选 residential；曲线地形与水景节点选 landscape；城市活动公园、广场、花境花园选 park。优先使用本库已核验的真实材质和配景，沿用对应风格的纹理、植物层次、节点、光影与线稿关系。默认完成度为 L2。跨库补充按 style-profiles.json 的配方控制色阶、功能和光向。

素材仅决定表现，目标 CAD / 设计资料决定几何。`reference` 条目用于参考，不能直接铺入新项目充当建筑或场地。所有颜色和素材均受目标场地及分区蒙版约束。明确检查边缘、转角和空白遗漏。

保留原始 PSD；修改或扩展只写新版本。素材 ID 与文件哈希应写入最终使用记录。低分辨率素材、烘焙阴影和树组单位按索引处理。

## 项目工作方式

项目已使用 Git。所有代码、规范与素材索引变更保留可回退版本；缓存、依赖与临时视觉检查放在 `work/`。默认由主代理完成；只有严格必要时才创建子代理。
