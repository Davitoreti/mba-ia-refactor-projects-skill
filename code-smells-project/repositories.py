from models import Order, OrderItem, Product, User


def _product(row):
    return Product(
        id=row["id"],
        nome=row["nome"],
        descricao=row["descricao"],
        preco=row["preco"],
        estoque=row["estoque"],
        categoria=row["categoria"],
        ativo=row["ativo"],
        criado_em=row["criado_em"],
    )


class ProductRepository:
    def __init__(self, database):
        self.database = database

    def list(self, limit, offset):
        rows = self.database.execute(
            "SELECT * FROM produtos ORDER BY id LIMIT ? OFFSET ?", (limit, offset)
        ).fetchall()
        return [_product(row) for row in rows]

    def get(self, product_id):
        row = self.database.execute(
            "SELECT * FROM produtos WHERE id = ?", (product_id,)
        ).fetchone()
        return _product(row) if row else None

    def create(self, product):
        cursor = self.database.execute(
            """INSERT INTO produtos (nome, descricao, preco, estoque, categoria)
               VALUES (?, ?, ?, ?, ?)""",
            (
                product["nome"],
                product["descricao"],
                product["preco"],
                product["estoque"],
                product["categoria"],
            ),
        )
        self.database.commit()
        return cursor.lastrowid

    def update(self, product_id, product):
        cursor = self.database.execute(
            """UPDATE produtos
               SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ?
               WHERE id = ?""",
            (
                product["nome"],
                product["descricao"],
                product["preco"],
                product["estoque"],
                product["categoria"],
                product_id,
            ),
        )
        self.database.commit()
        return cursor.rowcount > 0

    def delete(self, product_id):
        cursor = self.database.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
        self.database.commit()
        return cursor.rowcount > 0

    def search(self, term, category, minimum_price, maximum_price, limit, offset):
        clauses = ["ativo = 1"]
        parameters = []
        if term:
            clauses.append("(nome LIKE ? OR descricao LIKE ?)")
            pattern = f"%{term}%"
            parameters.extend([pattern, pattern])
        if category:
            clauses.append("categoria = ?")
            parameters.append(category)
        if minimum_price is not None:
            clauses.append("preco >= ?")
            parameters.append(minimum_price)
        if maximum_price is not None:
            clauses.append("preco <= ?")
            parameters.append(maximum_price)
        parameters.extend([limit, offset])

        rows = self.database.execute(
            f"SELECT * FROM produtos WHERE {' AND '.join(clauses)} ORDER BY id LIMIT ? OFFSET ?",
            parameters,
        ).fetchall()
        return [_product(row) for row in rows]


class UserRepository:
    def __init__(self, database):
        self.database = database

    @staticmethod
    def _user(row):
        return User(
            id=row["id"],
            nome=row["nome"],
            email=row["email"],
            tipo=row["tipo"],
            criado_em=row["criado_em"] if "criado_em" in row.keys() else None,
        )

    def list(self, limit, offset):
        rows = self.database.execute(
            "SELECT id, nome, email, tipo, criado_em FROM usuarios ORDER BY id LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [self._user(row) for row in rows]

    def get(self, user_id):
        row = self.database.execute(
            "SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?",
            (user_id,),
        ).fetchone()
        return self._user(row) if row else None

    def find_for_login(self, email):
        return self.database.execute(
            "SELECT id, nome, email, senha, tipo, criado_em FROM usuarios WHERE email = ?",
            (email,),
        ).fetchone()

    def create(self, name, email, password_hash):
        cursor = self.database.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, 'cliente')",
            (name, email, password_hash),
        )
        self.database.commit()
        return cursor.lastrowid


class OrderRepository:
    def __init__(self, database):
        self.database = database

    def product_for_update(self, product_id):
        return self.database.execute(
            "SELECT id, nome, preco, estoque FROM produtos WHERE id = ? AND ativo = 1",
            (product_id,),
        ).fetchone()

    def create_order(self, user_id, total):
        cursor = self.database.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (user_id, total),
        )
        return cursor.lastrowid

    def create_item(self, order_id, product_id, quantity, unit_price):
        self.database.execute(
            """INSERT INTO itens_pedido
               (pedido_id, produto_id, quantidade, preco_unitario)
               VALUES (?, ?, ?, ?)""",
            (order_id, product_id, quantity, unit_price),
        )

    def decrease_stock(self, product_id, quantity):
        cursor = self.database.execute(
            """UPDATE produtos SET estoque = estoque - ?
               WHERE id = ? AND estoque >= ?""",
            (quantity, product_id, quantity),
        )
        return cursor.rowcount > 0

    def list(self, limit, offset, user_id=None):
        where = "WHERE p.usuario_id = ?" if user_id is not None else ""
        parameters = [user_id] if user_id is not None else []
        parameters.extend([limit, offset])
        rows = self.database.execute(
            f"""SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
                       i.produto_id, i.quantidade, i.preco_unitario,
                       pr.nome AS produto_nome
                FROM (
                    SELECT * FROM pedidos p {where}
                    ORDER BY p.id LIMIT ? OFFSET ?
                ) p
                LEFT JOIN itens_pedido i ON i.pedido_id = p.id
                LEFT JOIN produtos pr ON pr.id = i.produto_id
                ORDER BY p.id, i.id""",
            parameters,
        ).fetchall()
        return self._group_orders(rows)

    @staticmethod
    def _group_orders(rows):
        orders = {}
        for row in rows:
            order = orders.setdefault(
                row["id"],
                Order(
                    id=row["id"],
                    usuario_id=row["usuario_id"],
                    status=row["status"],
                    total=row["total"],
                    criado_em=row["criado_em"],
                ),
            )
            if row["produto_id"] is not None:
                order.itens.append(
                    OrderItem(
                        produto_id=row["produto_id"],
                        produto_nome=row["produto_nome"] or "Desconhecido",
                        quantidade=row["quantidade"],
                        preco_unitario=row["preco_unitario"],
                    )
                )
        return list(orders.values())

    def update_status(self, order_id, status):
        cursor = self.database.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?", (status, order_id)
        )
        self.database.commit()
        return cursor.rowcount > 0

    def sales_report(self):
        return self.database.execute(
            """SELECT COUNT(*) AS total_pedidos,
                      COALESCE(SUM(total), 0) AS faturamento,
                      COALESCE(SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END), 0) AS pendentes,
                      COALESCE(SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END), 0) AS aprovados,
                      COALESCE(SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END), 0) AS cancelados
               FROM pedidos"""
        ).fetchone()
