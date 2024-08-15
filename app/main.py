import os
from flask import render_template, Blueprint, session, redirect, url_for, request, flash
from fit_club.database.db import fetch_query, user_profile_update, add_customer_to_class, execute_query, create_new_order, add_order_items
from werkzeug.utils import secure_filename
from fit_club.misc.functions import allowed_file
from datetime import datetime


UPLOAD_CUSTOMER_DIR = os.path.join('\\'.join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1]), r'static\images\uploads\customers')

main = Blueprint('main', __name__, static_folder = '../static', template_folder = '../templates')

@main.route('/')
def home():
    if 'customer_id' in session:
        user = session['customer_id']

        user_name_query = "SELECT name, profile_pic_path FROM customer WHERE id = %s;"

        username, profile_picture = fetch_query(user_name_query, (user,))[0]

        return render_template('index.html', username=username, profile_picture=profile_picture)
    return render_template('index.html')

@main.route('/profile')
def user_page():
    if 'customer_id' in session:
        user = session['customer_id']

        user_info_query = """
        SELECT
               customer.name,
               customer.email,
               customer.tel_number,
               customer.birth_date,
               customer.address,
               customer.postal_code,
               customer.sex,
               customer.profile_pic_path,
               membership.end_date
        FROM membership
        INNER JOIN customer ON membership.customer = customer.id
        WHERE customer.id = %s;
        """

        fetched_user_info = fetch_query(user_info_query, (user,))[0]

        user_info = {"name": fetched_user_info[0],
                     "email": fetched_user_info[1],
                     "telephone": fetched_user_info[2],
                     "birth_date": fetched_user_info[3],
                     "address": fetched_user_info[4],
                     "postal_code": fetched_user_info[5],
                     "sex": fetched_user_info[6],
                     "profile_pic_path": fetched_user_info[7],
                     "expiration_date": fetched_user_info[8]}
        
        is_customer_plan_null_query = "SELECT subscription FROM membership WHERE customer = %s;"

        customer_plan = fetch_query(is_customer_plan_null_query, (user,))[0][0]

        current_plan_name = ""

        if not customer_plan:
            current_plan_name = "Тариф отсутствует"
        else:
            fetch_current_plan_name = """
            SELECT subscription.plan_name
            FROM membership
            INNER JOIN subscription ON membership.subscription = subscription.id
            WHERE membership.customer = %s;
            """
            current_plan_name = fetch_query(fetch_current_plan_name, (user,))[0][0]

        return render_template('profile.html', user_info=user_info, plan_name=current_plan_name) 

    return redirect(url_for('auth.signup'))

@main.route('/edit-profile')
def edit_user_profile():
    if 'customer_id' not in session:
        return redirect(url_for('auth.signup'))
    
    user = session['customer_id']

    user_info_query = "SELECT name, email, tel_number, birth_date, address, postal_code, sex FROM customer WHERE id = %s;"
    fetched_user_info = fetch_query(user_info_query, (user,))[0]
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

    is_user_in_train_session = "SELECT exists(SELECT 1 FROM cust_train_session WHERE training_session = %s AND customer = %s);"

    result = fetch_query(is_user_in_train_session, (session_id, current_user))[0][0]

    if result:
        flash("Вы уже присоединились к занятию.")
        return redirect(url_for('main.all_classes'))
    
    add_customer_to_class(current_user, session_id)
    return redirect(url_for('main.all_classes'))


@main.route('/equipment')
def shop_page():
    if 'customer_id' not in session:
        return redirect(url_for('auth.login'))
    
    fetch_all_equipment = """
        SELECT equipment.id, 
               equipment.name,
               equipment.price,
               equipment.equipment_pic_path
        FROM equipment
        INNER JOIN category
        ON equipment.category = category.id;
        """
    equipments = fetch_query(fetch_all_equipment)
    equipment_list = []
    for product in equipments:
        product_info = {
            "id": product[0],
            "name": product[1],
            "price": product[2],
            "picture": product[3]
        }
        equipment_list.append(product_info)


    fetch_all_categories = "SELECT id, name FROM category;"

    categories_raw = fetch_query(fetch_all_categories)

    categories = []

    for category in categories_raw:
        category_info = {
            "id": category[0],
            "name": category[1]
        }
        categories.append(category_info)

    
    return render_template('equipment.html', equipment_list=equipment_list, categories=categories)


