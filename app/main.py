from flask import render_template, Blueprint, session, redirect, url_for, request
from fit_club.database.db import fetch_query

main = Blueprint('main', __name__, static_folder = '../static', template_folder = '../templates')

@main.route('/')
def home():
    if 'customer_id' in session:
        user = session['customer_id']

        user_name_query = "SELECT name FROM customer WHERE id = %i;" % user

        username = fetch_query(user_name_query)[0][0]

        return render_template('index.html', username=username)
    return render_template('index.html')

@main.route('/profile')
def user_page():
    if 'customer_id' in session:
        user = session['customer_id']

        user_info_query = "SELECT name, email, tel_number, birth_date, address, postal_code, sex, profile_pic_path FROM customer WHERE id = %i;" % user

        fetched_user_info = fetch_query(user_info_query)[0]

        user_info = {"name": fetched_user_info[0],
                     "email": fetched_user_info[1],
                     "telephone": fetched_user_info[2],
                     "birth_date": fetched_user_info[3],
                     "address": fetched_user_info[4],
                     "postal_code": fetched_user_info[5],
                     "sex": fetched_user_info[6],
                     "profile_pic_path": fetched_user_info[7]}

        
        return render_template('profile.html', user_info=user_info) 

    return redirect(url_for('auth.signup'))

@main.route('/edit-profile', methods=["GET", "POST"])
def edit_user_profile():
    if request.method == "POST":
        return redirect(url_for("main.user_page"))

    user = session['customer_id']

    user_info_query = "SELECT name, email, tel_number, birth_date, address, postal_code, sex, profile_pic_path FROM customer WHERE id = %i;" % user
    fetched_user_info = fetch_query(user_info_query)[0]
    user_info = {"name": fetched_user_info[0],
                 "email": fetched_user_info[1],
                 "telephone": fetched_user_info[2],
                 "birth_date": fetched_user_info[3],
                 "address": fetched_user_info[4],
                 "postal_code": fetched_user_info[5],
                 "sex": fetched_user_info[6],
                 "profile_pic_path": fetched_user_info[7]}


    return render_template('edit.html', user_info = user_info)

@main.route('/equipment')
def shop_page():
    return render_template('equipment.html')

@main.route('/profile/cart')
def user_cart():
    return render_template('cart.html')

@main.route('/profile/order-history')
def user_order_history():
    return render_template('order_history.html')

@main.route('/plans')
def training_plans():
    return render_template('plans.html')
