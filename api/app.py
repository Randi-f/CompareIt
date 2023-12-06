import math
from flask import Flask, render_template, jsonify, request, session
from lxml import html
import requests
import psycopg2 as db
import os

# import psycopg2 as db
import uuid
import hashlib
from openpyxl import Workbook
from dotenv import load_dotenv
import string
import smtplib
import random

app = Flask(__name__)
app.secret_key = "your_unique_and_secret_key"


def get_db_connection():
    # server_params = {
    #     'dbname': 'nl1023',
    #     'host': 'db.doc.ic.ac.uk',
    #     'port': '5432',
    #     'user': 'nl1023',
    #     'password': 'aFZK-3CzFH*j3y',
    #     'client_encoding': 'utf-8'
    # }
    server_params = {
        "dbname": "sf23",
        "host": "db.doc.ic.ac.uk",
        "port": "5432",
        "user": "sf23",
        "password": "3048=N35q4nEsm",
        "client_encoding": "utf-8",
    }
    return db.connect(**server_params)


# homepage route for the app
@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/keywordsubmit", methods=["POST"])
def keywordsubmit():
    keyword = request.form.get("keyword")
    products_list = send_request(keyword)
    # if(products_list):

    result2 = vipapi(keyword)
    # print(products_list[0])
    return render_template("compare.html", result1=products_list[0], result2=result2)
    # return products_list[0]


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def submit():
    data = request.json

    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()

    cursor = conn.cursor()

    query = "SELECT * FROM my_user WHERE user_id = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    conn.close()

    # Check if user is not None before accessing its elements
    if user is not None:
        # Print or log the relevant information
        print(password, user[6])

        if password == user[6]:
            if user[7] is True:
                session["user"] = username
                return jsonify({"message": "Login successful"})
            else:
                return jsonify({"message": "Email is not verified"}), 401
        else:
            return (
                jsonify(
                    {"message": "The password is incorrect"}
                ),
                401,
            )
    else:
        return jsonify({"message": "User not found"}), 401


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        full_name = first_name + " " + last_name
        gender = request.form["gender"]
        email = request.form["email"]
        dob = request.form["dob"]
        postcode = request.form["postcode"]
        password = request.form["password"]

        user_id_initials = (first_name[0] + last_name[0]).upper()
        user_id_dob_part = dob[-2:]  # Last two digits of the year
        user_id_postcode_part = postcode[-3:]  # Last three digits of the postcode
        user_id = user_id_initials + user_id_dob_part + user_id_postcode_part

        verification_token = "".join(
            random.choices(string.ascii_letters + string.digits, k=32)
        )

        sqlcommand = """
            INSERT INTO my_user (user_id, name, gender, email, dob, postcode, password, email_verified, verification_token) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, False, %s)
        """

        values = (
            user_id,
            full_name,
            gender,
            email,
            dob,
            postcode,
            password,
            verification_token,
        )

        server_params = {
            "dbname": "sf23",
            "host": "db.doc.ic.ac.uk",
            "port": "5432",
            "user": "sf23",
            "password": "3048=N35q4nEsm",
            "client_encoding": "utf-8",
        }

        try:
            conn = db.connect(**server_params)
            curs = conn.cursor()
            curs.execute(sqlcommand, values)
            conn.commit()  # Commit to save changes
            send_verification_email(email, verification_token, user_id)
            message = "Registration successful"
        except Exception as e:
            print(f"An error occurred: {e}")  # Log the error
            message = "Registration failed due to a technical issue."
        finally:
            if "curs" in locals():
                curs.close()
            if "conn" in locals():
                conn.close()

        return render_template(
            "registration_result.html",
            message="Please check your email to confirm your registration",
        )
    else:
        return render_template("register.html")


