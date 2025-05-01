from pymysql import *

conn = connect(host='localhost',user='root',password='123456',database='wb',port=3306)
cursor = conn.cursor()


def querys(sql,params,type='no_select'):
    params = tuple(params)
    cursor.execute(sql,params)
    conn.ping(reconnect=True)
    if type != 'no_select':
        data_list = cursor.fetchall()
        conn.commit()
        return data_list
    else:
        conn.commit()
        return '数据库语句执行成功'