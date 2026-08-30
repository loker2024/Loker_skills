---
name: paper-fast-understanding
description: Fast understanding workflow for AI and machine learning papers. Use when the user provides or asks to analyze a paper PDF, arXiv/DOI/publisher link, project page, code repository, or asks for 快速读懂论文, 论文速读, AI论文理解, paper reading, paper summary with methods, formulas, experiments, reviewer critique, or reproduction guidance. Default to conclusions first, then explain background, method, formulas, figures, experiments, limitations, and reproducibility details.
---

# AI Paper Fast Understanding

## Core Positioning

Use this skill to help the user quickly understand artificial intelligence papers.

Default modes:

- Main mode: fast understanding.
- Auxiliary mode: learning-oriented explanation.
- Auxiliary mode: reproduction-oriented practice.

Always give the conclusion first, then unfold method, formulas, experiments, and reproduction details.

## Inputs

Support these inputs:

- Uploaded paper PDF.
- Paper link, including arXiv, DOI, publisher page, project page, or repository link.

Handle inputs by priority:

- For PDFs: read the full text, formulas, figures, tables, experiments, appendices, and supplementary materials when available.
- For links: fetch the paper body first, then look for official project pages, official code repositories, supplementary materials, and author notes.

If online material is needed or the user provides a link, browse and cite sources. Use the paper as the primary source.

## User Level

Explain by default for a computer science student:

- Assume programming fundamentals.
- Assume basic machine learning knowledge.
- Do not assume familiarity with the paper's narrow subfield.
- Add background explanations for unfamiliar concepts.
- Avoid repeating concepts that have already been explained in the same answer.
- Adjust depth based on follow-up questions.

## Source Boundaries

Separate all claims into one of these categories:

- Paper text.
- Official supplement, project page, or official code.
- External background explanation.
- Your own analysis.

Do not describe external material as a conclusion from the paper. Do not treat author claims as proven facts.

When the paper does not provide a reproduction detail, write "论文未说明". Do not invent hyperparameters, hardware, preprocessing, or implementation details.

## Default Output

Always produce the following three layers unless the user explicitly requests a narrower output.

### Layer 1: 30-Second Overview

Include:

- One-sentence summary.
- Problem solved by the paper.
- Core method.
- Main experimental results.
- Biggest innovation.
- Biggest limitation.
- Whether the paper is worth reading further.

### Layer 2: 5-Minute Understanding

Include:

- Research background and motivation.
- Problems with existing methods.
- Overall idea.
- Model structure and data flow.
- Core modules.
- Key formulas.
- Experimental design.
- Main results and ablations.
- Limitations.

### Layer 3: Reproduction Information

Include:

- Dataset.
- Data preprocessing.
- Model configuration.
- Loss function.
- Optimizer.
- Learning rate.
- Batch size.
- Epochs.
- Hardware environment.
- Evaluation metrics.
- Official code.
- Dependency environment.
- Training procedure.
- Reproduction difficulties.
- Likely pitfalls.
- Minimal reproduction plan.
- Reproduction success criteria.

Mark every missing item as "论文未说明".

## Formula Handling

Use tiered formula explanation.

For core innovation formulas, explain:

- What problem the formula solves.
- Intuition first.
- Meaning of every important symbol.
- Inputs and outputs.
- Computation process.
- Why the design makes sense.
- How it differs from ordinary methods.
- A simplified derivation or small example when useful.

For ordinary formulas, explain:

- Function of the formula.
- Key variables.
- Inputs and outputs.
- Relationship to other model parts.

For secondary formulas, summarize their purpose in one sentence.

When there are many formulas, choose the 3 to 5 formulas most important for understanding the paper.

Explain formulas in this order:

1. Intuition.
2. Symbols.
3. Computation.
4. Design reason.

## Figure And Table Handling

Use tiered figure and table explanation.

For core model architecture figures, explain:

- Function of each module.
- Where data enters.
- Which steps data passes through.
- How modules connect.
- Final output.
- Which parts are the paper's innovations.

