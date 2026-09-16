# Presença Moodle

Este é um script automatizado para registrar presença no Moodle utilizando Selenium.

## Pré-requisitos

Certifique-se de ter o **Python 3** instalado em sua máquina.

## Passo a Passo para Configuração

Após clonar o repositório, siga os passos abaixo para configurar e executar o projeto:

### 1. Configurar as Variáveis de Ambiente

O projeto utiliza um arquivo `.env` para gerenciar as credenciais com segurança. Primeiro, copie o arquivo de exemplo para criar o seu próprio `.env`:

**No Linux/macOS:**
```bash
cp .env.example .env
```

**No Windows (Prompt de Comando - CMD):**
```cmd
copy .env.example .env
```

**No Windows (PowerShell):**
```powershell
cp .env.example .env
```

### 2. Preencher as Variáveis no `.env`

Abra o arquivo `.env` recém-criado em um editor de texto e preencha as variáveis correspondentes:

```env
MOODLE_USUARIO=seu_usuario_moodle
MOODLE_SENHA=sua_senha_moodle
MOODLE_URL=https://moodle.ufsc.br/mod/attendance/view.php?id=XXXXXX
```

* **`MOODLE_USUARIO`**: O seu login de acesso ao Moodle.
* **`MOODLE_SENHA`**: A sua senha de acesso ao Moodle.
* **`MOODLE_URL`**: Entre na página de presença do Moodle da sua disciplina correspondente, copie a URL completa do seu navegador e cole-a neste campo.

### 3. Criar e Ativar o Ambiente Virtual (Venv)

É altamente recomendado utilizar um ambiente virtual (`venv`) para gerenciar as dependências do projeto de forma isolada.

#### Passo 3.1: Criar o ambiente virtual
```bash
python -m venv .venv
```
*(ou `python3 -m venv .venv` dependendo da sua instalação)*

#### Passo 3.2: Ativar o ambiente virtual

* **No Linux/macOS:**
  ```bash
  source .venv/bin/activate
  ```

* **No Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

* **No Windows (Prompt de Comando - CMD):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

### 4. Instalar as Dependências

Com o ambiente virtual ativado, instale as dependências necessárias executando:

```bash
pip install -r requirements.txt
```

As principais bibliotecas instaladas serão:
* `selenium` (para automação do navegador)
* `webdriver-manager` (para gerenciamento automático do driver do Chrome)
* `python-dotenv` (para ler as variáveis do arquivo `.env`)

### 5. Executar o Script

Com tudo configurado e as dependências instaladas, basta executar o script principal (certifique-se de que o venv está ativado):

```bash
python main.py
```

## Falhas de conexão

Durante o monitoramento, timeouts do Moodle, do Chrome ou do ChromeDriver são tratados como falhas temporárias. O script:

* tenta novamente indefinidamente, com espera crescente entre 5 e 60 segundos;
* emite apenas um alerta sonoro no início de cada sequência de falhas;
* reinicia automaticamente o navegador após três falhas consecutivas, caso o ChromeDriver fique travado;
* retoma o monitoramento e rearma o alerta assim que o carregamento funcionar novamente.

Assim, não é necessário reiniciar o script ou pressionar ENTER quando o Moodle estiver temporariamente indisponível.
