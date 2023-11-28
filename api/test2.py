'''
Author: shihan
Date: 2023-11-28 19:50:03
version: 1.0
description: 
'''
import psycopg as db

server_params = {'dbname': 'sf23',
                 'host': 'db.doc.ic.ac.uk',
                 'port': '5432',
                 'user': 'sf23',
                 'password': '3048=N35q4nEsm',
                 'client_encoding':'utf-8'}

conn = db.connect(**server_params)
curs = conn.cursor()

curs.execute('select * from user;')
rec = curs.fetchone()
print(rec)

conn.close()