For main result tables, explain:

- Compared methods.
- Metrics.
- Best method.
- Amount of improvement.
- Whether the improvement is practically meaningful.
- Whether the comparison may be unfair.

For ablation studies, check:

- Whether each module is truly useful.
- Whether module combinations are useful.
- Whether key ablations are missing.
- Whether gains are stable.
- Whether experiments support the author's conclusion.

For secondary figures and tables, summarize only key trends and conclusions.

Figure and table conclusions must use concrete values when values are available.

## Dual Perspective Analysis

Always include both perspectives.

### Author Perspective

Faithfully state:

- What the authors think the problem is.
- What method they propose.
- What innovations they claim.
- What experiments they provide.
- What conclusions they draw.

### Reviewer Perspective

Independently check:

- Whether the innovation is real.
- Whether the method is only a combination of known modules.
- Whether experiments are sufficient.
- Whether comparisons are fair.
- Whether baselines are strong enough.
- Whether datasets are representative.
- Whether metrics are appropriate.
- Whether multiple runs are reported.
- Whether standard deviation or confidence intervals are provided.
- Whether ablations are sufficient.
- Whether there may be selective reporting.
- Whether data leakage is possible.
- Whether conclusions exceed the evidence.
- Whether reproduction information is complete.

Do not criticize just for the sake of criticism. Distinguish:

- Author claims.
- What experiments directly prove.
- Reasonable inference.
- What remains unproven.

## Recommended Template

Use this structure by default.

```markdown
# 论文标题

## 一、30 秒速览

* 一句话概括：
* 研究问题：
* 核心方法：
* 主要结果：
* 最大创新：
* 最大局限：
* 阅读建议：

## 二、论文基本信息

* 作者：
* 机构：
* 发表时间：
* 会议或期刊：
* 论文链接：
* 官方代码：
* 项目主页：

## 三、研究背景

### 3.1 论文研究什么

### 3.2 为什么这个问题重要

### 3.3 现有方法有什么不足

## 四、核心方法

### 4.1 整体思路

### 4.2 模型输入与输出

### 4.3 模型结构

### 4.4 核心创新模块

### 4.5 完整数据流程

## 五、关键公式

对每个核心公式依次说明：

* 公式作用
* 直觉理解
* 符号含义
* 输入输出
* 计算过程
* 设计原因

## 六、实验设计

* 数据集
* 任务
* 基线方法
* 评价指标
* 实现细节
* 硬件环境

## 七、实验结果

### 7.1 主结果

### 7.2 消融实验

### 7.3 可视化结果

### 7.4 结果是否支持作者结论

## 八、审稿人视角

* 创新性：
* 实验充分性：
* 对比公平性：
* 统计可靠性：
* 潜在问题：
* 论文局限：
* 总体评价：

## 九、复现指南

### 9.1 官方资源

### 9.2 环境与依赖

### 9.3 数据准备

### 9.4 训练步骤

### 9.5 评价步骤

### 9.6 关键超参数

### 9.7 论文未说明的信息

### 9.8 可能踩坑点

### 9.9 最小复现方案

### 9.10 复现成功标准

## 十、最终总结

* 这篇论文真正的新意是什么
* 最值得学习的部分是什么
* 最值得怀疑的部分是什么
* 适合哪些人阅读
* 是否值得精读
* 推荐继续阅读哪些内容
```

## Mandatory Rules

Follow these rules strictly:

1. Do not merely rewrite the abstract.
2. Do not treat author claims as facts.
3. Do not invent hyperparameters or reproduction details.
4. Mark uncertain or missing information clearly.
5. Explain figure and table conclusions with concrete values when available.
6. Explain core formulas with intuition first.
7. Separate paper text, external material, official supplements, and your own judgment.
8. State how far the paper's evidence actually supports its conclusions.
9. Provide reproduction difficulties and a minimal reproduction plan.
10. Help the user build the overall paper framework first, then expand local details.
