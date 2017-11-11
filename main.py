#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import MySQLdb
import configparser
app = Flask(__name__)

class DBManager:
    def __init__(self):
        inifile = configparser.SafeConfigParser()
        inifile.read('./mysql.ini')
        # config = {'host' = '', 'user' = '', 'passwd' = '', 'db' = '', 'charset' = '', }
        self.config = inifile._sections['connect']
        self.query = {
            'month' : "select date_format(timestamp, \'%%Y-%%m\') AS time, count(*) as count from testtbl where value %s and event_type_id = %s group by date_format(timestamp, \'%%Y%%m\')",
            'day' : "select date_format(timestamp, \'%%Y-%%m-%%d\') AS time, count(*) as count from testtbl where value %s and event_type_id = %s group by date_format(timestamp, \'%%Y%%m%%d\')",
            'hour' : "select date_format(timestamp, \'%%Y-%%m-%%d %%H:00:00\') AS time, count(*) as count from testtbl where value %s and event_type_id = %s group by date_format(timestamp, \'%%Y%%m%%d%%H\')"
        }
        self.threshold ={
            'hot' : 50,
            'cold' : 5
        }
        self.inequality = {
            'hot' : '>=' + str(self.threshold['hot']),
            'cold' : '<=' + str(self.threshold['cold'])
        }
        self.num_recent_logs = 600

    def get_config(self):
        return self.config

    def evaluate_logs(self, id):
        logs = self.get_log(id)
        if not(logs):
            return None
        ave = 0
        for log in logs:
            ave += log["value"]
        ave = 1.0 * ave / self.num_recent_logs
        if ave >= self.threshold['hot']:
            evaluation = 'hot'
        elif ave <= self.threshold['cold']:
            evaluation = 'cold'
        else:
            evaluation = 'nomal'
        return {'event_type_id': id, 'ave': ave, 'evaluation': evaluation}

    def get_log(self, id):
        try:
            try:
                connection = MySQLdb.connect(**self.config)
                print("connect database")
                cursor = connection.cursor()
                cursor.execute("select * from testtbl where event_type_id = %s order by timestamp desc limit %s"%(id, self.num_recent_logs))
                print("Execute Query.")
            except MySQLdb.Error as e:
                print(e)
                return None
            rv = cursor.fetchall()
            if not(rv):
                return None
            payload = []
            content = {}
            for result in rv:
                content = {'event_type_id': result[0], 'value': result[1], 'timestamp': result[2]}
                payload.append(content)
                content = {}
            return payload
        finally:
            connection.close()
            print("Connection Closed.")

    def get_typed_log(self, id, date_type, temp_type):
        # Check Dict.
        if not(self.query.get(date_type)) or not(self.inequality.get(temp_type)):
            return None
        try:
            try:
                connection = MySQLdb.connect(**self.config)
                print("connect database")
                cursor = connection.cursor()
                cursor.execute(self.query[date_type]%(self.inequality[temp_type], id))
                print("Execute Query.")
            except MySQLdb.Error as e:
                print(e)
                return None
            rv = cursor.fetchall()
            if not(rv):
                return None
            payload = []
            content = {}
            for result in rv:
                content = {'time': result[0], 'count': result[1]}
                payload.append(content)
                content = {}
            return payload
        finally:
            connection.close()
            print("Connection Closed.")

@app.route('/login')
def login():
    return ""

@app.route('/logs/<id>', methods=['GET'])
def get_data(id):
    manager = DBManager()
    logs = manager.get_log(id)
    if not(logs):
        return jsonify({'status':'Error'})
    return jsonify({
        'status':'OK',
        'logs':logs
    })

@app.route('/typed_log', methods=['GET'])
def get_month_data():
    date_type = request.args.get('date_type')
    temp_type = request.args.get('temp_type')
    id = request.args.get('id')
    manager = DBManager()
    logs = manager.get_typed_log(id, date_type, temp_type)
    if not(logs):
        return jsonify({'status':'Error'})
    return jsonify({
        'status':'OK',
        'logs':logs
    })

@app.route('/evaluate/<id>', methods=['GET'])
def evaluate_data(id):
    manager = DBManager()
    evaluation = manager.evaluate_logs(id)
    if not(evaluation):
        return jsonify({'status':'Error'})
    return jsonify({
        'status':'OK',
        'evaluation':evaluation
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