@main.route('/equipment/filter-by-category/<int:category_id>')
def filter_by_category(category_id):

    fetch_items = """
    SELECT equipment.id, 
           equipment.name,
           equipment.price,
           equipment.equipment_pic_path
    FROM equipment
    INNER JOIN category
    ON equipment.category = category.id
    WHERE equipment.category =  %s;
    """
    equipments = fetch_query(fetch_items, (category_id,))
    equipment_list = []
    for product in equipments:
        product_info = {
            "id": product[0],
            "name": product[1],
            "price": product[2],
            "picture": product[3]
        }
        equipment_list.append(product_info)

    fetch_all_categories = "SELECT id, name FROM category;"

    categories_raw = fetch_query(fetch_all_categories)

    categories = []

    for category in categories_raw:
        category_info = {
            "id": category[0],
            "name": category[1]
        }
        categories.append(category_info)

    
    return render_template('equipment.html', equipment_list=equipment_list, categories=categories)

@main.route('/equipment/<int:product_id>')
def product_details(product_id):

    fetch_equipment_info = """
    SELECT equipment.id, equipment.name,
           equipment.description, equipment.price,
           equipment.equipment_pic_path,
           category.name
    FROM equipment
    INNER JOIN category
    ON equipment.category = category.id
    WHERE equipment.id = %s;
    """
    equipment_info = fetch_query(fetch_equipment_info, (product_id,))[0]

    equipment = {
        "id": equipment_info[0],
        "name": equipment_info[1],
        "description": equipment_info[2],
        "price": equipment_info[3],
        "picture": equipment_info[4],
        "category": equipment_info[5],
    }
    

    return render_template('product_details.html', equipment=equipment)

@main.route('/equipment/add-to-cart/<int:equipment_id>', methods=["POST"])
def add_to_cart(equipment_id):
    current_user = session['customer_id']

    customer_cart_id_query = "SELECT id FROM shopping_session WHERE customer = %s;"

    customer_cart_id = fetch_query(customer_cart_id_query, (current_user,))[0][0]

    check_cart_item_query = """
    SELECT id, quantity FROM cart_item WHERE shopping_session = %s AND equipment = %s;
    """

    cart_item_result = fetch_query(check_cart_item_query, (customer_cart_id, equipment_id))

    update_time = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")

    update_customer_cart_query = "UPDATE shopping_session SET modified_at = %s WHERE id = %s;"
    execute_query(update_customer_cart_query, (update_time, customer_cart_id))
    #if current item exists -> increment quantity
    if cart_item_result:
        cart_item_id, current_item_quantity = cart_item_result[0]

        current_item_quantity += 1

        update_item_quantity_query = """
        UPDATE cart_item
        SET quantity = %s, modified_at = %s WHERE id = %s;
        """
        execute_query(update_item_quantity_query, (current_item_quantity, update_time, cart_item_id))
    else:
        add_cart_item_query = """
        INSERT INTO cart_item(created_at, modified_at, shopping_session, equipment, quantity)
        VALUES (%s, %s, %s, %s, 1)
        """
        execute_query(add_cart_item_query, (update_time, update_time, customer_cart_id, equipment_id))

    flash('Товар был добавлен в корзину!')
    return redirect(url_for('main.product_details', product_id=equipment_id))


@main.route('/profile/cart')
def user_cart():

    if 'customer_id' not in session:
        return redirect(url_for('auth.login'))
    
    current_user = session['customer_id']

    fetch_customer_cart_items_query = """
    SELECT equipment.id,
           equipment.name,
           cart_item.quantity,
           equipment.price * cart_item.quantity AS total_price,
           equipment.description
    FROM cart_item
    INNER JOIN equipment
    ON cart_item.equipment = equipment.id
    WHERE cart_item.shopping_session = (SELECT id FROM shopping_session WHERE customer = %s);
    """

    customer_cart_items_raw = fetch_query(fetch_customer_cart_items_query, (current_user,))

    customer_cart_items = []

    for item in customer_cart_items_raw:
        item_info = {
            "item_id": item[0],
            "item_name": item[1],
            "item_quantity": item[2],
            "item_total_price": item[3],
            "item_description": item[4]
        }
        customer_cart_items.append(item_info)

    total_price = sum([item['item_total_price'] for item in customer_cart_items])


    return render_template('cart.html', customer_cart_items=customer_cart_items, total_price=total_price)


