import pymysql

host = 'localhost'
port = 3306
user = 'root'
password = '123456'
dbname = 'avbook'

def get_db():
    return pymysql.connect(host=host, port=port, user=user,
                         password=password, db=dbname)

def select(sql):
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result


def selectone(sql):
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result


def fetchone(sql, *args):
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql, args=args)
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result


def fetchall(sql, *args):
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql, args=args)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result


def execute(sql, *args):
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql, args=args)
    db.commit()
    cursor.close()
    db.close()
