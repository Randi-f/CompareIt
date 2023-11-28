'''
Author: shihan
Date: 2023-11-07 21:00:43
version: 1.0
description: 
'''
import math
from flask import Flask, render_template


app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("login.html")
    # return "Hello , my new app!"