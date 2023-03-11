from flask import render_template, url_for, flash, redirect, request, abort
from board import app, db, bcrypt
from board.forms import RegistrationForm, LoginForm, UpdateAccountForm, TaskForm, TeamForm
from board.models import User, Task, Team
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/')
def index():
    if current_user.is_authenticated:
        # Get tasks and ordered by priority in descending order and then by due date in ascending order. 
        # The tasks are not associated with a team. The tasks also belong to the current user
        tasks_todo = Task.query.filter_by(status='To Do', team_id=None, creator=current_user).order_by(Task.priority.desc(), Task.due_date.asc()).all()
        tasks_in_progress = Task.query.filter_by(status='In Progress', team_id=None, creator=current_user).order_by(Task.priority.desc(), Task.due_date.asc()).all()
        tasks_done = Task.query.filter_by(status='Done', team_id=None, creator=current_user).order_by(Task.priority.desc(), Task.due_date.asc()).all()

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
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # hash the password
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
        # pre-populate the form with the current user's data
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/account/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_account(user_id):
    user = User.query.get_or_404(user_id)
    # if current user trying to delete the account is not the owner, abort the request
    if user != current_user:
        abort(403)
    db.session.delete(user)
    db.session.commit()
    # flash('Your account has been deleted!', 'success')
    return redirect(url_for('index'))

@app.route('/task/new', methods=['GET', 'POST'])
@login_required
def create_task():
    # create a new task

    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, description=form.description.data, due_date=form.due_date.data, 
                    priority=form.priority.data, status=form.status.data, creator=current_user)
        db.session.add(task)
        db.session.commit()
        # flash('Your task has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_task.html', title='New Task', form=form, legend='New Task')

@app.route('/task/<int:task_id>')
@login_required
def task(task_id):
    # show the attributes of a task

    task = Task.query.get_or_404(task_id)
    return render_template('task.html', title=task.title, task=task)

@app.route('/task/<int:task_id>/update', methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    # update the attributes of an existing task

    task = Task.query.get_or_404(task_id)
    if task.creator != current_user:
        abort(403)
    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.status = form.status.data
        task.due_date = form.due_date.data
        task.priority = form.priority.data
        db.session.commit()
        # flash('Your task has been updated!', 'success')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        # pre-populate the form with the current task's data
        form.title.data = task.title
        form.description.data = task.description
        form.status.data = task.status
        form.due_date.data = task.due_date
        form.priority.data = task.priority
    return render_template('create_task.html', title='Update Task', form=form, legend='Update Task')


@app.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    # delete a task

    task = Task.query.get_or_404(task_id)
    if task.team_id:  # if the task is part of a team, make sure the user trying to delete it is part of the team
        team = Team.query.get_or_404(task.team_id)
        if current_user not in team.members:
            abort(403)
    db.session.delete(task)
    db.session.commit()
    # flash('Your task has been deleted!', 'success')
    return redirect(url_for('index'))

@app.route('/team/new', methods=['GET', 'POST'])
@login_required
def create_team():
    # create a new team

    form = TeamForm()
    if form.validate_on_submit():
        team = Team(name=form.name.data)
        team.members.append(current_user)
        members_to_be_added = form.member_emails.data.split(',')
        for member in members_to_be_added:
            user = User.query.filter_by(email=member).first()
            if user:
                team.members.append(user)
        db.session.add(team)
        db.session.commit()
        # flash('Your team has been created!', 'success')
        return redirect(url_for('teams'))
    return render_template('create_team.html', title='New Team', form=form, legend='New Team')

@app.route('/teams')
@login_required
def teams():
    # show all the teams the user is part of

    teams = current_user.teams
    if len(teams) == 0:
        return redirect(url_for('create_team'))
    return render_template('teams.html', teams=teams)

@app.route('/team/<int:team_id>')
@login_required
def team(team_id):
    # show the team page where the user can see all the tasks of the team and update the team

    team = Team.query.get_or_404(team_id)
    if current_user not in team.members:
        abort(403)
    return render_template('team.html', title=team.name, team=team)

@app.route('/team/<int:team_id>/update', methods=['GET', 'POST'])
@login_required
def update_team(team_id):
    # update a team by changing its name and/or adding new members

    team = Team.query.get_or_404(team_id)
    if current_user not in team.members:
        abort(403)
    form = TeamForm()
    if form.validate_on_submit():
        team.name = form.name.data
        members_to_be_added = form.member_emails.data.split(',')
        for member in members_to_be_added:
            user = User.query.filter_by(email=member).first()
            if user:
                team.members.append(user)
        db.session.commit()
        # flash('Your team has been updated!', 'success')
        return redirect(url_for('teams'))
    elif request.method == 'GET':
        form.name.data = team.name
    return render_template('create_team.html', title='Update Team', form=form, legend='Update Team')


@app.route('/team/<int:team_id>/delete', methods=['POST'])
@login_required
def delete_team(team_id):
    # delete a team

    team = Team.query.get_or_404(team_id)
    if current_user not in team.members:
        abort(403)
    db.session.delete(team)
    db.session.commit()
    # flash('Your team has been deleted!', 'success')
    return redirect(url_for('teams'))


@app.route('/team/<int:team_id>/task/new', methods=['GET', 'POST'])
@login_required
def create_team_task(team_id):
    # create a new task for a team. this will not be visible to the user as part of their personal tasks

    form = TaskForm()
    if form.validate_on_submit():
        team = Team.query.get_or_404(team_id)
        task = Task(title=form.title.data, description=form.description.data, status=form.status.data, due_date=form.due_date.data, priority=form.priority.data, team=team)
        db.session.add(task)
        db.session.commit()
        # flash('Your task has been created!', 'success')
        return redirect(url_for('team_tasks', team_id=team_id))
    return render_template('create_task.html', title='New Task', form=form, legend='New Task')

@app.route('/team/<int:team_id>/tasks')
def team_tasks(team_id):
    # show all the tasks of a team
    
    team = Team.query.get_or_404(team_id)
    if current_user not in team.members:
        abort(403)

    # get tasks ordered by priority in descending order and then by due date in ascending order
    tasks_todo = Task.query.filter_by(team=team, status='To Do').order_by(Task.priority.desc(), Task.due_date.asc()).all()
    tasks_in_progress = Task.query.filter_by(team=team, status='In Progress').order_by(Task.priority.desc(), Task.due_date.asc()).all()
    tasks_done = Task.query.filter_by(team=team, status='Done').order_by(Task.priority.desc(), Task.due_date.asc()).all()

    return render_template('team_tasks.html', title=team.name, team=team, tasks_todo=tasks_todo, tasks_in_progress=tasks_in_progress, tasks_done=tasks_done)
