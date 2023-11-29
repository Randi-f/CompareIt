'''
Author: shihan
Date: 2023-11-28 19:41:59
version: 1.0
description: 
'''
import psycopg2

try:
 # create a connection to postgres
    connection = psycopg2.connect(user="sf23",
    password="3048=N35q4nEsm",
    host="db.doc.ic.ac.uk",
    port="5432",
    database="sf23")
    cursor = connection.cursor()
    # using SQL
    query = "select * from user"
    cursor.execute(query)
    # loop through and print all records from query
    records = cursor.fetchall()
    for record in records:
        print(record)
    # Error handling
except (Exception, psycopg2.Error) as error:
    print("Error while fetching data from Postgres", error)
# Remember to close the DB connection
finally:
    # closing database connection.
    if connection:
        cursor.close()
    connection.close()
    print("Postgres connection is closed")