# Akinator
Jogo no estilo Akinator para a disciplina de Projeto e Análise de Algoritmos

## Criar ambiente virtual e instalar dependências:
```
# criar o ambiente virtual 
python -m venv env

# windows - ativar o ambiente virtual
env/scripts/activate

# linux - ativar o ambiente virtual
source env/bin/activate

# instalar dependências
pip install -r requirements.txt
```
## Executando o projeto
```
flask --app main --debug run
```

## Fazendo requisições

Url de desenvolvimento: `http://localhost:5000`

Url de produção: `https://akinator-five.vercel.app`

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


Após fazer a pergunta, mandar a requisição novamente com a resposta

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
  "questions": [
    {
      "answer": "yes",
      "column": "type",
      "data": "Movie"
    }
  ],
  "guesses": [
     "The Grand Seduction"
  ]
}
```
