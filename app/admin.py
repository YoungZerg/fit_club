import os
from flask import render_template, Blueprint, session, redirect, url_for, request, flash
from fit_club.database.db import fetch_query, create_new_admin, verify_password, create_new_equipment, add_category, add_class, new_training_session, execute_query
from argon2 import PasswordHasher
from fit_club.misc.functions import allowed_file
from werkzeug.utils import secure_filename


UPLOAD_EQUIPMENT_DIR = os.path.join('\\'.join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1]), r'static\images\uploads\equipment')

admin = Blueprint('admin', __name__, static_folder='../static', template_folder='../templates/admin')

ph = PasswordHasher()

@admin.route('/admin-home', methods=["GET", "POST"])
def admin_home():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        retrieve_admin_name = "SELECT name FROM admin WHERE id = %i;" % admin_id
        admin_name = fetch_query(retrieve_admin_name)[0][0]
        return render_template('admin_main.html', admin_name=admin_name)
    return redirect(url_for('admin.admin_login'))
 

@admin.route('/admin-login', methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        fetch_admin = "SELECT id, password_hash FROM admin WHERE email = '%s';" % email
        admin = fetch_query(fetch_admin)

        if (len(admin) == 0) or (len(admin) != 0 and not verify_password(admin[0][1], password)):
            flash('Please check your login details and try again.')
            return redirect(url_for('admin.admin_login'))
        
        session['admin_id'] = admin[0][0]
        return redirect(url_for('admin.admin_home'))

    return render_template('admin_login.html')

@admin.route('/admin-signup', methods=["GET", "POST"])
def admin_signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        is_admin_exists = "SELECT exists (SELECT 1 FROM admin WHERE email = '%s' LIMIT 1);" % email

        result = fetch_query(is_admin_exists)[0][0]

        if result:
            flash("Admin already exists.")
            return redirect(url_for('admin.admin_signup'))
        
        hashed_password = ph.hash(password)

        create_new_admin(name, email, hashed_password)
        return redirect(url_for('admin.admin_login'))

    return render_template('admin_register.html')


@admin.route('/admin-logout')
def admin_logout():
    session.pop('admin_id', None)
    return redirect(url_for('admin.admin_login'))


@admin.route('/admin-home/add-new-equipment', methods=["GET", "POST"])
def add_new_equipment():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        category = request.form.get("category")

        if name is None or description is None or price is None or category is None:
            flash("Please enter all parameters")
            return redirect(url_for('admin.add_new_equipment'))

        if "equipment_photo" not in request.files:
            flash("Please choose an image for a product")
            return redirect(url_for('admin.add_new_equipment'))
        
        file = request.files["equipment_photo"]
        if file.filename == "":
            flash("Please choose an image for a product")
            return redirect(url_for('admin.add_new_equipment'))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_EQUIPMENT_DIR, filename)
            file.save(filepath)
            create_new_equipment(name, description, price, category, filename)

        return redirect(url_for('admin.add_new_equipment'))

    fetch_all_categories = "SELECT id, name FROM category;"
    categories = fetch_query(fetch_all_categories)
    return render_template("add_equipment.html", categories=categories)


