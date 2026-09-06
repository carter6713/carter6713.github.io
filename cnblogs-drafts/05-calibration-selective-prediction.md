---
title: 模型说 90% 真的可信吗 植物病害识别中的概率校准与选择性预测
date: 2026-09-06
categories: 机器学习, 计算机视觉
tags: 概率校准, 选择性预测, 不确定性, 植物病害识别
status: 待发布
---

# 模型说“90%”真的可信吗：植物病害识别中的概率校准与选择性预测

> 本文是一篇公开的可信机器学习方法笔记，只介绍通用评估与实现思路，不包含未公开课题的实验结果。

分类模型通常会输出一个最高类别概率。例如，模型把一张叶片图像判断为某种病害，并给出 90% 的置信度。这个数字很容易让人产生一种直觉：在所有置信度约为 90% 的样本中，模型大约应有 90% 判断正确。

但神经网络的 Softmax 输出并不会自动满足这种对应关系。模型可能分类准确，却过度自信；也可能在新设备、新季节或田间背景下仍给出很高的概率，却频繁判断错误。因此，部署前不能只问“预测是什么”，还要问两个问题：**这个概率是否可信？不可信时系统能否暂缓自动判断？**

![从分类输出到校准、接收与人工复核的决策流程](https://carter6713.github.io/blog/img/research-notes/calibrated-selective-prediction.png)

## 一、准确率与校准回答的是不同问题

准确率关心预测类别是否正确，校准关心置信度与实际正确率是否匹配。假设两个模型的准确率都是 85%：

- 模型 A 在错误样本上经常给出 99% 的置信度；
- 模型 B 在困难样本上只给出 55%—65% 的置信度。

如果系统允许把低置信度样本交给人工复核，模型 B 往往更容易建立安全的工作流。准确率相同，并不代表两个模型的风险表达能力相同。

校准也不等于分类能力。一个始终输出类别频率的模型可能具有某种统计校准，却没有足够的个体判别能力。因此，分类指标与校准指标必须同时报告。

## 二、先画可靠性图

可靠性图会把预测按置信度分箱，再比较每个分箱的平均置信度与真实正确率：

```python
import numpy as np

def reliability_bins(confidence, correct, n_bins=10):
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    rows = []

    for left, right in zip(edges[:-1], edges[1:]):
        mask = (confidence > left) & (confidence <= right)
        if not mask.any():
            continue

        rows.append({
            "count": int(mask.sum()),
            "mean_confidence": float(confidence[mask].mean()),
            "accuracy": float(correct[mask].mean()),
        })

    return rows
```

理想情况下，各分箱应靠近 `accuracy = confidence` 的对角线。若某一分箱的平均置信度为 0.9，实际正确率却只有 0.7，模型就在该区间明显过度自信。

分箱图容易受样本量和分箱方式影响，所以不要只展示曲线，还应给出每个分箱的样本数。小样本任务中，一个只有两三个样本的柱子不能支持稳定结论。

## 三、ECE 和 Brier score 怎样理解

### 1. Expected Calibration Error

ECE 对各置信度分箱中的“平均置信度—实际正确率”差异进行加权。它直观、常用，但会受到分箱数量和边界的影响。比较实验时应固定分箱策略，并报告设置。

### 2. Brier score

Brier score 直接衡量预测概率与真实标签之间的平方差。它不依赖分箱，但同时受到分类准确性和概率质量影响。

因此，更稳妥的报告方式是：可靠性图用于观察误差发生在哪个置信度区间，ECE 提供概括性校准指标，Brier score 作为不依赖分箱的补充。任何一个数字都不应被单独解释为“模型可信”。

## 四、温度缩放是一条简单基线

温度缩放保留类别排序，只用一个正数温度调整 logits：

```text
p(y | x) = softmax(z / T)
```

当 `T > 1` 时，概率通常会变得更平缓；当 `T < 1` 时，概率会更尖锐。温度必须只在验证集上拟合，不能利用测试标签。

```python
import torch
import torch.nn as nn

class TemperatureScaler(nn.Module):
    def __init__(self):
        super().__init__()
        self.log_temperature = nn.Parameter(torch.zeros(()))

    def forward(self, logits):
        temperature = self.log_temperature.exp().clamp_min(1e-6)
        return logits / temperature
```

温度缩放是值得保留的基线，因为实现简单且不会改变预测类别。但它不是万能修复：如果验证集与部署环境差异很大，用验证集拟合的温度在新域中仍可能失效。

## 五、选择性预测：允许模型说“我不确定”

选择性预测不要求系统自动处理所有样本。设定置信度阈值后：

- 高于阈值的样本自动输出；
- 低于阈值的样本进入人工复核或补充检测；
- 图像质量异常、类别不在训练范围内的样本直接拒绝。

```python
probability = torch.softmax(calibrated_logits, dim=1)
confidence, prediction = probability.max(dim=1)

threshold = 0.80
accept = confidence >= threshold
review = ~accept
```

阈值不能凭感觉选择，而应根据验证集上的“覆盖率—风险”曲线确定：

- **覆盖率**：模型自动处理的样本比例；
- **选择性风险**：在已接收样本上的错误率。

阈值升高通常会降低覆盖率，并可能降低已接收样本的风险。一个完整结果不应只报告某个阈值下的准确率，而要展示不同覆盖率下风险怎样变化。

## 六、校准必须在分布变化下重新检查

模型在实验室数据上校准良好，不代表它在田间图像上仍然可靠。背景、相机、病程和季节改变后，错误率与置信度可能同时发生漂移。

建议至少分开报告：

| 场景 | 分类指标 | 校准指标 | 选择性指标 |
|---|---|---|---|
| 域内测试 | Macro-F1、召回率 | ECE、Brier score | 覆盖率—风险曲线 |
| 新设备或新地点 | Macro-F1、召回率 | ECE、Brier score | 覆盖率—风险曲线 |
| 图像质量退化 | Macro-F1、召回率 | ECE、Brier score | 拒绝率、错误接收率 |

如果新域数据参与温度或阈值拟合，就应明确称为适配后的结果；如果研究目标是未知域泛化，模型选择阶段不能读取该域的标签。

## 七、人工复核也需要形成闭环

“交给专家”并不是一句结束语。系统还需要记录：哪些样本被拒绝、人工如何修改、修改结果是否进入后续训练，以及新版本是否重新完成独立评估。

建议保存以下字段：

```text
sample_id
predicted_class
confidence
calibration_version
decision: accept / review / reject
reviewed_label
review_reason
model_version
```

这些记录既能支持错误分析，也能防止人工修正结果在没有版本控制的情况下悄悄回流到测试集。

## 八、发布前检查清单

- [ ] 概率校准只使用验证集拟合；
- [ ] 分类性能和校准性能分开报告；
- [ ] 可靠性图同时展示各分箱样本量；
- [ ] ECE 的分箱规则保持一致并被记录；
- [ ] 阈值通过覆盖率—风险关系确定；
- [ ] 域内与域外校准结果分别报告；
- [ ] 被拒绝样本有清晰的人工复核与版本记录。

在高风险或数据稀缺的视觉任务中，一个能够表达不确定性并主动暂缓判断的模型，通常比一个对所有输入都给出肯定答案的模型更容易被安全使用。可信系统的关键并不是让模型永远自信，而是让它的自信程度可以被检查、校正和约束。

## 参考资料

1. Guo et al. [On Calibration of Modern Neural Networks](https://proceedings.mlr.press/v70/guo17a.html).
2. Ovadia et al. [Can You Trust Your Model's Uncertainty? Evaluating Predictive Uncertainty Under Dataset Shift](https://arxiv.org/abs/1906.02530).
3. Geifman and El-Yaniv. [Selective Classification for Deep Neural Networks](https://arxiv.org/abs/1705.08500).
4. scikit-learn. [Probability Calibration](https://scikit-learn.org/stable/modules/calibration.html).
