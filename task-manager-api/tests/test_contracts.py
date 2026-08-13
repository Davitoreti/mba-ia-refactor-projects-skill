import os
import tempfile
import unittest

os.environ.setdefault('SECRET_KEY', 'test-only-secret-key')

from app import create_app
from database import db
from sqlalchemy import func, select
from models.category import Category
from models.task import Task
from models.user import User


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SECRET_KEY': 'isolated-test-secret',
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            admin = User(name='Admin', email='admin@example.com', role='admin')
            admin.set_password('admin1234')
            manager = User(name='Manager', email='manager@example.com', role='manager')
            manager.set_password('manager1234')
            category = Category(name='Backend', description='API', color='#112233')
            db.session.add_all([admin, manager, category])
            db.session.flush()
            task = Task(title='Task inicial', description='Teste', status='pending', priority=2,
                        user_id=admin.id, category_id=category.id)
            db.session.add(task)
            db.session.commit()

        self.admin_token = self._login('admin@example.com', 'admin1234')
        self.manager_token = self._login('manager@example.com', 'manager1234')

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _login(self, email, password):
        response = self.client.post('/login', json={'email': email, 'password': password})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('password', response.get_json()['user'])
        return response.get_json()['token']

    @staticmethod
    def _auth(token):
        return {'Authorization': f'Bearer {token}'}

    def test_public_and_authentication_contracts(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/health').status_code, 200)
        self.assertEqual(self.client.get('/tasks').status_code, 401)
        self.assertEqual(self.client.get('/tasks', headers=self._auth('invalid')).status_code, 401)
        self.assertEqual(self.client.post('/login', json={'email': 'x', 'password': 'x'}).status_code, 401)

    def test_user_contracts(self):
        headers = self._auth(self.admin_token)
        users = self.client.get('/users', headers=headers)
        self.assertEqual(users.status_code, 200)
        self.assertNotIn('password', users.get_json()[0])

        user = self.client.get('/users/1', headers=headers)
        self.assertEqual(user.status_code, 200)
        self.assertNotIn('password', user.get_json())
        self.assertEqual(self.client.get('/users/1/tasks', headers=headers).status_code, 200)

        created = self.client.post('/users', headers=headers, json={
            'name': 'Novo Usuário', 'email': 'novo@example.com', 'password': 'segura123', 'role': 'user'
        })
        self.assertEqual(created.status_code, 201)
        user_id = created.get_json()['id']
        updated = self.client.put(f'/users/{user_id}', headers=headers, json={'name': 'Nome Atualizado'})
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(self.client.delete(f'/users/{user_id}', headers=headers).status_code, 200)

    def test_task_contracts(self):
        headers = self._auth(self.admin_token)
        self.assertEqual(self.client.get('/tasks', headers=headers).status_code, 200)
        self.assertEqual(self.client.get('/tasks/1', headers=headers).status_code, 200)
        self.assertEqual(self.client.get('/tasks/search?q=inicial', headers=headers).status_code, 200)
        self.assertEqual(self.client.get('/tasks/search?priority=invalid', headers=headers).status_code, 400)
        self.assertEqual(self.client.get('/tasks/stats', headers=headers).status_code, 200)

        created = self.client.post('/tasks', headers=headers, json={
            'title': 'Nova task', 'priority': 3, 'user_id': 1, 'category_id': 1,
            'tags': ['test', 'contract'], 'due_date': '2030-01-01'
        })
        self.assertEqual(created.status_code, 201)
        task_id = created.get_json()['id']
        self.assertEqual(self.client.put(f'/tasks/{task_id}', headers=headers,
                                         json={'status': 'in_progress'}).status_code, 200)
        self.assertEqual(self.client.delete(f'/tasks/{task_id}', headers=headers).status_code, 200)

    def test_report_and_category_contracts(self):
        admin_headers = self._auth(self.admin_token)
        manager_headers = self._auth(self.manager_token)
        self.assertEqual(self.client.get('/reports/summary', headers=manager_headers).status_code, 200)
        self.assertEqual(self.client.get('/reports/user/1', headers=manager_headers).status_code, 200)
        self.assertEqual(self.client.get('/categories', headers=manager_headers).status_code, 200)

        created = self.client.post('/categories', headers=admin_headers, json={
            'name': 'Frontend', 'description': 'UI', 'color': '#abcdef'
        })
        self.assertEqual(created.status_code, 201)
        category_id = created.get_json()['id']
        self.assertEqual(self.client.put(f'/categories/{category_id}', headers=admin_headers,
                                         json={'color': '#fedcba'}).status_code, 200)
        self.assertEqual(self.client.delete(f'/categories/{category_id}', headers=admin_headers).status_code, 200)

    def test_file_persistence_survives_app_recreation(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = os.path.join(directory, 'contracts.db').replace('\\', '/')
            database_uri = f'sqlite:///{database_path}'
            first_app = create_app({
                'TESTING': True,
                'SQLALCHEMY_DATABASE_URI': database_uri,
                'SECRET_KEY': 'persistence-test-secret',
            })
            with first_app.app_context():
                db.create_all()
                db.session.add(Category(name='Persistida', color='#123456'))
                db.session.commit()
                db.session.remove()
                db.engine.dispose()

            second_app = create_app({
                'TESTING': True,
                'SQLALCHEMY_DATABASE_URI': database_uri,
                'SECRET_KEY': 'persistence-test-secret',
            })
            with second_app.app_context():
                self.assertEqual(db.session.scalar(select(func.count(Category.id))), 1)
                db.session.remove()
                db.engine.dispose()


if __name__ == '__main__':
    unittest.main()
