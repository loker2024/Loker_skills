---
name: conversation-title
description: Use when the user asks to name, rename, or standardize the current Codex conversation title, including Chinese requests such as “为当前对话命名” or “按规范重命名”. Excludes bulk historical task renaming.
---

# 对话标题格式化

当用户要求为当前 Codex 对话命名、重命名或统一标题格式时，使用此 skill。

## 命名流程

1. 读取当前对话的 `createdAt`，转换为 Asia/Shanghai 日期；不得用 `updatedAt` 代替。
2. 根据本次实际任务选择一个类型：`功能`、`设计`、`修复`、`优化`、`发布`、`探索`、`文档`、`研究`。
3. 提炼简洁、具体的主题；不要重复项目名称、堆砌关键词或照抄完整用户消息。
4. 以 `YYYYMMDD｜类型｜主题` 设置标题。

## 边界

- 只能修改当前对话的标题，不修改项目名称、归属、排序、置顶、归档、内容或其他对话。
- 无法可靠取得 `createdAt`，或无法可靠判断类型和主题时，不要猜测或改名；向用户简要说明原因。
- 只处理当前对话。批量整理或重命名历史对话需要用户明确另行提出。
