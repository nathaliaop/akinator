# Akinator
Jogo no estilo Akinator para a disciplina de Projeto e Análise de Algoritmos

# Clonar o projeto
```
# clonar o repositório
git clone https://github.com/nathaliaop/akinator.git

# acessar o diretório do projeto
cd akinator
```

# Adicionar variáveis de ambiente
Adicionar uma arquivo chamado .env com o seguinte conteúdo
```
PORT=5000
```

## Criar ambiente virtual e instalar dependências:
```
# criar o ambiente virtual 
python -m venv env

# windows - ativar o ambiente virtual
env/scripts/activate

# linux - ativar o ambiente virtual
source env/bin/activate

# desativar ambiente virtual caso necessário
deactivate

# instalar dependências
pip install -r requirements.txt
```
## Executando o projeto
```
flask --app main --debug run
```

## Fazendo requisições

Url de desenvolvimento: `http://localhost:5000`

Url de produção: `https://akinator.up.railway.app`

Rota: `/`

Método: POST

Requisição
```json
{
  "questions" : [
  ],
  "guesses": [
  ]
}
```

Resposta:
```json
{
  "questions": [
    {
      "answer": null,
      "column": "type",
      "data": "Movie"
    }
  ],
  "guesses": [
  ]
}
```


O tipo é filme? Após fazer a pergunta, mandar a requisição novamente com a resposta. Respostas possível são `yes` para sim, `no` para não e `idk` para não sei.

Requisição:
```json
{
  "questions" : [
    {
      "answer": "yes",
      "column": "type",
      "data": "Movie"
    }
  ],
  "guesses": [
  ]
}
```

Resposta:
```json
{
  "questions" : [
    {
      "answer": "yes",
      "column": "type",
      "data": "Movie"
    },
    {
      "answer": null,
      "column": "release_year",
      "data": "2021"
    }
  ],
  "guesses": [
  ]
}
```

Mandar as respostas anteriores junto a cada nova requisição. Quando houver informações o suficiente, a resposta será adicionada ao array guesses. Caso a reposta esteja incorreta, reenviar a requisição e uma nova resposta será adicionada ao array guesses. Se não houver mais respostas possíveis, null será adicionado ao array guesses.

Requisição:
```json
{
  "questions" : [
    {
      "answer": "yes",
      "column": "type",
      "data": "Movie"
    },
    {
      "answer": "idk",
      "column": "release_year",
      "data": "2021"
    },
    {
      "answer": "no",
      "column": "country",
      "data": "India"
    }
  ],
  "guesses": [
    "The Grand Seduction"
  ]
}
```

Resposta:
```json
{
  "questions" : [
    {
      "answer": "yes",
      "column": "type",
      "data": "Movie"
    },
    {
      "answer": "idk",
      "column": "release_year",
      "data": "2021"
    },
    {
      "answer": "no",
      "column": "country",
      "data": "India"
    }
  ],
  "guesses": [
    "The Grand Seduction",
    null
  ]
}
```
