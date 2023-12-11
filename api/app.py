import math
from flask import Flask, render_template, jsonify, request, session
from lxml import html
import requests
import psycopg as db
import configparser
import time

# import psycopg2 as db
import uuid
import hashlib
from openpyxl import Workbook
from dotenv import load_dotenv
import string
import smtplib
import random
import os
import http.client
import urllib
import json
from pip._vendor.distlib.compat import raw_input

# from Controller.website1_JD import send_request_JD
# from Controller.website2_WPH import send_request_WPH

app = Flask(__name__)
app.secret_key = "your_unique_and_secret_key"


def get_db_connection():
    # config = configparser.ConfigParser()
    # config.read("dbtool.ini")
    server_params = {
        "dbname": "sf23",
        "host": "db.doc.ic.ac.uk",
        "port": "5432",
        "user": "sf23",
        "password": "3048=N35q4nEsm",
        "client_encoding": "utf-8",
    }

    return db.connect(**server_params)
    # return db.connect(**config["connection"])


# home page for the app
@app.route("/")
def hello_world():
    return render_template("index.html")


# compare page for the app
@app.route("/keywordsubmit", methods=["POST"])
def keywordsubmit():
    keyword = request.form.get("keyword")
    products_list = send_request_JD(keyword)
    res = []
    result2 = send_request_WPH(keyword)
    return render_template("compare.html", result1=products_list, result2=result2)


# compare page for the app
@app.route("/keywordsubmit2", methods=["POST"])
def keywordsubmit2():
    keyword = request.form.get("keyword")

    res = send_request_WPH(keyword)
    res2 = send_request_JD(keyword)
    for r in res2:
        res.append(r)
    print(res)
    if len(res) > 0:
        return jsonify(res)
    else:
        return None  # 将数据以 JSON 格式返回给前端


@app.route("/comparev2")
def comparev2():
    return render_template("comparev2.html")


# login page
@app.route("/login")
def login():
    return render_template("login.html")


# login submit
@app.route("/login", methods=["POST"])
def submit():
    data = request.json
    user_id = data.get("user_id")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM my_user WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    conn.close()

    # Check if user is not None before accessing its elements
    if user is not None:
        # Print or log the relevant information
        print(password, user[6])
        input_encrypted_password = hashlib.md5(password.encode()).hexdigest()
        if input_encrypted_password == user[6]:
            if user[7] is True:
                session["user"] = user_id
                return jsonify({"message": "Login successful"})
            else:
                return jsonify({"message": "Email is not verified"}), 401
        else:
            return (
                jsonify({"message": "The password is incorrect"}),
                401,
            )
    else:
        return jsonify({"message": "User not found"}), 401


# register page
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
        encrypted_password = hashlib.md5(password.encode()).hexdigest()

        # generate unique user_id
        sqlcommand = (
            "SELECT COUNT(*) AS row_count FROM my_user WHERE name = '"
            + first_name
            + " "
            + last_name
            + "';"
        )
        try:
            conn = get_db_connection()
            curs = conn.cursor()
            curs.execute(sqlcommand)
            ret = curs.fetchone()
        except Exception as e:
            print(f"An error occurred: {e}")  # Log the error
        finally:
            if "curs" in locals():
                curs.close()
            if "conn" in locals():
                conn.close()

        # approach 1
        user_id = (first_name + last_name).lower() + (str)(ret[0] + 1)
        print(user_id)
        # approach 2
        # user_id_initials = (first_name[0] + last_name[0]).upper() + (ret[0]+1)
        # user_id_dob_part = dob[-2:]  # Last two digits of the year
        # user_id_postcode_part = postcode[-3:]  # Last three digits of the postcode
        # user_id = user_id_initials + user_id_dob_part + user_id_postcode_part

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
            encrypted_password,
            verification_token,
        )

        try:
            conn = get_db_connection()
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
            message="Please check your email to confirm your registration!\n\n",
        )
    else:
        return render_template("register.html")


# email verification
@app.route("/verify_email/<verification_token>")
def verify_email(verification_token):
    # You should implement logic here to check the verification token in your database
    # If the token is valid, update the 'email_verified' column for the user
    sqlcommand = (
        "UPDATE my_user SET email_verified = True WHERE verification_token = %s"
    )
    print(sqlcommand)

    try:
        conn = get_db_connection()
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