@app.route("/verify_email/<verification_token>")
def verify_email(verification_token):
    # You should implement logic here to check the verification token in your database
    # If the token is valid, update the 'email_verified' column for the user
    sqlcommand = (
        "UPDATE my_user SET email_verified = True WHERE verification_token = %s"
    )
    print(sqlcommand)

    server_params = {
        "dbname": "sf23",
        "host": "db.doc.ic.ac.uk",
        "port": "5432",
        "user": "sf23",
        "password": "3048=N35q4nEsm",
        "client_encoding": "utf-8",
    }

    try:
        conn = db.connect(**server_params)
        curs = conn.cursor()
        curs.execute(sqlcommand, (verification_token,))
        conn.commit()  # Commit to save changes
        message = "Registration successful"
    except Exception as e:
        print(f"An error occurred: {e}")  # Log the error
        message = "Registration failed due to a technical issue."
    finally:
        if "curs" in locals():
            curs.close()
        if "conn" in locals():
            conn.close()
    # For now, let's assume it's successful
    return render_template("email_verified.html")


def send_verification_email(receiver_mail, verification_token, user_id):
    # Retrieve email configuration from environment variables
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    # Construct the email message
    subject = "Please verify your email"
    verification_link = (
        f"http://127.0.0.1:5000/verify_email/{verification_token}"  # check email!!
    )
    message = (
        f"Welcome to CompareIt! \n\n Thank you for signing up! Your user id is: {user_id}."
        f"Your user id will be used to login in along with your chosen password.\n\n"
        f"Please click on the following link to verify your email:\n\n{verification_link}"
    )
    text = f"Subject: {subject}\n\n{message}"

    # Send the email
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, receiver_mail, text)
    # server.sendmail(email, receiver_mail, text)
    server.quit()

    print(f"Verification email has been sent to {receiver_mail}")


# Profile route
@app.route("/profile")
def profile():
    server_params = {
        "dbname": "sf23",
        "host": "db.doc.ic.ac.uk",
        "port": "5432",
        "user": "sf23",
        "password": "3048=N35q4nEsm",
        "client_encoding": "utf-8",
    }
    if "user" in session:
        username = session["user"]

        # Connect to the database
        try:
            conn = db.connect(**server_params)
            curs = conn.cursor()
            # curs.execute(sqlcommand, values)
            # conn.commit()  # Commit to save changes

            # config=configparser.ConfigParser()
            # config.read('dbtool.ini')

            # conn = db.connect(**config['connection'])
            # curs = conn.cursor()

            # Perform the profile query to fetch user data based on the username
            curs.execute("SELECT * FROM my_user WHERE user_id = %s", (username,))
            user = curs.fetchone()

            # Check if the user is found
            if user:
                # The user is a tuple; you may want to convert it to a dictionary for easier handling
                user_dict = {
                    "username": user[1],
                    "email": user[3],
                    "gender": user[2],
                    "postcode": user[5],
                    # Add other properties as needed
                }

                return render_template("profile.html", user=user_dict)
            else:
                return "User not found."
        except Exception as e:
            print(f"An error occurred: {e}")  # Log the error
            return "Error fetching profile data."
        finally:
            if "curs" in locals():
                curs.close()
            if "conn" in locals():
                conn.close()
    else:
        return "You are not logged in. Please log in."


@app.route("/compare")
def compare():
    return render_template("compare.html", result1={}, result2={})


def send_request(keyword):
    products_list = []
    """ 爬取京东的商品数据 """

    url = "https://search.jd.com/Search?keyword=" + keyword + "&enc=utf-8"

    respons = requests.get(url)
    respons.encoding = "utf-8"
    html_doc = respons.text

    selector = html.fromstring(html_doc)

    ul_list = selector.xpath('//div[@id="J_goodsList"]/ul/li')

    for li in ul_list:
        title = li.xpath(
            'div/div[@class="p-name p-name-type-2"]/a/em/text() | '
            'div/div[@class="p-name"]/a/@title'
        )

        link = li.xpath(
            'div/div[@class="p-name p-name-type-2"]/a/@href | '
            'div/div[@class="p-name"]/a/@href'
        )

        price = li.xpath(
            'div/div[@class="p-price"]/strong/i/text() | '
            'div/div[@class="p-price"]/strong/i/text()'
        )

        store = li.xpath(
            'div/div[@class="p-shop"]//a/text() | ' 'div//a[@class="curr-shop"]/@title'
        )
        products_list.append(
            {
                "title": title[0],
                "price": price[0],
                "link": "https:" + link[0],
                "store": store[0],
                "referer": "JD",
            }
        )

    return products_list


