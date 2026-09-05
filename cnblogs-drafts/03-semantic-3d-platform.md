---
title: 从语义到三维场景 一个可追溯的智能展馆平台怎样设计
date: 2026-09-05
categories: 三维应用, 全栈开发
tags: Three.js, Django REST Framework, 场景图, 语义驱动
status: 待发布
---

# 从语义到三维场景：一个可追溯的智能展馆平台怎样设计

在“语义导向的三维虚拟数字展馆智能生成平台”项目中，我逐渐意识到：真正难维护的不是把一个 GLB 模型加载到网页，而是让“展品是谁、放在哪里、和什么内容绑定、由谁修改过”成为可查询的数据。

如果场景只存在于 Three.js 运行时对象里，刷新页面后就只剩下一段难以解释的 JSON；如果每次修改都覆盖旧结果，系统也无法支持回退、比较和审核。

这篇文章整理一套可复用的系统设计思路。它描述的是公开架构与原型经验，不涉及合作项目的业务数据、未公开接口或部署信息。

![语义驱动三维平台的结构化中间层](https://carter6713.github.io/blog/img/research-notes/semantic-3d-architecture.png)

## 一、三维场景不是一个文件

一个可编辑展馆至少包含五类对象：

- **资产**：展馆、展柜、展品、灯光等 GLB/图片/视频文件；
- **实体**：场景中的可选择对象及其稳定标识；
- **关系**：位于、相邻、面向、绑定等对象关系；
- **内容**：标题、说明、图片、音视频和交互行为；
- **方案**：某个版本下全部摆放、绑定与参数的集合。

把它们压缩成一个巨大的场景 JSON 虽然起步快，但之后任何局部更新都要读写整份数据，也难以回答“是谁改了哪个展品”。

## 二、先建立结构化中间层

我更倾向于用以下层级组织数据：

```text
Project
└── Version
    ├── Entity
    ├── Relation
    ├── ContentBinding
    └── ScenePlan
```

一个实体可以使用这样的公开化表示：

```json
{
  "id": "entity_exhibit_023",
  "type": "exhibit",
  "asset_id": "asset_ceramic_07",
  "transform": {
    "position": [1.25, 0.8, -2.1],
    "rotation": [0, 1.57, 0],
    "scale": [1, 1, 1]
  },
  "semantic": {
    "theme": "craft",
    "importance": "primary"
  }
}
```

这里的 `id` 必须稳定。Three.js 对象名称适合调试，却不一定适合作为数据库主键；同一个 GLB 中还可能有重名节点。加载模型后应把后端实体 ID 写入 `userData`，让点击选择能够回到业务对象。

## 三、关系与约束要分开

关系描述“当前是什么”，约束描述“允许成为什么”。例如：

```json
{
  "relation": ["entity_exhibit_023", "inside", "region_hall_a"],
  "constraints": {
    "min_clearance_m": 0.8,
    "allowed_wall": ["wall_north", "wall_east"],
    "requires_media": true
  }
}
```

如果把约束只写在前端拖拽逻辑里，批量生成、导入数据或更换客户端时就会失效。约束应在后端再次校验，并返回结构化错误：违反了哪条规则、涉及哪些实体、是否可以自动修复。

DRF Serializer 很适合承担这层边界：

```python
from rest_framework import serializers

class TransformSerializer(serializers.Serializer):
    position = serializers.ListField(
        child=serializers.FloatField(), min_length=3, max_length=3
    )
    rotation = serializers.ListField(
        child=serializers.FloatField(), min_length=3, max_length=3
    )
    scale = serializers.ListField(
        child=serializers.FloatField(min_value=0.001),
        min_length=3,
        max_length=3,
    )

class EntitySerializer(serializers.Serializer):
    id = serializers.CharField()
    type = serializers.ChoiceField(["hall", "region", "exhibit", "media"])
    asset_id = serializers.CharField()
    transform = TransformSerializer()
```

序列化器负责格式与基本约束，跨实体碰撞、区域容量和关系闭包等检查则放到独立领域服务，避免把业务逻辑全部塞进 `.validate()`。

## 四、Three.js 只负责渲染吗

Three.js 的 `GLTFLoader` 可以加载 glTF 2.0 资产，但平台还要维护从资产节点到业务实体的映射：

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const loader = new GLTFLoader();
const gltf = await loader.loadAsync(asset.url);

gltf.scene.traverse((node) => {
  const entityId = node.userData?.entityId;
  if (entityId) entityIndex.set(entityId, node);
});

scene.add(gltf.scene);
```

需要注意三点：

1. 资产加载成功不代表语义绑定成功；两者应分别报告状态。
2. 替换模型时要清理几何体、材质和纹理，避免长时间编辑后的内存泄漏。
3. 变换保存要统一坐标系、单位与旋转表示，不能让前后端各自猜测。

## 五、为什么必须做版本化

三维方案编辑是高频局部修改：移动一个展品、替换一张图片、调整灯光、修改说明文字。若每次保存都原地覆盖，系统很难支持：

- 比较两个方案；
- 回退到上一次稳定状态；
- 审核生成结果；
- 定位错误来源；
- 复现实验或演示。

一种简单做法是让 Version 不可变：用户每次确认保存，就基于父版本创建新版本，只存变化或生成完整快照。前者节省空间但读取复杂，后者查询简单但占用更多存储。原型阶段可以先用完整快照，等数据规模明确后再引入事件日志或差量存储。

## 六、“智能生成”应该停在哪里

语义驱动并不意味着一句自然语言必须直接生成最终可发布展馆。更可靠的链路是：

1. 把用户意图解析成结构化实体、关系和约束；
2. 校验缺失字段与冲突；
3. 生成候选 ScenePlan；
4. 在 Three.js 中预览；
5. 由用户确认或修改；
6. 保存为新版本并记录来源。

模型可以提出候选，结构化中间层负责让候选可检查，人负责决定是否发布。这比“黑盒端到端生成”多了几步，却更适合真实项目中的维护、追溯与协作。

## 七、上线前的工程检查清单

- GLB 资产、贴图和多媒体是否有稳定 ID 与版本号；
- 前后端是否统一坐标系、单位和旋转表示；
- 场景对象是否能够追溯到数据库实体；
- 所有写入是否经过后端校验；
- 保存是否创建新版本，失败是否保持原版本不变；
- 模型与纹理是否在移除后正确释放；
- 生成内容是否标记来源并经过人工确认；
- 日志中是否避免记录未脱敏的业务内容。

回头看这类平台，最有价值的并不是“页面上出现了一个 3D 展馆”，而是形成了从项目、版本、绑定到方案的完整数据闭环。只要中间层足够清晰，后续更换生成模型、渲染框架或数据库都不会推翻全部系统。

## 参考资料

1. Three.js. [GLTFLoader Documentation](https://threejs.org/docs/pages/GLTFLoader.html).
2. Django REST Framework. [Serializers](https://www.django-rest-framework.org/api-guide/serializers/).
3. Wald et al. [Learning 3D Semantic Scene Graphs from 3D Indoor Reconstructions](https://openaccess.thecvf.com/content_CVPR_2020/html/Wald_Learning_3D_Semantic_Scene_Graphs_From_3D_Indoor_Reconstructions_CVPR_2020_paper.html).
4. Gao et al. [GraphDreamer: Compositional 3D Scene Synthesis from Scene Graphs](https://openaccess.thecvf.com/content/CVPR2024/papers/Gao_GraphDreamer_Compositional_3D_Scene_Synthesis_from_Scene_Graphs_CVPR_2024_paper.pdf).
