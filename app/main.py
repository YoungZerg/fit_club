import os
from flask import render_template, Blueprint, session, redirect, url_for, request, flash
from fit_club.database.db import fetch_query, user_profile_update, add_customer_to_class
from werkzeug.utils import secure_filename
from fit_club.misc.functions import allowed_file

UPLOAD_CUSTOMER_DIR = os.path.join('\\'.join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1]), r'static\images\uploads\customers')

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

@main.route('/edit-profile')
def edit_user_profile():
    if 'customer_id' not in session:
        return redirect(url_for('auth.signup'))
    
    user = session['customer_id']

    user_info_query = "SELECT name, email, tel_number, birth_date, address, postal_code, sex FROM customer WHERE id = %i;" % user
    fetched_user_info = fetch_query(user_info_query)[0]
    user_info = {"name": fetched_user_info[0],
                 "email": fetched_user_info[1],
                 "telephone": fetched_user_info[2],
                 "birth_date": fetched_user_info[3],
                 "address": fetched_user_info[4],
                 "postal_code": fetched_user_info[5],
                 "sex": fetched_user_info[6]}


    return render_template('edit.html', user_info = user_info)


@main.route('/save-changes', methods=["POST"])
def update_user_profile():
    user_id = session['customer_id']
    name = request.form.get('name')
    email = request.form.get('email')
    telephone = request.form.get('tel_number')
    birth_date = request.form.get('birth_date')
    address = request.form.get('address')
    postal_code = request.form.get('postal_code')
    sex = request.form.get('sex')

    if 'profile_pic' not in request.files:
        user_profile_update(user_id, name, email, telephone, birth_date, address, postal_code, sex, None)
        return redirect(url_for('main.user_page'))
    
    file = request.files['profile_pic']
    if file.filename == '':
        user_profile_update(user_id, name, email, telephone, birth_date, address, postal_code, sex, None)
        return redirect(url_for('main.user_page'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_CUSTOMER_DIR, filename)
        file.save(filepath)
        user_profile_update(user_id, name, email, telephone, birth_date, address, postal_code, sex, filename)

    return redirect(url_for('main.user_page'))



@main.route('/training_classes')
def all_classes():

    all_class_sessions_query = """
    SELECT training_session.id,
           training_session.start_time,
           training_session.end_time,
           training_session.room_number,
           class.name,
           trainer.name
    FROM training_session
    INNER JOIN class ON training_session.class = class.id
    INNER JOIN trainer ON training_session.trainer = trainer.id
    ORDER BY training_session.start_time;
    """

    all_class_sessions_raw = fetch_query(all_class_sessions_query)

    all_class_sessions = []

    for class_session in all_class_sessions_raw:
        class_session_info = {
            "session_id": class_session[0],
            "start_time": class_session[1],
            "end_time": class_session[2],
            "room_number": class_session[3],
            "class_name": class_session[4],
            "trainer_name": class_session[5],
        }
        all_class_sessions.append(class_session_info)


    return render_template('train_classes.html', all_class_sessions=all_class_sessions)


@main.route('/training_classes/<int:session_id>', methods=["GET", "POST"])
def apply_class(session_id):
    current_user = session['customer_id']

    is_user_in_train_session = "SELECT exists(SELECT 1 FROM cust_train_session WHERE training_session = %i AND customer = %i);" % (session_id, current_user)

    result = fetch_query(is_user_in_train_session)[0][0]

    if result:
        flash("You already parcitipate in that class")
        return redirect(url_for('main.all_classes'))
    
    add_customer_to_class(current_user, session_id)
    return redirect(url_for('main.all_classes'))


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


@main.route('/partnership')
def plans():
    return render_template('partnership.html')
