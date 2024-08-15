from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from fit_club.database.db import fetch_query, add_new_user, verify_password, add_new_customer_cart, add_new_customer_membership
from argon2 import PasswordHasher

auth = Blueprint('auth', __name__, static_folder = '../static', template_folder = '../templates')

ph = PasswordHasher()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        fetch_user = "SELECT id, profile_pic_path, password_hash FROM customer WHERE email = %s;"

        user = fetch_query(fetch_user, (email,))

        if (len(user) == 0) or (len(user) != 0 and not verify_password(user[0][2], password)):
            flash('Пожалуйста, проверьте введенные данные и попытайтесь войти снова.')
            return redirect(url_for('auth.login'))
        
        session['customer_id'] = user[0][0]
        session['profile_picture'] = user[0][1]
        return redirect(url_for('main.home'))
    
    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        address = request.form.get("address")
        birth_date = request.form.get("birthdate")
        telephone = request.form['telephone']
        postalcode = request.form['postalcode']
        sex = request.form['sex']

        params_list = [email, name, password, address, birth_date, telephone, postalcode, sex]

        if any(param is None for param in params_list):
            flash("Пожалуйста, заполните все поля.")
            return redirect(url_for('auth.signup'))

        fetch_user_query = "SELECT exists (SELECT 1 FROM customer WHERE email = %s LIMIT 1);"

        result = fetch_query(fetch_user_query, (email,))[0][0]

        if result:
            flash('Пользователь с такой почтой уже существует.')
            return redirect(url_for('auth.signup'))
    
        hashed_password = ph.hash(password)

        add_new_user(email, name, hashed_password, address, birth_date, telephone, postalcode, sex)

        last_added_user_query = "SELECT MAX(id) FROM customer;"

        last_added_user_id = fetch_query(last_added_user_query)[0][0]

        add_new_customer_cart(last_added_user_id)
        add_new_customer_membership(last_added_user_id)

        return redirect(url_for('auth.login'))

    return render_template('signup.html')


@auth.route('/logout')
def logout():
    session.pop('customer_id', None)
    return redirect(url_for('main.home'))
