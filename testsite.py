from flask import Flask
from flask import request
from flask import jsonify
import datetime
import time
import sqlite3
import traceback
import random
from werkzeug.debug import DebuggedApplication

application = Flask(__name__)
application.debug=True
application.wsgi_app = DebuggedApplication(application.wsgi_app, True)

@application.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

@application.route("/math",methods=['GET','POST'])
def test():
    thing = request.args.get('user')
    return """<h1 style='color:blue'>Title</h1><p>You name is {}.  That's great.</p>""".format(thing)

@application.route("/logger",methods=['GET','POST'])
def harvest():
    try: 
        #user = request.args.get('user')
        user = request.form['user']
        mousex = request.form['mouseX']
        mousey = request.form['mouseY']
        scroll = request.form['scroll']
        focus = request.form['focus']
        stuff = (mousex,mousey,scroll,focus)
        timeo = str(datetime.datetime.now())
        conn = sqlite3.connect('info1.db')
        c = conn.cursor()
        c.execute('''INSERT INTO things VALUES (?,?,?)''',(user,timeo,str(stuff)))
        conn.commit()
        conn.close()
        return """all good"""
    except:
        trace = traceback.format_exc()
        return("<pre>" + trace + "</pre>"), 500

def authorization(user,pword):
    conn = sqlite3.connect('stuff.db')
    c = conn.cursor()
    c.execute('SELECT * FROM userstuff WHERE user=?',(user,))
    output = c.fetchone()
    pword_test = output[1]
    return pword_test == pword

@application.route("/hw_supervisor",methods=['GET','POST'])
def manage():
    try: 
        if request.method == 'GET':
            user = request.args.get('user')
            pword = request.args.get('pword')
            if authorization(user,pword):
                conn = sqlite3.connect('hw_status.db')
                c = conn.cursor()
                c.execute('SELECT * FROM hw_status WHERE user=? ORDER BY rowid DESC LIMIT 1;', (user,))
                data = c.fetchone()
                status = data[1]
                code_to_run = data[4]
                to_return = {'login':True,'status':'nothing','dbstate':str(data),'command':''}
                if status == 1:
                    to_return['command']=code_to_run
                    c.execute("""UPDATE hw_status SET status=2 WHERE user = ?;""",(user,))
                conn.commit()
                conn.close()
                return jsonify(to_return)
            else:
                return jsonify({'login':False})
        elif request.method == 'POST': #POST
            user = request.form['user']
            pword = request.form['pword'] 
            if authorization(user,pword):
                action = request.form['action']
                if action == 'test_request':
                    conn = sqlite3.connect('hw_status.db')
                    c = conn.cursor()
                    c.execute('SELECT * FROM hw_status WHERE user=? ORDER BY rowid DESC LIMIT 1;', (user,))
                    data = c.fetchone()
                    status = data[1]
                    if status != 0:
                        return jsonify({'login':True,'status':'Incomplete Test Already Running','dbstate':str(data),'response':''})

                    timeo = str(time.time())
                    code_to_run = request.form['test_code']
                    ticket = int(10000*random.random())
                    c.execute("""UPDATE hw_status SET status=?,ticket=?,time=?,to_execute=?,output='' WHERE user = ?;""",(1,ticket,timeo,code_to_run,user))
                    conn.commit()
                    conn.close()
                    conn = sqlite3.connect('hw_status_archive.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO "+user+" VALUES (?,?,?,?,?,?)", (user, 1, ticket,timeo,code_to_run, ''))
                    conn.commit()
                    conn.close()
                    return jsonify({'login':True,'status':'Test Submitted','dbstate':str(data),'response':''})
                elif action == 'status_query':
                    conn = sqlite3.connect('hw_status.db')
                    c = conn.cursor()
                    c.execute('SELECT * FROM hw_status WHERE user=? ORDER BY rowid DESC LIMIT 1;', (user,))
                    data = c.fetchone()
                    status = data[1]
                    message = ""
                    response = ""
                    if status ==1:
                        message= "Queued..."
                    elif status ==2:
                        message= "Running..."
                    elif status ==3:
                        c.execute("""UPDATE hw_status SET status=0 WHERE user = ?;""",(user,))
                        message = "Done: "
                        response = data[5]
                    else:
                        message = "Error"
                    conn.commit()
                    conn.close()
                    return jsonify({'login':True,'status':message,'dbstate':str(data),'response':response})
                elif action == 'reset':
                    conn = sqlite3.connect('hw_status.db')
                    c = conn.cursor()
                    c.execute('SELECT * FROM hw_status WHERE user=? ORDER BY rowid DESC LIMIT 1;', (user,))
                    data = c.fetchone()
                    timeo = str(time.time())
                    c.execute("""UPDATE hw_status SET status=?,time=?,to_execute='',output=? WHERE user = ?;""",(0,timeo,'',user))
                    conn.commit()
                    conn.close()
                    conn = sqlite3.connect('hw_status_archive.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO "+user+" VALUES (?,?,?,?,?,?)", (user, 0, 0,timeo, '',''))
                    conn.commit()
                    conn.close()
                    return jsonify({'login':True,'status':"Process Removed",'dbstate':str(data),'response':''})
                elif action == 'test_response':
                    conn = sqlite3.connect('hw_status.db')
                    c = conn.cursor()
                    c.execute('SELECT * FROM hw_status WHERE user=? ORDER BY rowid DESC LIMIT 1;', (user,))
                    data = c.fetchone()
                    status = data[1]
                    if status != 2:
                        return jsonify({'login':True,'status':"Test Aborted",'dbstate':str(data),'response':""})
                    timeo = str(time.time())
                    ticket = data[2]
                    response = request.form['response']
                    c.execute("""UPDATE hw_status SET status=?,time=?,to_execute='',output=? WHERE user = ?;""",(3,timeo,response,user))
                    conn.commit()
                    conn.close()
                    conn = sqlite3.connect('hw_status_archive.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO "+user+" VALUES (?,?,?,?,?,?)", (user, 3, ticket,timeo, '',response))
                    conn.commit()
                    conn.close()
                    return jsonify({'login':True,'status':"Concluded",'dbstate':str(data),'response':response})
                else:
                    return jsonify({'login':False})
        return jsonify({'login':False})
    except:
        trace = traceback.format_exc()
        return("<pre>" + trace + "</pre>"), 500


@application.errorhandler(500)
def internal_error(exception):
    """Show traceback in the browser when running a flask app on a production server.
    By default, flask does not show any useful information when running on a production server.
    By adding this view, we output the Python traceback to the error 500 page.
    """
    trace = traceback.format_exc()
    return("<pre>" + trace + "</pre>"), 500



if __name__ == "__main__":
    application.run(host='0.0.0.0')