@main.route('/profile/cart/update-item-quantity/<int:equipment_id>', methods=["POST"])
def update_item_quantity(equipment_id):
    
    action = request.form.get('action')
    current_user = session['customer_id']

    current_cart_id_query = "SELECT id FROM shopping_session WHERE customer = %s"
    current_cart_id = fetch_query(current_cart_id_query, (current_user,))[0][0]

    update_time = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    cart_update_modified_time_query = "UPDATE shopping_session SET modified_at = %s WHERE id = %s;"

    execute_query(cart_update_modified_time_query, (update_time, current_cart_id))

    fetch_item_quantity_query = """
    SELECT quantity
    FROM cart_item
    WHERE equipment = %s AND shopping_session = %s;
    """

    current_item_quantity = fetch_query(fetch_item_quantity_query, (equipment_id, current_cart_id))[0][0]

    if action == "add":
        current_item_quantity += 1
    elif action == "subtract":
        if current_item_quantity == 1:
            delete_item_query = "DELETE FROM cart_item WHERE equipment = %s AND shopping_session = %s;" 
            execute_query(delete_item_query, (equipment_id, current_cart_id))
            flash("Товар был убран из корзины.")
            return redirect(url_for('main.user_cart'))
        else:
            current_item_quantity -= 1
    
    update_cart_item_info_query = """
    UPDATE cart_item
    SET modified_at = %s, quantity = %s WHERE equipment = %s AND shopping_session = %s;
    """
    
    execute_query(update_cart_item_info_query, (update_time, current_item_quantity, equipment_id, current_cart_id))

    flash('Корзина успешно обновлена.')
    return redirect(url_for('main.user_cart'))

@main.route('/profile/cart/make-order', methods=["POST"])
def make_order():
    current_user = session['customer_id']

    current_cart_id_query = "SELECT id FROM shopping_session WHERE customer = %s;"
    current_cart_id = fetch_query(current_cart_id_query, (current_user,))[0][0]

    fetch_cart_items_query = """
    SELECT cart_item.equipment,
           cart_item.quantity,
           equipment.price * cart_item.quantity AS total_item_price
    FROM cart_item
    INNER JOIN equipment ON cart_item.equipment = equipment.id
    WHERE cart_item.shopping_session = %s; 
    """

    cart_items_raw = fetch_query(fetch_cart_items_query, (current_cart_id,))

    order_total = sum([item[2] for item in cart_items_raw])

    cart_items = []

    for item in cart_items_raw:
        item_info = {
            "equipment_id": item[0],
            "item_quantity": item[1]
        }
        cart_items.append(item_info)
    

    create_new_order(current_user, order_total)

    add_order_items(cart_items)

    clear_customer_cart_query = "DELETE FROM cart_item WHERE shopping_session = %s;" 
    execute_query(clear_customer_cart_query, (current_cart_id,))

    return redirect(url_for('main.user_order_history'))


@main.route('/profile/order-history')
def user_order_history():
    if 'customer_id' not in session:
        return redirect(url_for('auth.login'))
    
    current_customer = session['customer_id']

    fetch_all_customer_orders_query = """
    SELECT id,
           total,
           status
    FROM "order"
    WHERE customer = %s;
    """

    all_customer_orders_raw = fetch_query(fetch_all_customer_orders_query, (current_customer,))

    all_customer_orders = []

    for order in all_customer_orders_raw:
        order_info = {
            "order_id": order[0],
            "order_total": order[1], #order_total is total sum for that order
            "order_status": order[2]
        }
        all_customer_orders.append(order_info)

    return render_template('order_history.html', customer_orders=all_customer_orders)


@main.route('/profile/order-history/<int:order_id>')
def render_order_info(order_id):

    fetch_order_info_query = """
    SELECT id,
           total as order_total_price,
           status
    FROM "order"
    WHERE id = %s;
    """

    order_info_result_raw = fetch_query(fetch_order_info_query, (order_id,))[0]

    order_info = {
        "order_id": order_info_result_raw[0],
        "order_total_price": order_info_result_raw[1],
        "order_status": order_info_result_raw[2]
    }

    fetch_order_items_query = """
    SELECT equipment.id,
           equipment.name,
           order_items.quantity,
           equipment.price * order_items.quantity AS total_price
    FROM order_items
    INNER JOIN equipment
    ON order_items.equipment = equipment.id
    WHERE order_items."order" = %s;
    """

    current_order_items_raw = fetch_query(fetch_order_items_query, (order_id,))

    current_order_items = []

    for item in current_order_items_raw:
        item_info = {
            "item_id": item[0],
            "item_name": item[1],
            "item_quantity": item[2],
            "item_total_price": item[3]
        }
        current_order_items.append(item_info)

    return render_template('order_info.html', order_info=order_info, current_order_items=current_order_items)


