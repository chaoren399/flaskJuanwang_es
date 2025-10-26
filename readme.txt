

es.a.baimeidashu.com

1-新题材步骤

先把xlxs 文件复制到data/目录下
然后执行 tool_xlsx_to_csv.py 转换为csv 文件（存储到 data/csv目录下）

然后执行tool_csv_to_es.py 把csv 文件导入 es 中就可以。
也去搜索验证一下。


openpyxl

将目录D:\03-code\pycharm\stock\flaskJuanwang_es\data\csv 中所有CSV 文件导入ES
# Elasticsearch连接配置 - 修复版本
es = Elasticsearch(
    hosts=[{
        'host': '10.0.0.215',
        'port': 9200,
        'scheme': 'http'  # 添加scheme参数
    }]
)

es:"8.14.1

用户名:elastic 密码:123456


且索引设置为 stockinfo


    # 创建索引
    mapping = {
        "mappings": {
            "properties": {
                "序号": {"type": "integer"},
                "题干": {"type": "text"},
                "选项 A": {"type": "text"},
                "选项 B": {"type": "text"},
                "选项 C": {"type": "text"},
                "选项 D": {"type": "text"},
                "选项 E": {"type": "text"},
                "选项 F": {"type": "text"},
                "选项 G": {"type": "text"},
                "选项 H": {"type": "text"},
                "解析": {"type": "text"},
                "分数": {"type": "keyword"},
                "答案": {"type": "text"},
                "标签": {"type": "keyword"}
            }
        }
    }

适应手机屏幕显示
保存历史记录10条

