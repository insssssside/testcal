from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Memo
from forms import LoginForm, RegisterForm
from datetime import date, timedelta
from calendar import monthrange

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables():
    db.create_all()  # 最初のリクエストの前にテーブルを作成

@app.route('/')
@login_required
def calendar():
    # 現在の年月を取得
    current_year = request.args.get('year', date.today().year, type=int)
    current_month = request.args.get('month', date.today().month, type=int)
    
    # 月の最初と最後の日を取得
    first_day, last_day = monthrange(current_year, current_month)
    first_date = date(current_year, current_month, 1)
    last_date = date(current_year, current_month, last_day)
    
    # 現在の月のメモを取得
    memos = Memo.query.filter(
        Memo.user_id == current_user.id,
        Memo.date >= first_date,
        Memo.date <= last_date
    ).all()
    
    return render_template('calendar.html', 
                           memos=memos, 
                           year=current_year, 
                           month=current_month,
                           first_date=first_date,
                           last_date=last_date)

@app.route('/add_memo', methods=['POST'])
@login_required
def add_memo():
    date_str = request.form.get('date')
    content = request.form.get('content')
    memo = Memo(date=date_str, content=content, user_id=current_user.id)
    db.session.add(memo)
    db.session.commit()
    return redirect(url_for('calendar', year=date_str.split('-')[0], month=date_str.split('-')[1]))

@app.route('/get_memos')
@login_required
def get_memos():
    # メモを JSON 形式で取得（カレンダー表示用）
    memos = Memo.query.filter_by(user_id=current_user.id).all()
    memos_data = [{"date": memo.date, "content": memo.content} for memo in memos]
    return jsonify(memos_data)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('calendar'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