@main.route('/profile/order-history/<int:order_id>/update-item-quantity/<int:equipment_id>', methods=["POST"])
def update_order_item_quantity(order_id, equipment_id):
    action = request.form.get("action")

    fetch_order_status = "SELECT status FROM \"order\" WHERE id = %s;"

    order_status = fetch_query(fetch_order_status, (order_id,))[0][0]

    fetch_order_total = "SELECT total FROM \"order\" WHERE id = %s;"

    order_total = fetch_query(fetch_order_total, (order_id,))[0][0]

    if order_status != "Обрабатывается":
        return redirect(url_for('main.render_order_info', order_id=order_id))   

    update_time = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    update_order_time = "UPDATE \"order\" SET modified_at=%s WHERE id=%s;"
    execute_query(update_order_time, (update_time, order_id))

    fetch_order_item_quantity = "SELECT quantity FROM order_items WHERE equipment=%s AND \"order\"=%s;" 

    current_item_quantity = fetch_query(fetch_order_item_quantity, (equipment_id, order_id))[0][0]

    fetch_item_price = "SELECT price FROM equipment WHERE id = %s;"

    item_price = fetch_query(fetch_item_price, (equipment_id,))[0][0]

    if action == "add":
        current_item_quantity += 1
        new_order_total = "UPDATE \"order\" SET total = %s WHERE id = %s;"
        execute_query(new_order_total, (order_total+item_price, order_id))
    elif action == "subtract":
        if current_item_quantity == 1:
            new_order_total = "UPDATE \"order\" SET total = %s WHERE id = %s;"
            execute_query(new_order_total, (order_total-item_price, order_id))

            delete_item_from_order = "DELETE FROM order_items WHERE equipment=%s AND \"order\"=%s;"
            execute_query(delete_item_from_order, (equipment_id, order_id))
            flash("Товар был убран из заказа.")
            return redirect(url_for('main.render_order_info', order_id=order_id))
        else:
            current_item_quantity -= 1
            new_order_total = "UPDATE \"order\" SET total = %s WHERE id = %s;"
            execute_query(new_order_total, (order_total-item_price, order_id))

    update_order_item_time = "UPDATE order_items SET modified_at=%s, quantity=%s WHERE \"order\"=%s AND equipment=%s;"  
    execute_query(update_order_item_time, (update_time, current_item_quantity, order_id, equipment_id))
    return redirect(url_for('main.render_order_info', order_id=order_id))


@main.route('/equipment/search', methods=["GET"])
def search_equipment():

    search_string = request.args.get('search_string', '')

    if not search_string:
        return redirect(url_for('main.shop_page'))

    fetch_all_equipment = """
        SELECT equipment.id, 
               equipment.name,
               equipment.price,
               equipment.equipment_pic_path
        FROM equipment
        INNER JOIN category
        ON equipment.category = category.id
        WHERE regexp_like(equipment.name, %s, 'i');  
        """
    
    equipments = fetch_query(fetch_all_equipment, (search_string,))
    equipment_list = []
    for product in equipments:
        product_info = {
            "id": product[0],
            "name": product[1],
            "price": product[2],
            "picture": product[3]
        }
        equipment_list.append(product_info)

    fetch_all_categories = "SELECT id, name FROM category;"

    categories_raw = fetch_query(fetch_all_categories)

    categories = []

    for category in categories_raw:
        category_info = {
            "id": category[0],
            "name": category[1]
        }
        categories.append(category_info)


    return render_template('equipment.html', equipment_list=equipment_list, categories=categories)


@main.route('/profile/training-history')
def training_history():

    current_user = session['customer_id']

    current_time = datetime.now()

    current_user_training_sessions_query = """
    SELECT 
           training_session.start_time,
           training_session.end_time,
           training_session.room_number,
           class.name,
           trainer.name
    FROM training_session
    INNER JOIN class ON training_session.class = class.id
    INNER JOIN trainer ON training_session.trainer = trainer.id
    WHERE training_session.id IN  (SELECT training_session from cust_train_session WHERE customer = %s)
    ORDER BY training_session.start_time;
    """

    current_user_training_sessions_query = fetch_query(current_user_training_sessions_query, (current_user,))

    past_training_sessions = []

    upcoming_training_sessions = []

    for class_session in current_user_training_sessions_query:
        class_session_info = {
            "start_time": class_session[0],
            "end_time": class_session[1],
            "room_number": class_session[2],
            "class_name": class_session[3],
            "trainer_name": class_session[4],
        }
        
        if class_session_info['start_time'] <= current_time:
            past_training_sessions.append(class_session_info)
        else:
            upcoming_training_sessions.append(class_session_info)

    return render_template('training_history.html', upcoming_sessions=upcoming_training_sessions, past_sessions=past_training_sessions)

@main.route('/plans')
def customer_training_plans():

    fetch_plans = "SELECT plan_name, description, price FROM subscription;"

    all_plans_raw = fetch_query(fetch_plans)

    all_plans = []

    for plan in all_plans_raw:
        plan_info = {
            "name": plan[0],
            "description": plan[1],
            "price": plan[2]
        }
        all_plans.append(plan_info)

    return render_template('plans.html', training_plans=all_plans) 

@main.route('/partnership')
def partnership():
    return render_template('partnership.html')