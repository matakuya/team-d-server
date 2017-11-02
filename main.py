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

    def store_log(self, data):
        try:
            connection = MySQLdb.connect(**self.config)
            print("connect database")
            cursor = connection.cursor()
            cursor.execute("insert into log (user_id, temp, hot_cold)values (%s, %s, %s)", (data['user_id'], data['temp'], data['hot_cold']))
            connection.commit()
            print("Execute Query.")
        except MySQLdb.Error as e:
            print("SQL ERROR %d: %s" % (e.args[0], e.args[1]))
        finally:
            if connection: connection.close()
            print("Connection Closed.")

@app.route('/')
def index():
    return "Hello World!"

@app.route('/login')
def login():
    return ""

@app.route('/store', methods=['POST'])
def store_data():
    if request.headers['Content-Type'] == 'application/json':
        # POST paratemers
        content = request.json
        manager = DBManager()
        manager.store_log(content)
        return "success."
    else:
        return "Invalid Request."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