# function: send verification email
def send_verification_email(receiver_mail, verification_token, user_id):
    # Retrieve email configuration from environment variables
    # email = os.getenv("EMAIL")
    email = "price.project23@gmail.com"
    # password = os.getenv("PASSWORD")
    password = "dkto zovm nnwx csqo"

    # Construct the email message
    subject = "Please verify your email"
    # verification_link = (
    #     f"http://127.0.0.1:5000/verify_email/{verification_token}"  # check email!!
    # )
    verification_link = f"https://compare-it-lyart.vercel.app/verify_email/{verification_token}"  # check email!!
    message = (
        f"Welcome to CompareIt! \n\n Thank you for signing up! Your user id is: {user_id}."
        f"Your user id will be used to login in along with your chosen password.\n\n"
        f"Please click on the following link to verify your email:\n\n{verification_link} \n\n\n"
        f"CompareIt \n"
        f"South Kensington, London SW7 2AZ \n"
        f"Phone: (555) 555-5555\n"
        f"Email: price.project23@gmail.com\n"
    )
    text = f"Subject: {subject}\n\n{message}"

    # Send the email
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, receiver_mail, text)
    server.quit()

    print(f"Verification email has been sent to {receiver_mail}")


# Profile page
@app.route("/profile")
def profile():
    if "user" in session:
        username = session["user"]

        # Connect to the database
        try:
            conn = get_db_connection()
            curs = conn.cursor()

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
                    "dob": user[4],
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


# compare page
@app.route("/compare")
def compare():
    result1 = [
        ["?","?","?","?","?"]
    ]
    result2 = [
        ["?", "?", "?", "?", "?"],
        ["?", "?", "?", "?", "?"],
        ["?", "?", "?", "?", "?"],
    ]
    return render_template("compare.html", result1=result1, result2=result2)


# function send request to JD
def send_request_JD(keyword):
    # some frequent words can be stored
    if keyword == "sweater":
        ret = [
            [
                "望了型 高领毛衣男秋冬季加绒加厚韩版修身保暖秋衣男士针织衫羊男生打底毛衫线衣 黑色Watched high necked sweater for men in autumn and winter, plush and thickened Korean version, slim fit and warm autumn clothes for men, knitted sweater for sheep and boys, base sweater, black sweater",
                "望了型",
                "35",
                "https://img14.360buyimg.com/n0/jfs/t1/136281/30/30901/94370/632d50b3E1dd41fbb/b9c62196fa2ba5f6.jpg",
                "（加绒加厚）",
                "https://item.jd.com/10061294624394.html",
            ]
        ]
        return ret
    if "shirt" in keyword:
        ret = [
            [
                "畅登 短袖t恤男夏季宽松圆领卡通印花五分袖T恤潮百搭半袖学生上衣服Changdeng short-sleeved T-shirt men's summer loose round neck cartoon printed five-quarter sleeve T-shirt trendy versatile half-sleeved student tops",
                "畅登",
                "17",
                "https://img14.360buyimg.com/n0/jfs/t1/216924/32/15608/135408/62397f0dE7af14933/45faad5764c11018.jpg.avif",
                "孔雀蓝 L",
                "https://item.jd.com/29979454936.html",
            ]
        ]
        return ret
    if "nike" in keyword:
        #  CZ5847-100
        ret = [
            [
                "nikeNike耐克2021春秋新款男鞋DROP-TYPE运动休闲鞋板鞋CZ5847-100nikeNike 2021 spring and autumn new men's shoes DROP-TYPE sports and casual shoes CZ5847-100"
                "耐克",
                "159",
                "https://img14.360buyimg.com/n0/jfs/t1/234125/7/7113/80164/657468deF4cbe85c8/514963e3c4579b64.jpg.avif",
                "主图款 44.5",
                "https://item.jd.com/10020315162111.html",
            ]
        ]
        return ret
    products_list = []
    url = "https://search.jd.com/Search?keyword=" + keyword + "&enc=utf-8"
    response = requests.get(url)
    # Check the status code
    if response.status_code == 200:
        print("Request was successful!")
        print("Status code:", response.status_code)
    else:
        print("Request failed!")
        print("Status code:", response.status_code)

    response.encoding = "utf-8"
    html_doc = response.text
    # print(html_doc)
    selector = html.fromstring(html_doc)

    ul_list = selector.xpath('//div[@id="J_goodsList"]/ul/li')
    if len(ul_list) == 0:

        ret = [['API network error', 
                '-', 
                'please try again later', 
                'https://img-qn.51miz.com/preview/element/00/01/15/79/E-1157992-2ACF8A1A.jpg!/quality/90/unsharp/true/compress/true/format/jpg/fw/720', 
                'none', 
                '-']]
        return ret
        products_list.append(
            {
                "title": "network error",
                "price": "-",
                "link": "try later for JD goods",
                "store": "-",
                "referer": "JD",
            }
        )
        return products_list
    ret = []
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
        row = [title[0],store[0],price[0],'https://img-qn.51miz.com/preview/element/00/01/15/79/E-1157992-2ACF8A1A.jpg!/quality/90/unsharp/true/compress/true/format/jpg/fw/720','normal',"https:" + link[0]]
        # products_list.append(
        #     {
        #         "title": title[0],
        #         "price": price[0],
        #         "link": "https:" + link[0],
        #         "store": store[0],
        #         "referer": "JD",
        #     }
        # )
        products_list.append(row)

    return products_list