@admin.route('/admin-home/list-equipment', methods=["GET", "POST"])
def list_all_equipment():
    if 'admin_id' in session:
        fetch_all_equipment = """
        SELECT equipment.id, equipment.name,
               equipment.price, category.name,
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
                "category": product[3],
                "picture": product[4]
            }
            equipment_list.append(product_info)

        return render_template('all_equipment.html', equipment_list=equipment_list)
    
    return redirect(url_for('admin.admin_login'))

@admin.route('/admin-home/list-equipment/<int:equipment_id>')
def equipment_page(equipment_id):
    fetch_equipment_info = """
    SELECT equipment.id, equipment.name,
           equipment.description, equipment.price,
           equipment.equipment_pic_path,
           category.name
    FROM equipment
    INNER JOIN category
    ON equipment.category = category.id
    WHERE equipment.id = %i;
    """ % equipment_id
    equipment_info = fetch_query(fetch_equipment_info)[0]

    equipment = {
        "id": equipment_info[0],
        "name": equipment_info[1],
        "description": equipment_info[2],
        "price": equipment_info[3],
        "picture": equipment_info[4],
        "category": equipment_info[5],
    }
    
    return render_template('equipment_page.html', equipment=equipment)


@admin.route('/admin-home/add-new-category', methods=["GET", "POST"])
def add_new_category():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if (name is None or description is None) or (len(name) == 0 or len(description) == 0):
            flash("Please enter all parameters")
            return redirect(url_for('admin.add_new_category'))
        else: 
            add_category(name, description)
            return redirect(url_for('admin.add_new_category'))
    
    return render_template("add_category.html")

@admin.route('/admin-home/add-new-class', methods=["GET", "POST"])
def add_new_class():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        if (name is None or description is None) or (len(name) == 0 or len(description) == 0):
            flash("Please enter all parameters")
            return redirect(url_for('admin.add_new_class'))
            
        add_class(name, description)
        return redirect(url_for('admin.add_new_class'))
    
    return render_template("add_class.html")



@admin.route('/admin-home/add-training-session', methods=["GET", "POST"])
def add_training_session():
    if request.method == "POST":
        class_name = request.form.get("class_name")
        trainer_name = request.form.get("trainer_name")
        room_number = request.form.get("room_number")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")

        new_training_session(class_name, trainer_name, room_number, start_time, end_time)

        return redirect(url_for('admin.add_training_session'))

    all_classes_query = "SELECT id, name FROM class;"
    all_classes_raw = fetch_query(all_classes_query)
    all_classes = []

    for training_class in all_classes_raw:
        class_info = {
            "class_id": training_class[0],
            "class_name": training_class[1]
        }
        all_classes.append(class_info)

    all_trainers_query = "SELECT id, name FROM trainer;"
    all_trainers_raw = fetch_query(all_trainers_query)
    all_trainers = []

    for trainer in all_trainers_raw:
        trainer_info = {
            "trainer_id": trainer[0],
            "trainer_name": trainer[1]
        }
        all_trainers.append(trainer_info)


    all_sessions_query = """
    SELECT training_session.start_time,
           training_session.end_time,
           training_session.room_number,
           class.name,
           trainer.name
    FROM training_session
    INNER JOIN class ON training_session.class = class.id
    INNER JOIN trainer ON training_session.trainer = trainer.id
    ORDER BY training_session.start_time;
    """
    all_sessions_raw = fetch_query(all_sessions_query)
    all_sessions = []

    for training_session in all_sessions_raw:
        session_info = {
            "start_time": training_session[0],
            "end_time": training_session[1],
            "room_number": training_session[2],
            "class_name": training_session[3],
            "trainer_name": training_session[4]
        }
        all_sessions.append(session_info)



    return render_template('add_train_session.html', all_classes=all_classes, all_trainers=all_trainers, all_sessions=all_sessions)

@admin.route('/admin-home/customers-orders')
def view_orders():
    if 'admin_id' not in session:
        return redirect(url_for('admin.admin_login'))

    fetch_all_orders_info = """
    SELECT customer.name,
           "order".id,
           "order".total,
           "order".status
    FROM "order"
    INNER JOIN customer
    ON "order".customer = customer.id;
    """

    all_orders_raw = fetch_query(fetch_all_orders_info)

    all_orders = []

    for order in all_orders_raw:
        order_info = {
            "customer_name": order[0],
            "order_id": order[1],
            "order_total": order[2],
            "order_status": order[3]
        }
        all_orders.append(order_info)

    return render_template('view_orders.html', orders=all_orders)

@admin.route('/admin-home/customers-orders/<int:order_id>', methods=["GET", "POST"])
def order_page(order_id):

    if request.method == "POST":
        new_order_status = request.form.get("status")
        update_order_status_query = "UPDATE \"order\" SET status = '%s' WHERE id = %i;" % (new_order_status, order_id)
        execute_query(update_order_status_query)    
        return redirect(url_for('admin.order_page', order_id=order_id))


    fetch_order_info = """
    SELECT customer.name,
           "order".id,
           "order".total,
           "order".status
    FROM "order"
    INNER JOIN customer
    ON "order".customer = customer.id
    WHERE "order".id = %i;
    """ % order_id

    order_info_raw = fetch_query(fetch_order_info)[0]

    order_info = {
            "customer_name": order_info_raw[0],
            "order_id": order_info_raw[1],
            "order_total": order_info_raw[2],
            "order_status": order_info_raw[3]
    }

    fetch_order_items = """
    SELECT equipment.id,
           equipment.name,
           order_items.quantity,
           equipment.price * order_items.quantity AS total_price
    FROM order_items
    INNER JOIN equipment
    ON order_items.equipment = equipment.id
    WHERE order_items."order" = %i; 
    """ % order_id

    order_items_raw = fetch_query(fetch_order_items)
    
    order_items = []

    for item in order_items_raw:
        item_info = {
            "item_id": item[0],
            "item_name": item[1],
            "item_quantity": item[2],
            "item_total_price": item[3]
        }
        order_items.append(item_info)



    return render_template('admin_order_page.html', order_items=order_items, order_info=order_info)


#

@admin.route('/admin-home/customers-orders/<int:order_id>/update-item-quantity/<int:equipment_id>', methods=["POST"])
def update_order_item_quantity(order_id, equipment_id):
    
    action = request.form.get("action")
    fetch_item_quantity = "SELECT quantity FROM order_items WHERE \"order\" = %i AND equipment = %i;" % (order_id, equipment_id)

    current_item_quantity = fetch_query(fetch_item_quantity)[0][0]

    current_item_price = fetch_query("SELECT price FROM equipment WHERE id = %i;" % equipment_id)[0][0]

    current_order_total = fetch_query("SELECT total FROM \"order\" WHERE id = %i" % order_id)[0][0]

    if action == "add":
        current_item_quantity += 1
        new_order_total = "UPDATE \"order\" SET total = %i WHERE id = %i;" % (current_order_total+current_item_price, order_id)
        execute_query(new_order_total)

    elif action=="subtract":
        if current_item_quantity == 1:
            new_order_total = "UPDATE \"order\" SET total = %i WHERE id = %i;" % (current_order_total-current_item_price, order_id)
            execute_query(new_order_total)

            delete_item_query = "DELETE FROM order_items WHERE \"order\" = %i AND equipment = %i;" % (order_id, equipment_id)
            execute_query(delete_item_query)
        else:
            current_item_quantity -= 1
            new_order_total = "UPDATE \"order\" SET total = %i WHERE id = %i;" % (current_order_total-current_item_price, order_id)
            execute_query(new_order_total)
    
    update_item_quantity = "UPDATE order_items SET quantity = %i WHERE \"order\"= %i AND equipment = %i" % (current_item_quantity, order_id, equipment_id)
    execute_query(update_item_quantity)

    return redirect(url_for('admin.order_page', order_id=order_id))

@admin.route('/admin-home/customers-orders/search/', methods=["GET"])
def search_order():

    search_string = request.args.get('search_string', '')

    if not search_string:
        return redirect(url_for('admin.view_orders'))

    fetch_all_customer_orders = """
    SELECT customer.name,
           "order".id,
           "order".total,
           "order".status
    FROM "order"
    INNER JOIN customer
    ON "order".customer = customer.id
    WHERE regexp_like(customer.name, '%s', 'i');  
    """ % search_string

    all_orders_raw = fetch_query(fetch_all_customer_orders)

    all_orders = []

    for order in all_orders_raw:
        order_info = {
            "customer_name": order[0],
            "order_id": order[1],
            "order_total": order[2],
            "order_status": order[3]
        }
        all_orders.append(order_info)


    return render_template('order_search.html', orders=all_orders)


@admin.route('/admin-home/list-equipment/search', methods=["GET"])
def search_equipment():
    search_string = request.args.get('search_string', '')

    if not search_string:
        return redirect(url_for('admin.list_all_equipment'))

    fetch_all_equipment = """
    SELECT equipment.id, equipment.name,
           equipment.price, category.name,
           equipment.equipment_pic_path
    FROM equipment
    INNER JOIN category
    ON equipment.category = category.id
    WHERE regexp_like(equipment.name, '%s', 'i');  
    """ % search_string


    equipments = fetch_query(fetch_all_equipment)
    equipment_list = []
    for product in equipments:
        product_info = {
            "id": product[0],
            "name": product[1],
            "price": product[2],
            "category": product[3],
            "picture": product[4]
        }
        equipment_list.append(product_info)



    return render_template('equipment_search.html', equipment_list=equipment_list)