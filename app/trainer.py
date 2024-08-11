import os
from flask import render_template, Blueprint, session, redirect, url_for, request, flash, send_from_directory
from fit_club.database.db import fetch_query, add_new_trainer, trainer_profile_update, verify_password, upload_new_certificate
from argon2 import PasswordHasher
from fit_club.misc.functions import allowed_file, allowed_cert
from werkzeug.utils import secure_filename


trainer = Blueprint('trainer', __name__, static_folder='../static', template_folder='../templates/trainer')
ph = PasswordHasher()

UPLOAD_CERT_DIR = os.path.join('\\'.join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1]), r'static\images\uploads\trainers\certs')
UPLOAD_TRAINER_DIR = os.path.join('\\'.join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1]), r'static\images\uploads\trainers\profile')


@trainer.route('/trainer-home', methods=["GET", "POST"])
def trainer_home():
    if 'trainer_id' in session:
        
        trainer_info_query = "SELECT * FROM trainer WHERE id = %i" % session['trainer_id']

        #trainer_sessions_query = "SELECT"

        trainer_info = fetch_query(trainer_info_query)

        

        #trainer = {
        #    "name": result[0],
        #    "email": 
        #}

        return render_template('trainer_main.html', trainer_name=trainer_info[0][1])
    return redirect(url_for('trainer.trainer_login'))


@trainer.route('/trainer-profile/trainer-schedule')
def trainer_schedule():
    current_trainer = session['trainer_id']
    
    trainer_name_query = "SELECT name FROM trainer WHERE id = %i;" % current_trainer
    
    trainer_sessions_query = """
    SELECT training_session.id,
           training_session.start_time,
           training_session.end_time,
           class.name
    FROM training_session
    INNER JOIN class
    ON training_session.class = class.id
    WHERE training_session.trainer = %i
    ORDER BY training_session.start_time;
    """ % current_trainer

    trainer_name = fetch_query(trainer_name_query)[0][0]
    
    trainer_sessions_result = fetch_query(trainer_sessions_query)

    trainer_schedule = []

    for session_entry in trainer_sessions_result:
        trainer_session = {
            "session_id": session_entry[0],
            "start_time": session_entry[1],
            "end_time": session_entry[2],
            "class_name": session_entry[3]
        }
        trainer_schedule.append(trainer_session)

    return render_template('trainer_schedule.html', trainer_schedule=trainer_schedule, trainer_name=trainer_name)


@trainer.route('/trainer-profile/trainer-schedule/<int:session_id>')
def session_details(session_id):

    session_details_query = """
    SELECT training_session.start_time,
           training_session.end_time,
           training_session.room_number,
           class.name
    FROM training_session
    INNER JOIN class
    ON training_session.class = class.id
    WHERE training_session.id = %i;
    """ % session_id

    training_session_participants_query = """
    SELECT customer.name,
           customer.profile_pic_path
    FROM cust_train_session
    INNER JOIN training_session ON cust_train_session.training_session = training_session.id
    INNER JOIN customer ON  cust_train_session.customer = customer.id
    WHERE training_session.id = %i;
    """ % session_id

    session_details_result = fetch_query(session_details_query)
    training_session_participants_result = fetch_query(training_session_participants_query)

    train_session_details = {
        "start_time": session_details_result[0][0],
        "end_time": session_details_result[0][1],
        "room_number": session_details_result[0][2],
        "class_name": session_details_result[0][3]
    }

    participants_list = []

    for participant in training_session_participants_result:
        participant_info = {
            "name": participant[0],
            "pfp_name": participant[1]
        }
        participants_list.append(participant_info)
    

    return render_template('train_session.html', train_session_details=train_session_details, participants_list=participants_list)


