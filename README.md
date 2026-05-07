# 🛡️ Sentinel Data: High-Performance ETL Pipeline

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![SQLite](https://img.shields.io/badge/SQLite-Native-003B57?style=flat-square&logo=sqlite)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit)
![Pytest](https://img.shields.io/badge/Pytest-TDD-0A9EDC?style=flat-square&logo=pytest)
![Rich](https://img.shields.io/badge/Rich-CLI-8A2BE2?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

> **Sentinel Data** é um ecossistema completo de Engenharia de Dados focado em **extração, sanitização, validação e persistência** de grandes volumes de dados. Construído inteiramente em Python moderno, o projeto abandona o uso de bibliotecas de manipulação em memória massiva (como o Pandas) em favor de uma arquitetura limpa, eficiente e baseada em processamento contínuo (Streaming/Generators).

---

## 📖 Índice

1. [Sobre o Projeto](#-sobre-o-projeto)
2. [O Problema da Memória (Por que não usar Pandas?)](#-o-problema-da-memória-por-que-não-usar-pandas)
3. [Arquitetura e Engenharia de Software](#-arquitetura-e-engenharia-de-software)
4. [A Triagem e o "Usuário Batata"](#-a-triagem-e-o-usuário-batata)
5. [Interface de Usuário e Observabilidade](#-interface-de-usuário-e-observabilidade)
6. [Stack Tecnológica](#-stack-tecnológica)
7. [Guia de Instalação e Execução](#-guia-de-instalação-e-execução)
8. [Qualidade e Testes](#-qualidade-e-testes)
9. [Padrões de Desenvolvimento](#-padrões-de-desenvolvimento)

---

## 🎯 Sobre o Projeto

O processamento de dados no mundo real raramente lida com arquivos limpos e estruturados. Pipelines de dados enfrentam constantes desafios: CPFs inválidos, e-mails mal formatados, preços negativos e dados corrompidos. 

O **Sentinel Data** atua como uma barreira de segurança e higienização. Ele ingere gigabytes de dados de arquivos CSV desestruturados, aplica regras estritas de validação orientadas a objetos, bloqueia dados corrompidos de entrarem no banco de dados, e gera relatórios de auditoria precisos sem comprometer o hardware do servidor.

---

## 🧠 O Problema da Memória (Por que não usar Pandas?)

### O Gargalo Tradicional (*Out-Of-Memory*)
A abordagem mais comum (e acadêmica) para analisar arquivos CSV é utilizar o Pandas (`pd.read_csv()`). No entanto, o Pandas carrega todo o *DataFrame* na memória RAM de uma só vez. Se o seu arquivo bruto tem 10 GB e sua máquina possui 8 GB de RAM, o sistema operacional irá matar o processo, resultando em uma falha catastrófica.

### A Solução Sentinel: *Lazy Evaluation* e Geradores
Para contornar as limitações físicas de hardware, o Sentinel Data foi desenhado para operar como uma esteira de manufatura. 
Utilizando **Geradores do Python (`yield`)**, o sistema executa a leitura, a transformação e a carga **linha a linha**.
* O arquivo nunca é carregado inteiramente na memória.
* O uso de CPU e RAM permanece estável (estritamente plano - *flatline*), não importa se o arquivo processado tem 100 Megabytes ou 50 Gigabytes.
* Os dados são processados e descarregados no banco de dados em pequenos lotes (chunks) otimizados.

---

## 🏗️ Arquitetura e Engenharia de Software

O coração do Sentinel Data é construído sobre pilares estritos de **Orientação a Objetos Avançada**, Design Patterns e o Princípio da Responsabilidade Única (SOLID).

### Padrão *Template Method* (O Contrato Abstrato)
A orquestração do pipeline é feita por uma **Classe Abstrata (ABC)** chamada `ETL_Core`. Ela define um contrato blindado de três etapas que todas as entidades do sistema devem seguir, mas deixa os detalhes de implementação para as classes filhas:
1. **`extrair()`**: Lógica de varredura do arquivo CSV usando bibliotecas nativas como `csv.reader`.
2. **`transformar()`**: A execução do "Juiz". Onde as regras de negócio sanitizam a linha atual.
3. **`carregar()`**: A consolidação segura no destino final.

As classes `Cliente` e `Venda` herdam o `ETL_Core` e aplicam suas próprias validações via **Polimorfismo**.

### Idempotência com o `DB_Check`
Carregar milhões de IDs na memória para evitar duplicatas derrotaria o propósito do pipeline de baixa memória. Para resolver isso, o sistema implementa um **`DB_Check`** contínuo e otimizado usando SQL Nativo. O Sentinel executa checagens cirúrgicas no SQLite antes de gravar, garantindo que o banco de dados permaneça como uma "Fonte de Verdade" livre de chaves duplicadas.

---

## 🥔 A Triagem e o "Usuário Batata"

O ecossistema foi projetado para sobreviver ao caos através de um conceito de desenvolvimento chamado **Testes de Estresse contra o "Usuário Batata"** — entradas de dados aleatórias, ilógicas ou maliciosas (ex: digitar uma string de texto em um campo financeiro).

A triagem do pipeline divide o fluxo de dados em três caminhos distintos:

| Categoria | Status | Comportamento do Sistema |
| :--- | :---: | :--- |
| **🟢 Verdes** | **Sucesso** | Dados matematicamente válidos. Inseridos diretamente no banco de dados (SQLite). |
| **🟡 Amarelos** | **Atenção** | Dados com inconsistências (ex: espaços extras num e-mail) que a inteligência da classe conseguiu auto-corrigir. São salvos, mas alertam o log. |
| **🔴 Vermelhos** | **Falha Crítica** | Dados irrecuperáveis ou fraudulentos (ex: CPF falso). **Descarte sumário.** O banco de dados não é tocado. |

### O Sistema de Auditoria (JSONL)
O que acontece com os dados descartados? Eles alimentam um sistema de auditoria impecável.
Ao invés de carregar logs na RAM, a classe de Telemetria e Registro usa o formato **JSONL (JSON Lines)** em modo *append* (`a`). Cada linha com erro é convertida em um JSON válido e gravada em disco. 
Isso garante que:
1. O log nunca corrompe em caso de quedas de energia.
2. É infinitamente escalável (ocupa pouco disco).
3. O analista de negócios pode ler exatamente o que falhou sem abrir o arquivo original de 10 GB.

---

## 📡 Interface de Usuário e Observabilidade

Embora o *core* seja um script Python pesado, a operação do sistema foi dividida em duas experiências visuais para facilitar a vida da equipe de dados.

### 1. A Torre de Comando (CLI via Rich)
Para o Engenheiro de Dados, o sistema não roda em "telas pretas monótonas". Utilizando a biblioteca `Rich`, o terminal é convertido em um painel interativo exibindo:
* Barras de progresso dinâmicas reais.
* Contagem contínua de "Verdes, Amarelos e Vermelhos".
* Cálculos precisos de *Throughput* (linhas processadas por segundo).

### 2. O Observatório Analítico (Streamlit)
Para o Cientista de Dados e Gestores, o projeto sobe um servidor local web usando `Streamlit`. Esse painel nunca lê os arquivos brutos. Ele acessa os resumos consolidados no SQLite e a tabela de erros no JSONL, oferecendo:
* Gráficos financeiros das perdas evitadas (o que foi barrado como "Vermelho").
* Filtros de data para entender picos de anomalias na ingestão de dados.
* Dashboards interativos de altíssimo desempenho.

---

## 🛠️ Stack Tecnológica

O Sentinel Data depende apenas do ecossistema essencial, evitando dependências gigantescas. Todas estão mapeadas no `requirements.txt`.

* **Python Base (`typing`, `abc`, `csv`, `sqlite3`):** Para o *core* do sistema.
* **Rich:** Para UI de terminal de alta fidelidade.
* **Streamlit:** Para criação do Data Dashboard.
* **Faker:** Para injetar dados falsos (caos) de forma contínua durante testes.
* **Pytest:** Para testes unitários rigorosos (TDD).

---

## 🚀 Guia de Instalação e Execução

O Sentinel Data foi feito para ser clonado e operado localmente de maneira isolada. Siga os passos:

### 1. Preparação do Ambiente
Faça o clone do repositório e crie um ambiente virtual para isolar as dependências.
```bash
# Clone o repositório
git clone [https://github.com/SEU_USUARIO/sentinel-data.git](https://github.com/SEU_USUARIO/sentinel-data.git)
cd sentinel-data

# Crie o ambiente virtual (VENV)
python -m venv venv

# Ative o ambiente
# No Linux/MacOS:
source venv/bin/activate
# No Windows:
venv\Scripts\activate