import requests
import json
import database
import datetime

LIMIT = 200
HOST = "http://lab.mkblog.cn/wallpaper/"
API_DIVDE = "http://lab.mkblog.cn/wallpaper/api.php?cid=360tags"
HEADERS = {'Host': 'lab.mkblog.cn','Referer': 'http://lab.mkblog.cn/wallpaper/',
'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA\
58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Mobile Safari/537.36'}

def GetCatDiv():
    r = requests.get(API_DIVDE, headers=HEADERS)
    r.encoding = "utf-8"
    js = json.loads(r.text)
    data = js['data']
    db = database.DatabaseControl(host='127.0.0.1', passwd='123456', user='ysl', dbname='mkpicture')
    if db.connect():
        for item in data:
            # print(item)
            sqli = '''INSERT INTO divnum(id,name,order_num,create_date) VALUES ({},"{}",{},"{}")'''.format(
                int(item['id']), item['name'], int(item['order_num']), item['create_time'])
            # print(sql)
            ri = db.insertInToDB(sqli)
            if ri[0]:
                #print(ri[1])
                pass
            else:
                #print(ri[1])
                sqlu = '''UPDATE divnum SET name="{}",order_num={},create_date="{}" WHERE id={}''' \
                    .format(item['name'], int(item['order_num']), item['create_time'], int(item['id']))
                ru = db.updateInToDB(sqlu)
                if ru[0]:
                    #print(ru[1])
                    pass
                else:
                    print("错误的数据")
                    pass
        db.commit()
        db.close()

def GetTotal(link):
    r = requests.get(url=link,headers=HEADERS)
    r.encoding = 'utf-8'
    js = json.loads(r.text)
    return js['total']

def FlushTotal():
    db = database.DatabaseControl(host='127.0.0.1', passwd='123456', user='ysl', dbname='mkpicture')
    db.connect()
    db.cursor.execute("SELECT id,name From divnum")
    data = db.cursor.fetchall()
    for item in data:
        # print(item[0],item[1])
        link = HOST + "api.php?cid={}".format(item[0])
        # print(link)
        # print(GetTotal(link))
        s = GetTotal(link)
        sql = '''update divnum SET total={} WHERE id={} '''.format(s, item[0])
        ru = db.updateInToDB(sql)
        if ru[0]:
            pass;
        else:
            print("error")
    db.commit()
    db.close()

def GenDataLink():
    db = database.DatabaseControl(host='127.0.0.1', passwd='123456', user='ysl', dbname='mkpicture')
    db.connect()
    db.cursor.execute("SELECT id,name,total From divnum")
    data = db.cursor.fetchall()
    print(data)
    for item in data:
        total = int(item[2])
        while total > 0:
            count = total
            total = total - 200
            if total < 0:
                total = 0
            else:
                count = LIMIT
            link = HOST + "api.php?cid={}&start={}&count={}".format(item[0], total, count)
            yield link

def getData2DB(url):
    def flushcolumn(db):
        c = ['id','class_id']
        db.cursor.execute("select COLUMN_NAME from information_schema.COLUMNS where table_name = 'content'")
        dbdata = db.cursor.fetchall()
        c.extend([x[0] for x in dbdata])
        return  c
    r = requests.get(url=url,headers=HEADERS)
    r.encoding="utf-8"
    js= json.loads(r.text)
    data = js['data']

    #db = select COLUMN_NAME from information_schema.COLUMNS where table_name = 'your_table_name';
    db = database.DatabaseControl(host='127.0.0.1', passwd='123456', user='ysl', dbname='mkpicture')
    db.connect()
    column=flushcolumn(db)
    for d in data:
        for k in d.keys():
            if k not  in column:
                sql = '''alter table content add {} TEXT default NULL'''.format(k)
                db.cursor.execute(sql)
                column = flushcolumn(db)
            if k in ['id','class_id']:
                continue
            sqli = '''insert into content(c_id,c_class_id) values ({},{})'''.format(d['id'],d['class_id'])
            sqlu = '''update content set {}="{}" where c_id={}'''.format(k,d[k],d['id'])
            print(sqlu)
            ri=db.insertInToDB(sqli)
            ru=db.updateInToDB(sqlu)

            #print(ru)
            if not ru:
                if not ri:
                    with open("log.txt", 'a') as f:
                        f.write("insert error : "+sqli)
                with open("log.txt", 'a') as f:
                    f.write("update error : " + sqli)
    db.commit()
    db.close()


if __name__ == '__main__':

    for url in GenDataLink():
        getData2DB(url)



