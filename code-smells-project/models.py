from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Product:
    id: int
    nome: str
    descricao: str
    preco: float
    estoque: int
    categoria: str
    ativo: int
    criado_em: str

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class User:
    id: int
    nome: str
    email: str
    tipo: str
    criado_em: str | None = None

    def to_dict(self):
        data = asdict(self)
        if data["criado_em"] is None:
            data.pop("criado_em")
        return data


@dataclass(frozen=True)
class OrderItem:
    produto_id: int
    produto_nome: str
    quantidade: int
    preco_unitario: float

    def to_dict(self):
        return asdict(self)


@dataclass
class Order:
    id: int
    usuario_id: int
    status: str
    total: float
    criado_em: str
    itens: list[OrderItem] = field(default_factory=list)

    def to_dict(self):
        data = asdict(self)
        data["itens"] = [item.to_dict() for item in self.itens]
        return data