@trainer.route('/trainer-profile/save-changes', methods=["POST"])
def update_trainer_profile():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    sex = request.form.get("sex")
    birth_date = request.form.get("birth_date")
    
    current_trainer = session['trainer_id']


    if 'trainer_profile_pic' not in request.files:
        trainer_profile_update(current_trainer, name, email, phone, birth_date, sex, None)
        return redirect(url_for('trainer.trainer_profile_render'))
    
    trainer_pfp = request.files['trainer_profile_pic']

    if trainer_pfp.filename == '':
        trainer_profile_update(current_trainer, name, email, phone, birth_date, sex, None)
        return redirect(url_for('trainer.trainer_profile_render'))
    
    if trainer_pfp and allowed_file(trainer_pfp.filename):
        filename = secure_filename(trainer_pfp.filename)
        trainer_pfp.save(os.path.join(UPLOAD_TRAINER_DIR, filename))
        trainer_profile_update(current_trainer, name, email, phone, birth_date, sex, filename)



    return redirect(url_for('trainer.trainer_profile_render'))

@trainer.route('/trainer-profile/upload-cert', methods=["POST"])
def upload_certificate():
    if 'certificate' not in request.files:
        flash("No file part")
        return redirect(url_for('trainer.upload_certificate'))
    
    certificate = request.files['certificate']

    if certificate.filename == '':
        flash("No file part")
        return redirect(url_for('trainer.upload_certificate'))
    
    current_trainer = session['trainer_id']

    if certificate and allowed_cert(certificate.filename):
        filename = secure_filename(certificate.filename)
        certificate.save(os.path.join(UPLOAD_CERT_DIR, filename))
        upload_new_certificate(filename, current_trainer)
        return redirect(url_for('trainer.trainer_profile_render'))
    


@trainer.route('/trainer-profile', methods=["GET", "POST"])
def trainer_profile_render():
    if 'trainer_id' not in session:
        return redirect(url_for('trainer.trainer_login'))
    
    current_trainer = session['trainer_id']

    print(session)

    trainer_info_query = "SELECT name, email, sex, birth_date, tel_number, profile_pic_path FROM trainer WHERE id = %i;" % current_trainer
    
    trainer_certificates_query = "SELECT cert_path FROM train_cert WHERE trainer = %i;" % current_trainer 

    trainer_result = fetch_query(trainer_info_query)
    certificates_result = fetch_query(trainer_certificates_query)

    trainer_info = {
        "trainer_name": trainer_result[0][0],
        "trainer_email": trainer_result[0][1],
        "sex": trainer_result[0][2],
        "birth_date": trainer_result[0][3],
        "tel_number": trainer_result[0][4],
        "pfp_path": trainer_result[0][5]
    }

    trainer_certificates = [cert[0] for cert in certificates_result]


    return render_template('trainer_profile.html', trainer_info=trainer_info, trainer_certificates=trainer_certificates)


@trainer.route('/trainer-profile/download/<path:filename>')
def download_certificate(filename):
    return send_from_directory(UPLOAD_CERT_DIR, filename)


@trainer.route('/trainer-login', methods=["GET", "POST"])
def trainer_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        trainer_info_query = "SELECT id, password_hash FROM trainer WHERE email = '%s';" % email

        result = fetch_query(trainer_info_query)

        if (len(result) == 0) or (len(result) != 0 and not verify_password(result[0][1], password)):
            flash("Please check your login details and try again.")
            return redirect(url_for('trainer.trainer_login'))
        
        session['trainer_id'] = result[0][0]    
        return redirect(url_for('trainer.trainer_home'))
        

    return render_template('trainer_login.html')



@trainer.route('/trainer-signup', methods=["GET", "POST"])
def trainer_register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        sex = request.form.get("sex")
        tel_number = request.form.get("telephone")
        birth_date = request.form.get("birth_date")

        is_trainer_exists_query = "SELECT exists (SELECT 1 FROM trainer WHERE email = '%s' LIMIT 1);" % email

        result = fetch_query(is_trainer_exists_query)[0][0]

        if result:
            flash("Trainer already exists.")
            return redirect(url_for('trainer.trainer_register'))

        hashed_password = ph.hash(password)

        add_new_trainer(name, email, hashed_password, tel_number, birth_date, sex)
        return redirect(url_for('trainer.trainer_login'))

    return render_template('trainer_register.html')