# function send request to WPH
def send_request_WPH(key_word):
    if key_word == "sweater":
        time.sleep(5)
        ret = [
            [
                "秋款SWEATER 女士百搭保暖圆领套头衫卫衣Autumn SWEATER Women's versatile warm round neck pullover hoodie",
                "adidas三叶草",
                "209",
                "http://h2.appsimg.com/a.appsimg.com/upload/merchandise/pdcvis/2021/11/09/45/0441a83b-4f00-45d1-9fd4-2f4b920b9d93.jpg",
                "微弹,常规,常规,常规",
                "https://detail.vip.com/detail-1712010589-6919644945043361949.html",
            ],
            [
                "BAMBI SWEATER女士舒适百搭款休闲运动圆领卫衣BAMBI SWEATER Women's Comfortable Versatile Casual Sports Round Neck Sweater",
                "adidas三叶草",
                "219",
                "http://h2.appsimg.com/a.appsimg.com/upload/merchandise/pdcvis/2023/08/31/129/92c4f49f-0c9c-4236-bd80-8ea5f32c8521.jpg",
                "微弹,常规,常规,常规",
                "https://detail.vip.com/detail-1711231437-6920534809724224269.html",
            ],
            [
                "SWEATER女士舒适耐磨运动休闲半高领卫衣SWEATER Women's Comfortable and Durable Sports Casual Half High Collar Sweater",
                "adidas三叶草",
                "405",
                "http://h2.appsimg.com/a.appsimg.com/upload/merchandise/pdcvis/2023/08/16/75/33c9218c-db24-479e-b7c6-1b50730dff49.jpg",
                "宽松,常规,运动风,春/秋",
                "https://detail.vip.com/detail-1711326373-6920507049491323717.html",
            ],
        ]
        return ret
    # folder_path = "../vip_res"
    # os.makedirs(folder_path, exist_ok=True)
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
        "sort": "1",
        "pageOffset": "0",
        "channelId": "1",
        "gPlatform": "PC",
        "batchSize": "120",
        "_": "1689250387620",
    }

    response = requests.get(url=url, params=data, headers=headers)
    products = [i["pid"] for i in response.json()["data"]["products"]]

    # workbook = Workbook()
    # sheet = workbook.active

    # header = ["标题", "品牌", "售价", "图片", "商品信息", "详情页"]
    # sheet.append(header)

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
            if len(min_price_row) < 3:
                min_price_row.append(row)

    # workbook.save("../vip_res/商品.xlsx")
    print(min_price_row)
    for i in range(3):
        translated = translate_to_english(min_price_row[i][0])
        print(translated)
        min_price_row[i][0] += str(translated)
        print(min_price_row[i][0])
    return min_price_row
    # workbook.save("../vip_res/商品.xlsx")
    # print("最低价商品" + min_price_row[0])
    # translated = translate_to_english(min_price_row[0])
    # print(translated)
    # min_price_row[0] += str(translated)
    # print(min_price_row)
    # return min_price_row


def translate_to_english(content):
    # 百度appid和密钥需要通过注册百度【翻译开放平台】账号后获得
    appid = "20231208001904336"  # 填写你的appid
    secretKey = "1BtHmA9RiYqLrq2VEnFm"  # 填写你的密钥

    httpClient = None
    myurl = "/api/trans/vip/translate"  # 通用翻译API HTTP地址

    fromLang = "auto"  # 原文语种
    toLang = "en"  # 译文语种
    salt = random.randint(32768, 65536)
    # 手动录入翻译内容，q存放
    # q = raw_input("please input the word you want to translate:")
    q = content
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = (
        myurl
        + "?appid="
        + appid
        + "&q="
        + urllib.parse.quote(q)
        + "&from="
        + fromLang
        + "&to="
        + toLang
        + "&salt="
        + str(salt)
        + "&sign="
        + sign
    )

    dst_value = "null"
    # 建立会话，返回结果
    try:
        httpClient = http.client.HTTPConnection("api.fanyi.baidu.com")
        httpClient.request("GET", myurl)
        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)
        print(result)
        first_translation = result["trans_result"][0]
        # Access the value associated with the 'dst' key
        dst_value = first_translation["dst"]
        print(dst_value)
        return dst_value

    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()
    return dst_value


if __name__ == "__main__":
    app.run()
