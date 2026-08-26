 DataPolisher 

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Flet](https://img.shields.io/badge/GUI-Flet-darkblue.svg)
![Pandas](https://img.shields.io/badge/Data-Pandas-150458.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

O **DataPolisher Studio** é uma aplicação desktop moderna projetada para simplificar a etapa mais demorada da Ciência de Dados: a higienização e tratamento de bases de dados (Data Cleaning). 

Focado na experiência do usuário (UX), ele permite que cientistas de dados, analistas e estudantes preparem seus arquivos de forma visual, sem a necessidade de escrever scripts complexos, mantendo a integridade dos dados e otimizando o tempo de análise.

<p align="center">
  <!-- DICA: Tire um print do seu app rodando, salve na pasta assets com o nome "screenshot.png" e tire o comentário abaixo -->
  <!-- <img src="assets/screenshot.png" alt="Tela inicial do DataPolisher" width="800"> -->
</p>

---

##  Funcionalidades em Destaque

###  Transformação de Dados
* **Limpeza Inteligente:** Preenchimento de valores nulos (NaN) com tipagem dinâmica, evitando que colunas numéricas sejam corrompidas.
* **Padronização Textual:** Interface dedicada para normalização de strings (minúsculas, maiúsculas, título) removendo acentos e espaços extras.
* **Filtros e Remoções:** Remoção de duplicatas com um clique e isolamento de dados via filtros precisos de linha ou coluna.
* **Controle de Estado:** Sistema de histórico na memória (Undo) que permite desfazer ações destrutivas acidentais.

### Interface e Experiência (UI/UX)
* **Design Responsivo e Moderno:** Construído sob o `Flet`, com controles nativos, feedback de interação e layout adaptável.
* **Navegação Avançada:** Tabela de dados (Treeview) estilizada com suporte a *Swipe/Arraste Horizontal* nativo no desktop.
* **Personalização Completa:** 
  * Menu flutuante animado.
  * Internacionalização nativa (Suporte a Português e Inglês).
  * Alternância de Tema (Modo Claro / Modo Escuro).
  * Escala de fonte dinâmica para acessibilidade.

---

## Arquitetura e Tecnologias

O projeto foi construído seguindo boas práticas de engenharia de software (Clean Code e Separação de Preocupações):
* **Backend (Regras de Negócio):** `Python` e `Pandas` (isolados no módulo `cleaner.py`).
* **Frontend (Visual):** `Flet` (isolado no módulo `interface.py`).

### Estrutura do Projeto
```text
DataPolisher/
├── assets/                 # Ícones, imagens e recursos visuais
│   └── iconeData1.png
├── src/                    # Código fonte (Source)
│   ├── main.py             # Ponto de entrada do aplicativo
│   ├── interface.py        # Camada de visualização (Frontend)
│   └── cleaner.py          # Camada de lógica e dados (Backend)
├── README.md               # Documentação do projeto
└── requirements.txt        # Dependências do Python
