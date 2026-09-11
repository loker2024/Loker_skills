# Zhihu-Collections-MCP 项目适配参考

只在确认当前仓库具有下列结构时使用。函数名是定位提示，不是稳定 API；先读当前代码和依赖版本。

## 已验证的定位点

| 功能 | 典型位置 |
| --- | --- |
| 收藏夹总数及分页条目 | `main.py`: `get_article_nums_of_collection`、`get_article_urls_in_collection` |
| 回答正文 | `get_single_answer_content` |
| 专栏正文 | `get_single_post_content` |
| HTML 转 Markdown | `markdownify`、`ObsidianStyleConverter` |
| 图片下载及引用 | `ObsidianStyleConverter.convert_img` |
| 输出目录 | `base_output_path`、`current_collection_name`、`get_output_path` |
| 已导出 URL 去重 | 检查收藏夹处理函数及 `get_unique_filename` 的调用链 |

运行前检查导入模块是否自动载入示例 cookies/config、配置日志或触发网络；确认后再使用函数级调用。临时覆盖仅作用于当前进程，避免改坏用户配置。

收藏夹 Network 请求曾采用 `/api/v4/collections/<id>/items?offset=0&limit=20`。应以当前页面实际请求和分页响应为准，不能假设参数、签名或接口永不变化。

## 转换器修复模式

当前依赖若采用 `parent_tags` 参数，公式转换的最小形态是：

```python
def convert_span(self, el, text, parent_tags):
    tex = el.get("data-tex")
    if not tex:
        return text
    if el.get("data-eeimg") == "2":
        return "\n\n$$\n" + tex + "\n$$\n\n"
    return "$" + tex + "$"
```

这是需按已安装版本适配的模式，不是要求无条件粘贴的补丁。使用原始 `data-tex`，否则下划线和换行等可能已被普通文字转义。已有公式适配时先复现，避免重复处理。

图片结果应指向真实下载目录，例如 `![性能图](<assets/figure.jpg>)`。若函数原先输出 `![[figure.jpg]]`，文件虽存在，Typora 仍可能显示原始标记。不要只补下载而不修引用。

## 最小验收样例

- `data-eeimg="2"` 且 `data-tex` 含下标和双反斜杠的 span：输出保留原 LaTeX 的块公式。
- 中文句子内 `data-eeimg="1"` 的 span：只把公式置于行内分隔符中。
- 无 `data-tex` 的中文 span：文字保持不变。
- 一张图片：实际转换结果经 Markdown 解析得到 img 节点，其 src 解析到正确资产；下载得到的真实图片另做解码检查。

若仓库已有 `test/test_markdown_rendering.py`，运行它；另外对当前实际文章做源与输出检查，并在用户阅读器打开结果。测试通过不能替代全文和实际显示验收。

修复场景中，用干净缓存正文重新生成比对已转义 Markdown 做全局替换更可靠。只缓存正文，不保存包含账号信息的整页、请求头或完整 cURL。
