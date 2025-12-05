# -*- coding: utf-8 -*-
import pymysql
from dotenv import load_dotenv
import os

# 加载.env文件
load_dotenv()


def get_template_count():
    """
    连接数据库并执行查询：SELECT COUNT(DISTINCT name) FROM `t_template`
    """
    # 从环境变量获取数据库配置
    config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT')),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME'),
        'charset': 'utf8mb4'
    }

    connection = None
    try:
        # 建立数据库连接
        connection = pymysql.connect(**config)

        with connection.cursor() as cursor:
            # 执行查询
            sql = "SELECT COUNT(DISTINCT name) FROM `t_template`"
            cursor.execute(sql)

            # 获取结果
            result = cursor.fetchone()
            count = result[0] if result else 0

            print(f"模板表中不同名称的数量: {count}")
            return count

    except pymysql.Error as e:
        print(f"数据库错误: {e}")
        return None
    except Exception as e:
        print(f"其他错误: {e}")
        return None
    finally:
        # 关闭数据库连接
        if connection:
            connection.close()


# 执行查询
if __name__ == "__main__":
    get_template_count()
