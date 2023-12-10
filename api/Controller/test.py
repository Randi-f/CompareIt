import psycopg as db
import configparser
"""
Author: shihan
Date: 2023-12-07 21:37:25
version: 1.0
description: 
"""


first_name = "Shihan"
last_name = "Fu"
config = configparser.ConfigParser()
config.read("dbtool.ini")
# generate unique user_id
sqlcommand = (
    "SELECT COUNT(*) AS row_count FROM my_user WHERE name = '"
    + first_name
    + " "
    + last_name
    + "';"
)
try:
    conn = db.connect(**config["connection"])
    curs = conn.cursor()
    curs.execute(sqlcommand)
    ret = curs.fetchone()
    print(ret[0] + 1)
except Exception as e:
    print(f"An error occurred: {e}")  # Log the error
finally:
    if "curs" in locals():
        curs.close()
    if "conn" in locals():
        conn.close()
