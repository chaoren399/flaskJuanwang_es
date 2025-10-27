# app_stockinfo.py
from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch
import math

# 初始化Flask应用
app = Flask(__name__)

# Elasticsearch连接配置
es = Elasticsearch(
    hosts=[{
        'host': '10.0.0.215',
        'port': 9200,
        'scheme': 'http'
    }]
)

# 索引名称
INDEX_NAME = 'stockinfo'


@app.route('/')
def index():
    """主页路由，显示搜索界面"""
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    """处理搜索请求"""
    # 获取查询参数
    query = request.args.get('q', '').strip()
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    search_type = request.args.get('type', 'fulltext')  # 查询类型: fulltext(全文) 或 precise(精准)
    field_filter = request.args.get('field', 'all')  # 字段过滤

    # 构建Elasticsearch查询
    if query:
        if search_type == 'precise':
            # 精准查询 - 使用term查询
            if field_filter != 'all':
                # 指定字段精准查询
                search_body = {
                    "query": {
                        "term": {f"{field_filter}.keyword": query}
                    }
                }
            else:
                # 多字段精准查询
                search_body = {
                    "query": {
                        "bool": {
                            "should": [
                                {"term": {"题干.keyword": query}},
                                {"term": {"选项A.keyword": query}},
                                {"term": {"选项B.keyword": query}},
                                {"term": {"选项C.keyword": query}},
                                {"term": {"选项D.keyword": query}},
                                {"term": {"选项E.keyword": query}},
                                {"term": {"选项F.keyword": query}},
                                {"term": {"选项G.keyword": query}},
                                {"term": {"选项H.keyword": query}},
                                {"term": {"答案.keyword": query}},
                                # {"term": {"标签.keyword": query}},
                                {"wildcard": {"标签.keyword": f"*{query}*"}},  # 修改为wildcard查询支持模糊匹配
                                {"term": {"解析.keyword": query}}
                            ],
                            "minimum_should_match": 1
                        }
                    }
                }
        else:
            # 全文搜索 - 使用multi_match查询
            if field_filter != 'all':
                # 指定字段搜索
                search_body = {
                    "query": {
                        "match": {
                            field_filter: {
                                "query": query,
                                "operator": "and"
                            }
                        }
                    },
                    "highlight": {
                        "pre_tags": ["<span class='highlight'>"],
                        "post_tags": ["</span>"],
                        "fields": {
                            field_filter: {}
                        }
                    }
                }
            else:
                # 全字段搜索
                search_body = {
                    "query": {
                        "multi_match": {
                            "query": query,
                            "fields": ["题干", "选项A", "选项B", "选项C", "选项D",
                                       "选项E", "选项F", "选项G", "选项H", "解析", "标签"],
                            "operator": "and"
                        }
                    },
                    "highlight": {
                        "pre_tags": ["<span class='highlight'>"],
                        "post_tags": ["</span>"],
                        "fields": {
                            "题干": {},
                            "选项A": {},
                            "选项B": {},
                            "选项C": {},
                            "选项D": {},
                            "选项E": {},
                            "选项F": {},
                            "选项G": {},
                            "选项H": {},
                            "解析": {},
                            "标签": {}  #新加2025年10月27日 可以搜索到标签

                        }
                    }
                }
    else:
        # 如果没有查询词，返回所有文档
        search_body = {
            "query": {
                "match_all": {}
            }
        }

    try:
        # 执行搜索
        result = es.search(
            index=INDEX_NAME,
            body=search_body,
            from_=(page - 1) * size,
            size=size
        )

        # 处理搜索结果
        hits = result['hits']['hits']

        total = result['hits']['total']['value']
        print("---hist---")
        print(hits)
        # 格式化结果
        formatted_results = []
        for hit in hits:
            source = hit['_source']

            doc = {
                'id': hit['_id'],
                '序号': source.get('序号', '') or '',
                '题干': source.get('题干', '') or '',
                '选项': {
                    'A': source.get('选项A', '') or '',
                    'B': source.get('选项B', '') or '',
                    'C': source.get('选项C', '') or '',
                    'D': source.get('选项D', '') or '',
                    'E': source.get('选项E', '') or '',
                    'F': source.get('选项F', '') or '',
                    'G': source.get('选项G', '') or '',
                    'H': source.get('选项H', '') or ''
                },
                '解析': source.get('解析', '') or '',
                '分数': source.get('分数', '') or '',
                '答案': source.get('答案', '') or '',
                '标签': source.get('标签', '') or ''
            }

            # 添加高亮内容（如果有）
            if 'highlight' in hit:
                doc['highlight'] = hit['highlight']

            formatted_results.append(doc)

        print('Results-----:', formatted_results)
        # 返回结果
        return jsonify({
            'results': formatted_results,
            'total': total,
            'page': page,
            'total_pages': math.ceil(total / size),
            'size': size,
            'query': query,
            'search_type': search_type,
            'field_filter': field_filter
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/question/<question_id>')
def question_detail(question_id):
    """题目详情页面"""
    try:
        result = es.get(index=INDEX_NAME, id=question_id)
        question = result['_source']
        question['id'] = question_id
        return render_template('detail.html', question=question)
    except Exception as e:
        return f"Error: {str(e)}", 404


@app.route('/tags')
def get_tags():
    """获取所有标签"""
    try:
        # 使用聚合查询获取标签
        search_body = {
            "size": 0,
            "aggs": {
                "tags": {
                    "terms": {
                        "field": "标签.keyword",
                        "size": 1000
                    }
                }
            }
        }

        result = es.search(index=INDEX_NAME, body=search_body)
        tags = [bucket['key'] for bucket in result['aggregations']['tags']['buckets']]
        return jsonify({'tags': tags})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(debug=True, host='0.0.0.0', port=5030)