def vipapi(key_word):
    folder_path = "../vip_res"

    os.makedirs(folder_path, exist_ok=True)

    headers = {
        "Referer": "https://category.vip.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
    }

    url = "https://mapi.vip.com/vips-mobile/rest/shopping/pc/search/product/rank"
    data = {
        "app_name": "shop_pc",
        "app_version": "4.0",
        "warehouse": "VIP_HZ",
        "fdc_area_id": "104103101",
        "client": "pc",
        "mobile_platform": "1",
        "province_id": "104103",
        "api_key": "70f71280d5d547b2a7bb370a529aeea1",
        "user_id": "",
        "mars_cid": "1689245318776_e2b4a7b51f99b3dd6a4e6d356e364148",
        "wap_consumer": "a",
        "standby_id": "nature",
        "keyword": key_word,
        "lv3CatIds": "",
        "lv2CatIds": "",
        "lv1CatIds": "",
        "brandStoreSns": "",
        "props": "",
        "priceMin": "",
        "priceMax": "",
        "vipService": "",
        "sort": "0",
        "pageOffset": "0",
        "channelId": "1",
        "gPlatform": "PC",
        "batchSize": "120",
        "_": "1689250387620",
    }

    response = requests.get(url=url, params=data, headers=headers)
    products = [i["pid"] for i in response.json()["data"]["products"]]

    workbook = Workbook()
    sheet = workbook.active

    header = ["标题", "品牌", "售价", "图片", "商品信息", "详情页"]
    sheet.append(header)

    min_price_row = []
    for i in range(0, len(products), 50):
        product_id = ",".join(products[i : i + 50])
        link = (
            "https://mapi.vip.com/vips-mobile/rest/shopping/pc/product/module/list/v2"
        )
        params = {
            "app_name": "shop_pc",
            "app_version": "4.0",
            "warehouse": "VIP_HZ",
            "fdc_area_id": "104103101",
            "client": "pc",
            "mobile_platform": "1",
            "province_id": "104103",
            "api_key": "70f71280d5d547b2a7bb370a529aeea1",
            "user_id": "",
            "mars_cid": "1689245318776_e2b4a7b51f99b3dd6a4e6d356e364148",
            "wap_consumer": "a",
            "productIds": product_id,
            "scene": "search",
            "standby_id": "nature",
            "extParams": '{"stdSizeVids":"","preheatTipsVer":"3","couponVer":"v2","exclusivePrice":"1","iconSpec":"2x","ic2label":1,"superHot":1,"bigBrand":"1"}',
            "context": "",
            "_": "1689250387628",
        }
        json_data = requests.get(url=link, params=params, headers=headers).json()

        for index in json_data["data"]["products"]:
            attr = ",".join([j["value"] for j in index["attrs"]])
            row = [
                index["title"],
                index["brandShowName"],
                index["price"]["salePrice"],
                index["squareImage"],
                attr,
                f'https://detail.vip.com/detail-{index["brandId"]}-{index["productId"]}.html',
            ]
            if len(min_price_row) == 0 or float(row[2]) < float(min_price_row[2]):
                min_price_row = row
            sheet.append(row)

    workbook.save("../vip_res/商品.xlsx")
    print(min_price_row[0])
    return min_price_row

    """
                        <th>title</th>
                        <th>link</th>
                        <th>price</th>
                        <th>manufacturer</th>
                        <th>other</th>"""
    """
    ['COURT LEGACY 轻便休闲 小白鞋 男子板鞋',
    'Nike', 
    '198',
    'http://h2.appsimg.com/a.appsimg.com/upload/merchandise/pdcvis/611861/2023/0612/178/4b8049eb-ea43-4631-8e1d-e83f44c4b5f1.jpg', 
    '板鞋/小白鞋,平底,无,适中', 
    'https://detail.vip.com/detail-1710618487-6920028890971952983.html']"""
