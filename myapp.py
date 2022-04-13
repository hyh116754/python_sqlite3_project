from crypt import methods
from flask import Flask, render_template, request
import sqlite3
import os

DATABASE = "./groceries.db"

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")  # route bind to function next line
def main():
    return render_template("index.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/plans")
def plans():
    conn = get_db_connection()
    sql = """SELECT C.plan_id, C.plan_name, plan_contents, C.plan_price
            FROM plan C
            LEFT JOIN (
                SELECT pid
                    ,GROUP_CONCAT(items, ';') AS plan_contents
                FROM (
                    SELECT A.plan_id AS pid
                        ,B.item_name || '(' || B.quantity || ')' AS items
                    FROM recipe A
                    LEFT JOIN item B ON B.item_id = A.item_id
                    )
                GROUP BY pid
                ) ON C.plan_id = pid;"""
    plan_data = conn.execute(sql).fetchall()
    conn.close()
    return render_template("plans.html", plan_data=plan_data)

@app.route("/items")
def items():
    conn = get_db_connection()
    sql = """SELECT item.item_id, item_name, quantity, num_fav
            FROM item
            LEFT JOIN (
                SELECT favourite_item.item_id AS id, count(user_id) AS num_fav
                FROM favourite_item
                GROUP BY id
            ) ON item.item_id = id
            ORDER BY num_fav DESC;""" 
    item_data = conn.execute(sql).fetchall()
    conn.close()
    return render_template("items.html", item_data=item_data)

@app.route("/users")
def users():
    conn = get_db_connection()
    sql = """SELECT user_id, first_name, last_name, date_registration
            FROM user 
            ORDER BY date_registration 
            LIMIT 3;"""
    user_data_top_three = conn.execute(sql).fetchall()
    user_data_all = conn.execute("SELECT user_id, first_name, last_name, email, address, date_registration FROM user;").fetchall()
    conn.close()
    return render_template("users.html", user_data_all=user_data_all, user_data_top_three=user_data_top_three)

@app.route("/users/<int:u_id>")
def user_subscriptions(u_id):
    conn = get_db_connection()
    sql = """SELECT A.user_id, first_name, last_name, A.plan_id, plan_name, plan_price, s_quantity
            FROM subscription A
            LEFT OUTER JOIN plan B ON A.plan_id = B.plan_id
            LEFT OUTER JOIN user C ON A.user_id = C.user_id
            WHERE A.user_id = """ + str(u_id) + ';'
    sql2 = """ SELECT B.item_name
            FROM favourite_item A
            LEFT OUTER JOIN item B ON A.item_id = B.item_id
            WHERE A.user_id = """ + str(u_id) + ';'
    user_page_data = conn.execute(sql).fetchall()
    user_fav = conn.execute(sql2).fetchall()
    conn.close()
    return render_template("user_page.html", user_page_data=user_page_data, user_fav=user_fav)
    
@app.route("/get", methods=['GET'])
def get_req():
    return "get this webpage."

if __name__ == "__main__":
    app.run(debug=True)