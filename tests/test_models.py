import random
from dataclasses import asdict, dataclass
from faker import Faker


faker = Faker("pt_BR")


@dataclass
class Pessoa:
    nome: str
    cpf: str
    email: str
    idade: int
    saldo: float


def gerar_modelo() -> dict:
    """
    Gera um registro de Pessoa com dados aleatórios
    e retorna o modelo convertido para dicionário.
    """
    pessoa = Pessoa(
        nome=faker.name(),
        cpf=faker.cpf().replace(".", "").replace("-", ""),
        email=faker.email(),
        idade=random.randint(18, 80),
        saldo=round(random.uniform(0, 10000), 2)
    )

    return asdict(pessoa)