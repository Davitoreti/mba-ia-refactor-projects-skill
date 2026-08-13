import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "test-only-secret-key")

from app import create_app
from database import get_db, init_db


class ApiContractTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = str(Path(self.temporary_directory.name) / "test.db")
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE_PATH": self.database_path,
                "ENVIRONMENT": "testing",
                "SESSION_COOKIE_SECURE": False,
            }
        )
        with self.app.app_context():
            init_db()
        self.client = self.app.test_client()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def login(self, email="admin@loja.com", password="admin123"):
        response = self.client.post(
            "/login", json={"email": email, "senha": password}
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        return response

    def test_public_read_contracts_and_health_do_not_expose_secrets(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        products = self.client.get("/produtos")
        self.assertEqual(products.status_code, 200)
        self.assertTrue(products.get_json()["dados"])
        product_id = products.get_json()["dados"][0]["id"]
        self.assertEqual(self.client.get(f"/produtos/{product_id}").status_code, 200)
        self.assertEqual(self.client.get("/produtos/999999").status_code, 404)
        search = self.client.get("/produtos/busca?q=Mouse&preco_min=1")
        self.assertEqual(search.status_code, 200)
        self.assertIn("total", search.get_json())
        health = self.client.get("/health")
        self.assertEqual(health.status_code, 200)
        payload = health.get_json()
        self.assertNotIn("secret_key", payload)
        self.assertNotIn("db_path", payload)

    def test_search_is_parameterized_and_invalid_numbers_return_400(self):
        injection = self.client.get(
            "/produtos/busca", query_string={"q": "' OR 1=1 --"}
        )
        self.assertEqual(injection.status_code, 200)
        self.assertEqual(injection.get_json()["dados"], [])
        invalid = self.client.get("/produtos/busca?preco_min=barato")
        self.assertEqual(invalid.status_code, 400)

    def test_authentication_and_user_responses_hide_passwords(self):
        self.assertEqual(self.client.get("/usuarios").status_code, 401)
        login = self.login()
        self.assertNotIn("senha", login.get_json()["dados"])
        users = self.client.get("/usuarios")
        self.assertEqual(users.status_code, 200)
        self.assertNotIn("senha", users.get_json()["dados"][0])
        user_id = users.get_json()["dados"][0]["id"]
        self.assertNotIn(
            "senha", self.client.get(f"/usuarios/{user_id}").get_json()["dados"]
        )
        created = self.client.post(
            "/usuarios",
            json={
                "nome": "Cliente Teste",
                "email": "cliente@teste.com",
                "senha": "segura123",
            },
        )
        self.assertEqual(created.status_code, 201)
        duplicate = self.client.post(
            "/usuarios",
            json={
                "nome": "Outro",
                "email": "cliente@teste.com",
                "senha": "segura123",
            },
        )
        self.assertEqual(duplicate.status_code, 409)

    def test_plaintext_legacy_password_is_migrated_on_initialization(self):
        with self.app.app_context():
            get_db().execute(
                "UPDATE usuarios SET senha = ? WHERE email = ?",
                ("admin123", "admin@loja.com"),
            )
            get_db().commit()
        self.app.extensions["database_initialized"] = False
        self.login()
        with self.app.app_context():
            stored_password = get_db().execute(
                "SELECT senha FROM usuarios WHERE email = ?", ("admin@loja.com",)
            ).fetchone()[0]
        self.assertNotEqual(stored_password, "admin123")

    def test_admin_product_crud_contracts(self):
        unauthorized = self.client.post(
            "/produtos", json={"nome": "Novo", "preco": 10, "estoque": 2}
        )
        self.assertEqual(unauthorized.status_code, 401)
        self.login()
        created = self.client.post(
            "/produtos",
            json={"nome": "Novo produto", "preco": 10.5, "estoque": 2},
        )
        self.assertEqual(created.status_code, 201)
        product_id = created.get_json()["dados"]["id"]
        updated = self.client.put(
            f"/produtos/{product_id}",
            json={"nome": "Produto atualizado", "preco": 11, "estoque": 3},
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(self.client.delete(f"/produtos/{product_id}").status_code, 200)

    def test_order_flow_preserves_nested_response_and_stock(self):
        self.login("joao@email.com", "123456")
        created = self.client.post(
            "/pedidos",
            json={
                "usuario_id": 2,
                "itens": [{"produto_id": 1, "quantidade": 1}],
            },
        )
        self.assertEqual(created.status_code, 201, created.get_json())
        order_id = created.get_json()["dados"]["pedido_id"]
        own_orders = self.client.get("/pedidos/usuario/2")
        self.assertEqual(own_orders.status_code, 200)
        self.assertEqual(own_orders.get_json()["dados"][0]["id"], order_id)
        self.assertTrue(own_orders.get_json()["dados"][0]["itens"])
        self.assertEqual(self.client.get("/pedidos/usuario/1").status_code, 403)
        self.assertEqual(self.client.get("/pedidos").status_code, 403)
        self.client.post("/logout")
        self.login()
        self.assertEqual(self.client.get("/pedidos").status_code, 200)
        updated = self.client.put(
            f"/pedidos/{order_id}/status", json={"status": "aprovado"}
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(self.client.get("/relatorios/vendas").status_code, 200)

    def test_order_failure_rolls_back(self):
        self.login("joao@email.com", "123456")
        with self.app.app_context():
            before_orders = get_db().execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
            before_stock = get_db().execute(
                "SELECT estoque FROM produtos WHERE id = 1"
            ).fetchone()[0]
        response = self.client.post(
            "/pedidos",
            json={
                "usuario_id": 2,
                "itens": [
                    {"produto_id": 1, "quantidade": 1},
                    {"produto_id": 999999, "quantidade": 1},
                ],
            },
        )
        self.assertEqual(response.status_code, 400)
        with self.app.app_context():
            after_orders = get_db().execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
            after_stock = get_db().execute(
                "SELECT estoque FROM produtos WHERE id = 1"
            ).fetchone()[0]
        self.assertEqual(after_orders, before_orders)
        self.assertEqual(after_stock, before_stock)

    def test_admin_sql_endpoint_is_disabled(self):
        unauthorized = self.client.post("/admin/query", json={"sql": "SELECT 1"})
        self.assertEqual(unauthorized.status_code, 401)
        self.login()
        disabled = self.client.post("/admin/query", json={"sql": "SELECT 1"})
        self.assertEqual(disabled.status_code, 410)
        self.assertEqual(self.client.post("/admin/reset-db").status_code, 200)
        health = self.client.get("/health")
        self.assertEqual(health.get_json()["counts"]["produtos"], 0)
        self.assertEqual(health.get_json()["counts"]["usuarios"], 0)


if __name__ == "__main__":
    unittest.main()
