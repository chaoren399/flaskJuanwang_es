

es.a.baimeidashu.com


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