import csv
from itertools import islice
from pathlib import Path


def ler_csv_em_lotes(pasta, tamanho_do_lote):
    """
    Lê arquivos CSV de uma pasta de forma incremental.

    Cada chamada ao generator retorna apenas um lote de registros,
    evitando carregar o arquivo inteiro na memória.

    Args:
        pasta: Caminho da pasta que contém os arquivos CSV.
        tamanho_do_lote: Quantidade máxima de registros mantidos
            em memória por vez.

    Yields:
        list[dict]: Um lote de registros representados como dicionários.
    """
    caminhos = Path(pasta).glob("*.csv")

    for arquivo in caminhos:
        with open(
            arquivo, mode="r", encoding="utf-8", newline="") as f:

            # DictReader permite trabalhar com os nomes das colunas
            # desde o início, o que será importante quando o Schema
            # definir como cada campo deve ser tratado.
            leitor = csv.DictReader(f)

            while True:
                # islice consome apenas os próximos registros necessários.
                # O list() materializa somente o lote atual, mantendo o
                # restante do arquivo sob controle do generator.
                lote = list(islice(leitor, tamanho_do_lote))

                # Um lote vazio significa que não existem mais registros
                # no arquivo atual.
                if not lote:
                    break

                yield lote


# Configuração provisória para os testes iniciais.
# Posteriormente, esses valores serão fornecidos por outra camada
# do Sentinel.

TAMANHO_DO_LOTE = 1
PASTA_ALVO = "./generator"


# Consumindo o generator para validar seu comportamento.
if __name__ == "__main__":
    for lote in ler_csv_em_lotes(PASTA_ALVO, TAMANHO_DO_LOTE):
        print(f"Processando {len(lote)} registros")

        for registro in lote:
            print(registro)