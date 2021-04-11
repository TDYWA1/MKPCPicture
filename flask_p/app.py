from flask import *
import pymysql

app = Flask("app")
app.debug = True


def initDB():
    try:
        db = pymysql.connect(user="ysl", password="123456", host="127.0.0.1", database="mkpicture")
    except Exception as e:
        print("connect to database error")
        return
    return db


def testdata(db):
    cursor = db.cursor()
    cursor.execute("SELECT url from content LIMIT 30")
    return cursor.fetchall()
    pass


def GetNav(db):
    cursor = db.cursor()
    cursor.execute("SELECT id,name from divnum limit 14")
    return cursor.fetchall()


@app.route('/', methods=['GET', 'POST'])
def home():
    db = initDB()
    d = testdata(db)
    d = [x[0] for x in d]
    n = GetNav(initDB())
    n0 = [x[0] for x in n]
    n1 = [x[1] for x in n]

    return render_template('home.html', urls=d, navs=n, page=1)


def catdiv(db, id, page):
    cursor = db.cursor()
    page = (page ) * 32
    # cursor.execute("SELECT url from content WHERE c_class_id={} LIMIT 32 offset {}".format(id, page))
    cursor.execute("SELECT url from content WHERE c_class_id={} order by update_time desc ".format(id))
    return cursor.fetchmany(page)[-32:]


@app.route('/cat/<int:catid>/<int:page>')
def catfetch(catid, page):
    if page == 0:
        page = 1
    db = initDB()
    d = catdiv(db, catid, page)
    d = [x[0] for x in d]
    n = GetNav(initDB())
    n0 = [x[0] for x in n]
    n1 = [x[1] for x in n]

    return render_template('home.html', urls=d, navs=n, page=page, catid=catid)


if __name__ == '__main__':
    # print(GetNav(initDB()))
    app.run(host="192.168.1.2",port=5000)
