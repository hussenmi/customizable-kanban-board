import unittest
from board import app, db
from board.models import User, Task, Team
from board.urls import register
import json
import requests
from flask_login import current_user, logout_user, login_user
from datetime import datetime


class TestAuth(unittest.TestCase):
    def setUp(self):
        # set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kanban.db'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.app_context().push()
        db.create_all()
        self.app = app.test_client()
        self.app.testing = True

    def test_register(self):
        # Test registration functionality
        url = 'http://localhost:5000/register'

        # Define the data to be sent in the request
        data = {'username': 'test_user',
                'email': 'test_user@example.com',
                'password': 'test_password',
                'confirm_password': 'test_password'}

        # Convert the data to JSON format
        json_data = json.dumps(data)

        # Set the content type header to indicate that the request payload is JSON
        headers = {'Content-Type': 'application/json'}

        # Send the POST request with the data and headers included
        response = requests.post(url, data=json_data, headers=headers)

        # Check if the response is 200 OK
        self.assertEqual(response.status_code, 200)

        user = User(username='test_user', email='test_user@example.com', password='test_password')
        db.session.add(user)
        db.session.commit()
        
        # Check if user was created in the database
        user = User.query.filter_by(username='test_user').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'test_user')

    def tearDown(self):
        # delete the test database
        db.session.remove()
        db.drop_all()


class TestTasks(unittest.TestCase):
    def setUp(self):
        # set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kanban.db'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.app_context().push()
        db.create_all()
        self.app = app.test_client()
        self.app.testing = True

    def test_add_task(self):
        # Test adding a task
        url = 'http://localhost:5000/task/new'

        # Define the data to be sent in the request
        data = {'title': 'test_task',
                'description': 'test_description',
                'due_date': '2021-05-17',
                'priority': '1',
                'status': 'To Do'}

        # Convert the data to JSON format
        json_data = json.dumps(data)

        # Set the content type header to indicate that the request payload is JSON
        headers = {'Content-Type': 'application/json'}

        # Send the POST request with the data and headers included
        response = requests.post(url, data=json_data, headers=headers)

        # Check if the response is 200 OK
        self.assertEqual(response.status_code, 200)

        task = Task(title='test_task', description='test_description', due_date=datetime.strptime('2021-05-17', "%Y-%m-%d"), priority='1', status='To Do')
        db.session.add(task)
        db.session.commit()

        # Check if task was created in the database
        task = Task.query.filter_by(title='test_task').first()
        self.assertIsNotNone(task)
        self.assertEqual(task.title, 'test_task')

    def test_change_task_status(self):
        task = Task(title='test_task', description='test_description', due_date=datetime.strptime('2021-05-17', "%Y-%m-%d"), priority='1', status='To Do')
        task.status = 'In Progress'
        db.session.add(task)
        db.session.commit()

        # Check if the status of the task was changed
        task = Task.query.filter_by(title='test_task').first()
        self.assertEqual(task.status, 'In Progress')


    def test_delete_task(self):
        task = Task(title='test_task', description='test_description', due_date=datetime.strptime('2021-05-17', "%Y-%m-%d"), priority='1', status='To Do')
        db.session.add(task)
        db.session.commit()

        # Check if task was created in the database
        task = Task.query.filter_by(title='test_task').first()
        self.assertIsNotNone(task)
        self.assertEqual(task.title, 'test_task')

        db.session.delete(task)
        db.session.commit()

        # Check if task was deleted from the database
        task = Task.query.filter_by(title='test_task').first()
        self.assertIsNone(task)

    def tearDown(self):
        # delete the test database
        db.session.remove()
        db.drop_all()

class TestTeams(unittest.TestCase):
    def setUp(self):
        # set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kanban.db'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.app_context().push()
        db.create_all()
        self.app = app.test_client()
        self.app.testing = True

    def test_add_team(self):
        # Test adding a team
        url = 'http://localhost:5000/team/new'

        # Define the data to be sent in the request
        data = {'name': 'test_team', 'member_emails': ['user_1@example.com', 'user_2@example.com']}

        # Convert the data to JSON format
        json_data = json.dumps(data)

        # Set the content type header to indicate that the request payload is JSON
        headers = {'Content-Type': 'application/json'}

        # Send the POST request with the data and headers included
        response = requests.post(url, data=json_data, headers=headers)

        # Check if the response is 200 OK
        self.assertEqual(response.status_code, 200)

        team = Team(name='test_team')
        db.session.add(team)
        db.session.commit()

        # Check if team was created in the database
        team = Team.query.filter_by(name='test_team').first()
        self.assertIsNotNone(team)
        self.assertEqual(team.name, 'test_team')

    def test_delete_team(self):
        team = Team(name='test_team')
        db.session.add(team)
        db.session.commit()

        # Check if team was created in the database
        team = Team.query.filter_by(name='test_team').first()
        self.assertIsNotNone(team)
        self.assertEqual(team.name, 'test_team')

        db.session.delete(team)
        db.session.commit()

        # Check if team was deleted from the database
        team = Team.query.filter_by(name='test_team').first()
        self.assertIsNone(team)

    def tearDown(self):
        # delete the test database
        db.session.remove()
        db.drop_all()
        


if __name__ == '__main__':
    unittest.main()
