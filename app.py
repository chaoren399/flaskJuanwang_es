# app.py
from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch
import math

# 初始化Flask应用
app = Flask(__name__)

# Elasticsearch连接配置
from elasticsearch import Elasticsearch

es = Elasticsearch(
    hosts=[{
        'host': '10.0.0.215',
        'port': 9200,
        'scheme': 'http'
    }],
    verify_certs=False,
    api_key=('api_key_id', 'api_key_secret')  # 如果使用API密钥
)

# 索引名称
INDEX_NAME = 'ticaixifen'


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

    # 构建Elasticsearch查询
    if query:
        # 如果有查询词，进行全文搜索
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["题干", "选项 A", "选项 B", "选项 C", "选项 D",
                               "选项 E", "选项 F", "选项 G", "选项 H", "解析"]
                }
            },
            "highlight": {
                "fields": {
                    "题干": {},
                    "解析": {}
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

        # 格式化结果
        formatted_results = []
        for hit in hits:
            source = hit['_source']
            doc = {
                'id': hit['_id'],
                '序号': source.get('序号', ''),
                '题干': source.get('题干', ''),
                '选项': {
                    'A': source.get('选项 A', ''),
                    'B': source.get('选项 B', ''),
                    'C': source.get('选项 C', ''),
                    'D': source.get('选项 D', ''),
                    'E': source.get('选项 E', ''),
                    'F': source.get('选项 F', ''),
                    'G': source.get('选项 G', ''),
                    'H': source.get('选项 H', '')
                },
                '解析': source.get('解析', ''),
                '分数': source.get('分数', ''),
                '答案': source.get('答案', ''),
                '标签': source.get('标签', '')
            }

            # 添加高亮内容（如果有）
            if 'highlight' in hit:
                doc['highlight'] = hit['highlight']

            formatted_results.append(doc)

        # 计算分页信息
        total_pages = math.ceil(total / size)

        return jsonify({
            'results': formatted_results,
            'total': total,
            'page': page,
            'size': size,
            'total_pages': total_pages,
            'query': query
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/question/<question_id>')
def question_detail(question_id):
    """显示问题详情"""
    try:
        result = es.get(index=INDEX_NAME, id=question_id)
        source = result['_source']

        question = {
            'id': result['_id'],
            '序号': source.get('序号', ''),
            '题干': source.get('题干', ''),
            '选项': {
                'A': source.get('选项 A', ''),
                'B': source.get('选项 B', ''),
                'C': source.get('选项 C', ''),
                'D': source.get('选项 D', ''),
                'E': source.get('选项 E', ''),
                'F': source.get('选项 F', ''),
                'G': source.get('选项 G', ''),
                'H': source.get('选项 H', '')
            },
            '解析': source.get('解析', ''),
            '分数': source.get('分数', ''),
            '答案': source.get('答案', ''),
            '标签': source.get('标签', '')
        }

        return render_template('detail.html', question=question)

    except Exception as e:
        return f"Error: {str(e)}", 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5030)
