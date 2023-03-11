from board import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define the association table for the many-to-many relationship between users and teams
user_team_association = db.Table('user_team_association',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('team_id', db.Integer, db.ForeignKey('team.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    teams = db.relationship('Team', secondary=user_team_association, backref='members', lazy=True)

    # One-to-many relationship between users and tasks. We can easily access a users tasks by using the user.tasks attribute.
    # When a user is deleted, all of their tasks will be deleted as well.
    tasks = db.relationship('Task', backref='creator', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('To Do', 'In Progress', 'Done', name='task_status'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))


    def __repr__(self):
        return f"Task('{self.id}', '{self.title}')"
    
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='team', lazy=True)



    def __repr__(self):
        return f"Team('{self.id}', '{self.name}')"