import pytest
from src.utils.validators import validar_cpf, limpar_cpf, string_para_centavos

# --- TESTES DE LIMPEZA ---

# O @pytest.mark.parametrize funciona como um "loop" para o seu teste.
# 1. O primeiro argumento "entrada, esperado" define os nomes das variáveis que o teste vai usar.
# 2. O segundo argumento [ (lista de tuplas) ] contém os dados que serão injetados nessas variáveis.
# Cada tupla dentro da lista representa uma rodada de teste independente.
@pytest.mark.parametrize("entrada, esperado", [
    ("123.456.789-00", "12345678900"),
    ("12345678900", "12345678900"),
    (" 123.456.789-00 ", "12345678900"), # Testa se o sistema ignora espaços inúteis
    ("123-ABC-456", "123456"),            # Testa se o sistema limpa letras acidentais
    ("", ""),                             # Caso de borda: string vazia
    (None, ""),                           # Caso de borda: valor nulo (evita que o sistema quebre/crash)
])
def test_limpar_cpf_exaustivo(entrada, esperado):
    """
    Este teste será executado 6 vezes, uma para cada linha acima.
    Se a 3ª linha falhar, o Pytest te avisará exatamente qual falhou e continuará o resto.
    """
    assert limpar_cpf(entrada) == esperado


# --- TESTES DE CPF (A PROVA DE BALAS) ---

def test_validar_cpf_valido_real():
    # Teste unitário simples: apenas verifica se CPFs reais e corretos passam.
    # O 'is not None' confirma que a função retornou o CPF limpo (sucesso).
    assert validar_cpf("054.432.870-30") is None
    assert validar_cpf("451.341.240-05") is None

# Aqui usamos o parametrize novamente, mas apenas com UMA variável ("cpf_fake").
# Isso é útil quando queremos testar vários erros diferentes e o resultado esperado é sempre o mesmo.
@pytest.mark.parametrize("cpf_fake", [
    "000.000.000-00", # Algoritmo passa, mas é proibido pela Receita
    "111.111.111-11",
    "999.999.999-99",
    "123.456.789-00", # Dígitos verificadores matematicamente incorretos
    "123.456.789-123", # Excesso de caracteres
    "123.456.789",     # Falta de caracteres
    "   .   .   -  ", # Apenas máscara sem números
    "cpf invalido",   # Texto aleatório do Usuário Batata
])
def test_validar_cpf_invalidos_diversos(cpf_fake):
    """
    Para todos esses casos bizarros, o comportamento esperado é retornar None.
    Assim, garantimos que o dado inválido nunca entrará no nosso banco de dados.
    """
    assert validar_cpf(cpf_fake) is None

@pytest.mark.parametrize("entrada, esperado", [
    # --- Precisão Decimal (O terror dos floats) ---
    ("0,10", 10),
    ("0,20", 20),
    ("0,30", 30), # Muitos algoritmos falham aqui e retornam 29 por erro de float
    
    # --- Formatos Híbridos e Sujeira ---
    ("R$ 1.250,55", 125055),  # Padrão BR
    ("  1000  ", 100000),     # Espaços e sem decimais
    ("R$ -50,00", -5000),     # Valores negativos (estornos)
    
    # --- Entradas "Usuário Batata" Nível Hard ---
    ("R$ 1.000,000", 100000), # Três zeros no final (deve ignorar ou arredondar)
    ("0.00005", 0),           # Valor menor que um centavo
    ("9.999.999,99", 999999999), # Valores gigantes (Bilhões de centavos)
    
    # --- Segurança e Falhas ---
    ("Gratuito", 0),          # Texto ao invés de número
    ("R$ --50,00", 0),        # Erro de digitação no sinal
    (None, 0),                # Valor nulo
    ("", 0),                  # String vazia
    ("!!!", 0),               # Apenas símbolos
])
def test_string_para_centavos_exaustivo(entrada, esperado):
    assert string_para_centavos(entrada) == esperado