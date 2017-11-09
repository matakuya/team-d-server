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

    def get_config(self):
        return self.config

    def get_log(self, id):
        try:
            try:
                connection = MySQLdb.connect(**self.config)
                print("connect database")
                cursor = connection.cursor()
                cursor.execute("select * from testtbl where event_type_id = (%s)", (id))
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

@app.route('/login')
def login():
    return ""

@app.route('/log/<id>', methods=['GET'])
def get_data(id):
    manager = DBManager()
    logs = manager.get_log(id)
    if not(logs):
        return jsonify({'status':'Error'})
    return jsonify({
        'status':'OK',
        'logs':logs
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
