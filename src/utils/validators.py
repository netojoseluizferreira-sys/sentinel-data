import re

def limpar_cpf(cpf_sujo: str) -> str:
    """
    Remove pontos, traços e espaços, deixando apenas números.
    """
    if not cpf_sujo:
        return ""
    # Usa Regex para manter apenas o que for número
    return re.sub(r'\D', '', cpf_sujo)

def validar_cpf(cpf_bruto: str) -> str | None:
    """
    Executa a limpeza e validação matemática do CPF.
    Retorna o CPF limpo se válido, ou None se inválido.
    """
    cpf = limpar_cpf(cpf_bruto)

    # 1. Verifica se tem 11 dígitos ou se é uma sequência repetida (ex: 111.111...)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return None

    # 2. Cálculo do Primeiro Dígito Verificador
    soma = 0
    for i, peso in enumerate(range(10, 1, -1)):
        soma += int(cpf[i]) * peso
    
    resto = (soma * 10) % 11
    digito_1 = resto if resto < 10 else 0
    
    if digito_1 != int(cpf[9]):
        return None

    # 3. Cálculo do Segundo Dígito Verificador
    soma = 0
    for i, peso in enumerate(range(11, 1, -1)):
        soma += int(cpf[i]) * peso
        
    resto = (soma * 10) % 11
    digito_2 = resto if resto < 10 else 0
    
    if digito_2 != int(cpf[10]):
        return None

    return cpf  # CPF válido e limpo