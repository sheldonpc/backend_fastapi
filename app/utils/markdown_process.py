import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
import xml.etree.ElementTree as etree


class ArticleStyleExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(ArticleStyleTreeprocessor(md), 'article_style', 15)


class ArticleStyleTreeprocessor(Treeprocessor):
    def run(self, root):
        # 为所有段落添加缩进样式
        for p in root.iter('p'):
            p.set('class', 'article-paragraph')

        # 调整标题大小
        for level in range(1, 7):
            for heading in root.iter(f'h{level}'):
                heading.set('class', f'article-heading article-heading-{level}')

        # 为代码块添加样式
        for code in root.iter('code'):
            if code.get('class') and 'language-' in code.get('class', ''):
                code.set('class', f"article-code {code.get('class')}")

        # 为表格添加样式
        for table in root.iter('table'):
            table.set('class', 'article-table')

        return root


def process_markdown(content):
    # 处理Markdown内容
    html = markdown.markdown(
        content,
        extensions=[
            'extra',
            'codehilite',
            'toc',
            'attr_list',
            'sane_lists',
            'tables',
            'smarty',
            ArticleStyleExtension()
        ],
        extension_configs={
            'codehilite': {
                'css_class': 'article-codehilite',
                'use_pygments': True
            },
            'toc': {
                'permalink': True,
                'permalink_class': 'article-headerlink',
                'title': '目录'
            }
        }
    )

    # 添加CSS样式
    styled_html = f"""
    <div class="article-container">
        {html}
    </div>
    <style>
        .article-container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            padding-top: 1px;
            font-family: 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
        }}

        .article-paragraph {{
            margin-bottom: 1em;
        }}

        .article-heading-1 {{
            font-size: 1.7em;
            margin-bottom: 0.8em;
            margin-top: 0.2em;
            color: #333;
            font-weight: bold;
            border-bottom: 1px solid #eee;
            padding-bottom: 0.8em;
            text-align: center;
        }}

        .article-heading-2 {{
            font-size: 1.3em;
            margin-bottom: 0.6em;
            margin-top: 0.6em;
            color: #444;
        }}

        .article-heading-3 {{
            font-size: 1.1em;
            margin-bottom: 0.5em;
            margin-top: 0.5em;
            color: #555;
        }}

        .article-code {{
            background-color: #f6f8fa;
            border-radius: 3px;
            padding: 0.2em 0.4em;
            font-family: Consolas, Monaco, 'Andale Mono', monospace;
        }}

        .article-codehilite {{
            background-color: #f6f8fa;
            border-radius: 6px;
            padding: 16px;
            overflow: auto;
            margin-bottom: 1em;
        }}

        .article-table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 1em;
        }}

        .article-table th, .article-table td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}

        .article-table th {{
            background-color: #f2f2f2;
        }}

        .article-headerlink {{
            text-decoration: none;
            color: #999;
            margin-left: 0.5em;
        }}

        .article-headerlink:hover {{
            color: #333;
        }}
    </style>
    """

    return styled_html