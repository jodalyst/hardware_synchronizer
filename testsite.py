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

AUTHENTICATION = False

def authorization(user,pword):
    if not AUTHENTICATION:
        return True 
    conn = sqlite3.connect('stuff.db')
    c = conn.cursor()
    c.execute('SELECT * FROM userstuff WHERE user=?',(user,))
    output = c.fetchone()
    pword_test = output[1]
    return pword_test == pword

@application.route("/hw_supervisor",methods=['GET','POST'])
def manage():
    try:
        pword = 'test'
        if request.method == 'GET':
            user = request.args.get('user')
            if AUTHENTICATION:
                pword = request.args.get('pword')
            action = request.args.get('command')
            if authorization(user,pword) and action =='status_query':
                conn = sqlite3.connect('hw_status.db')
                c = conn.cursor()
                c.execute('SELECT * FROM hw_status WHERE user=? ORDER BY rowid DESC LIMIT 1;', (user,))
                data = c.fetchone()
                state = data[1]
                hw_command = data[2]
                hw_response = data[3]
                server_analysis = data[4]
                timeo = data[5] 
                
                to_return = {'login':True,'state':state,'hw_command': hw_command, 'hw_response':hw_response, 'server_analysis': server_analysis, 'time': timeo}
                return jsonify(to_return)
            else:
                return jsonify({'login':False})
        elif request.method == 'POST': #POST
            user = request.form['user']
            if AUTHENTICATION:
                pword = request.form['pword'] 
            if authorization(user,pword):
                action = request.form['command']
                conn = sqlite3.connect('hw_status.db')
                c = conn.cursor()
                c.execute('SELECT * FROM hw_status WHERE user=? ORDER BY rowid DESC LIMIT 1;', (user,))
                data = c.fetchone()
                state = data[1]
                hw_command = data[2]
                hw_response = data[3]
                server_analysis = data[4]
                timeo = data[5] 
                # new
                if action == "reset":
                    state = 0
                elif state ==0:
                    if action =="hw_command_request":
                        hw_command = request.form['hw_comm']
                        state = 1
                        timeo = str(time.time())
                elif state == 1:
                    if action =="hw_command_retrieval":
                        state = 2
                elif state == 2:
                    if action=="hw_response_provide":
                        hw_response = request.form['hw_resp']
                        state = 3
                elif state == 3:
                    if action == "server_analysis_provide":
                        server_analysis = request.form['server_anal']
                        state = 0
                elif state == 4: #deprecated...not used any more (6/06/2017)
                    if action == "server_analysis_retrieval":
                        state = 0
                to_return = {'login':True,'state':state,'hw_command': hw_command, 'hw_response':hw_response, 'server_analysis': server_analysis, 'time': timeo}
                conn = sqlite3.connect('hw_status.db')
                c = conn.cursor()
                c.execute("""UPDATE hw_status SET state=?,hw_command=?,hw_response=?,server_analysis=?,time=? WHERE user = ?;""",(state,hw_command,hw_response,server_analysis,timeo,user))
                conn.commit()
                conn.close()
                conn = sqlite3.connect('hw_status_archive.db')
                c = conn.cursor()
                c.execute("INSERT INTO "+user+" VALUES (?,?,?,?,?,?)", (user, state, hw_command,hw_response,server_analysis,timeo))
                conn.commit()
                conn.close()
                return jsonify(to_return)
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

