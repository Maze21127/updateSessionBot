import hashlib
import os

from flask import request, jsonify, render_template, redirect, send_file, flash, url_for
from flask_login import login_required, logout_user
from werkzeug.utils import secure_filename

from app import app, utils, auth, db
import app.services.telegram as tg
from app.models import User
from app.services.auth import auth_user, LoginStatus
from settings import AUTH_TOKEN


@auth.verify_token
def verify_token(token):
    if token == AUTH_TOKEN:
        return "admin"


@app.route('/', methods=['GET'])
@login_required
def index():
    return redirect('/account')


@app.route('/names', methods=["GET", "POST"])
@login_required
def names():
    form = utils.forms.UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                               secure_filename("names.txt")))
        return """<h1>Файл успешно загружен</h1> <a href="/names">Назад</a>"""
    return render_template("names.html", form=form)


@app.route('/download_file', methods=['GET', "POST"])
@login_required
def download_file():
    try:
        return send_file(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                      secure_filename("names.txt")), as_attachment=True)
    except FileNotFoundError:
        return """<h1>Сначала нужно загрузить файл</h1> <a href="/names">Назад</a>"""


@app.route('/account', methods=["GET"])
@login_required
async def account():
    my_account = await tg.get_me()
    if isinstance(my_account, dict):
        return render_template('account.html', account=my_account)
    else:
        return render_template('account.html', error=my_account)


@app.route('/account/status', methods=["GET"])
@auth.login_required
async def account_status():
    my_account = await tg.get_me()
    groups_list = await tg.get_groups()
    if isinstance(my_account, dict):
        return jsonify(account=my_account, groups=groups_list)
    else:
        return jsonify(error={"status": 400, "message": "Вход не выполнен"})


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login = request.form.get('username')
    password = request.form.get('password')
    status = auth_user(login, password)

    if status is LoginStatus.EMPTY_FIELDS:
        return render_template('login.html')

    if status is LoginStatus.USER_NOT_FOUND:
        flash("login or password incorrect")
        return render_template('login.html')

    if status is LoginStatus.SUCCESS:
        next_page = request.args.get("next")
        return redirect(next_page) if next_page is not None else redirect('/account')


@app.route('/rename', methods=['GET'])
@auth.login_required
async def rename():
    status = await tg.rename_channels()
    return jsonify(data=status)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))


# @app.route('/add_user')
# def add_user():
#     password = hashlib.sha512("".encode()).hexdigest()
#     user = User("sam", password)
#     db.session.add(user)
#     db.session.commit()
#     return "123"


@app.route('/account/groups', methods=["GET"])
@login_required
async def groups():
    my_groups = await tg.get_groups()
    if isinstance(my_groups, list):
        return render_template('groups.html', groups=my_groups)
    else:
        return render_template('groups.html', error=my_groups)


@app.route('/update', methods=['GET', 'POST'])
@login_required
async def update_session():
    form = request.form
    api_id = form.get("api_id")
    api_hash = form.get("api_hash")
    phone = form.get("phone_number")

    if api_id is None or api_hash is None or phone is None:
        return f"""<h1>Вы не ввели api_id или api_hash или номер телефона</h1> <a href="/account">Назад</a>"""

    status = await tg.send_code(api_id, api_hash, phone)
    if isinstance(status, str):
        return f"""<h1>{status}</h1> <a href="/account">Назад</a>"""

    return render_template("code.html", code_hash=status.code_hash)


@app.route('/update/code', methods=['GET', 'POST'])
@login_required
async def insert_code():
    if request.method == 'POST':
        form = request.form
        code = form.get('code')
        code_hash = form.get("code_hash")
        password = form.get("password")
        status = await tg.sign_in(code, code_hash, password)
        if status == 'Вход успешно выполнен':
            return redirect('/account')
        else:
            return f"<h1>Ошибка {status} </h1"


@app.after_request
def redirect_to_signin(responce):
    if responce.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)
    return responce

