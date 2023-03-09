from flask import render_template, url_for, flash, redirect, request, abort
from board import app, db, bcrypt
from board.forms import RegistrationForm, LoginForm, UpdateAccountForm, TaskForm
from board.models import User, Task
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/')
def index():
   
    # return "Please login to view your tasks"
    if current_user.is_authenticated:
        tasks_todo = Task.query.filter_by(creator=current_user, status='To Do').all()
        tasks_in_progress = Task.query.filter_by(creator=current_user, status='In Progress').all()
        tasks_done = Task.query.filter_by(creator=current_user, status='Done').all()
        # print(tasks_todo)
        return render_template('kanban.html', tasks_todo=tasks_todo, tasks_in_progress=tasks_in_progress, tasks_done=tasks_done)
    return render_template('kanban.html')

@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        # flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
            # flash(f'You have been logged in!', 'success')
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        # flash('Your account has been updated!', 'success')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/task/new', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, description=form.description.data, status=form.status.data, creator=current_user)
        db.session.add(task)
        db.session.commit()
        # flash('Your task has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_task.html', title='New Task', form=form, legend='New Task')

@app.route('/task/<int:task_id>')
@login_required
def task(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('task.html', title=task.title, task=task)

@app.route('/task/<int:task_id>/update', methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.creator != current_user:
        abort(403)
    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.status = form.status.data
        db.session.commit()
        # flash('Your task has been updated!', 'success')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.title.data = task.title
        form.description.data = task.description
        form.status.data = task.status
    return render_template('create_task.html', title='Update Task', form=form, legend='Update Task')


@app.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.creator != current_user:
        abort(403)
    db.session.delete(task)
    db.session.commit()
    # flash('Your task has been deleted!', 'success')
    return redirect(url_for('index'))