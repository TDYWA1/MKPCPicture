import pymysql
import datetime
class DatabaseControl:
    def __init__(self,host,user,passwd,port=3306,dbname=None):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = port
        self.dbname = dbname
        self.conn = None
        self.cusor = None


    def connect(self):
        try:
            self.conn = pymysql.connect(user=self.user,host=self.host,password=self.passwd,port=self.port,database=self.dbname)
            self.cursor = self.conn.cursor()
        except Exception as e:
            return False,"connect to database {} error!".format(self.dbname)
        return True

    def insertInToDB(self,sql):
        if not self.conn==None:
            cursor = self.conn.cursor()
            try:
                cursor.execute(sql)
            except Exception as e:
                return False, "insert error"
            return True,"insert success"
        else:
            return False,"can't connect to database"

    def updateInToDB(self,sql):
        if not self.conn==None:
            cursor = self.conn.cursor()
            try:
                cursor.execute(sql)
            except Exception as e:
                return False, "update error"
            return True,"update success"
        else:
            return False,"can't connect to database"

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

if __name__ == '__main__':
    db = DatabaseControl(host='127.0.0.1', passwd='123456', user='ysl', dbname='mkpicture')
    sql = '''INSERT INTO divnum(id,name,order_num,create_date) VALUES (18,"BABY秀",10,"2012-03-28 23:52:39")'''
    print(db.connect())
    print(db.insertInToDB(sql))
    db.commit()

