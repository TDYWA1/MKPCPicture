import requests
import json
import database
import datetime

UPDATE_TIME=None
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

def GenDataLink(divn):
    db = database.DatabaseControl(host='127.0.0.1', passwd='123456', user='ysl', dbname='mkpicture')
    db.connect()
    db.cursor.execute("SELECT id,name,total From divnum")
    data = db.cursor.fetchall()
    db.close()
    print(data)
    for item in data:
        total = int(item[2])
        if int(item[0]) != divn:
            continue
        start = 0
        while True:
            # count = total
            # total = total - 200
            # if total < 0:
            #     total = 0
            # else:
            #     count = LIMIT
            # link = HOST + "api.php?cid={}&start={}&count={}".format(item[0], total, count)
            # yield link
            count = LIMIT
            if start > total:
                count = LIMIT - (start-total)
            link = HOST + "api.php?cid={}&start={}&count={}".format(item[0], start, count)
            yield link
            if start >= total:
                break
            else:
                start = start+200


def getData2DB(url):
    print(url)
    def flushcolumn(db):
        c = ['id','class_id']
        db.cursor.execute("select COLUMN_NAME from information_schema.COLUMNS where table_name = 'content'")
        dbdata = db.cursor.fetchall()
        c.extend([x[0] for x in dbdata])
        return  c
    r = requests.get(url = url,headers=HEADERS)
    r.encoding="utf-8"
    js= json.loads(r.text)
    data = js['data']

    #db = select COLUMN_NAME from information_schema.COLUMNS where table_name = 'your_table_name';
    db = database.DatabaseControl(host='127.0.0.1', passwd='123456', user='ysl', dbname='mkpicture')
    db.connect()
    column=flushcolumn(db)
    for d in data:
        utime = datetime.datetime.strptime(d['update_time'],"%Y-%m-%d %H:%M:%S")
        global UPDATE_TIME
        if utime<UPDATE_TIME:
            db.commit()
            db.close()
            return False
        for k in d.keys():
            if k not in column:
                sql = '''alter table content add {} TEXT default NULL'''.format(k)
                print(sql)
                try:
                    db.cursor.execute(sql)
                except Exception  as e:
                    print(e)
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
    return True

def getupdate_date():
    db = database.DatabaseControl(host='127.0.0.1', passwd='123456', user='ysl', dbname='mkpicture')
    db.connect()
    sql = "SELECT update_time from content order by update_time desc "
    db.cursor.execute(sql)
    ldt = db.cursor.fetchone()
    global UPDATE_TIME
    UPDATE_TIME= datetime.datetime.strptime(ldt[0], "%Y-%m-%d %H:%M:%S")



if __name__ == '__main__':
    getupdate_date()
    FlushTotal()
    listdivnum = [5,6,7,9,10,11,12,13,14,15,16,18,22,26,29,30,35,36]
    if UPDATE_TIME!=None:
        for i in listdivnum:
            for url in GenDataLink(i):
                status = getData2DB(url)
                if not status:
                    break




