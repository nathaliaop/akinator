from flask import Flask, request
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_release_year(df):
    total = len(df["release_year"]) #there is no nan in this column
    release_year = df["release_year"].value_counts().div(total)
    return (min(1 - release_year[release_year.index[0]], release_year[release_year.index[0]]), release_year.index[0], "release_year")

def get_country(df):
    total = len(df["country"]) #including nan
    countries = df["country"].value_counts().div(total)
    return (min(1 - countries[0], countries[0]), countries.index[0], "country")

def get_type(df):
    total = len(df["type"]) #there is no nan in this column
    types = df["type"].value_counts().div(total)
    return (min(1 - types[0], types[0]), types.index[0], "type")

def preprocess(df):
    if "date_added" in df:
      del df["date_added"]

    return df

def question_asked(question, response_json):
    for object in response_json["questions"]:
      if question == object["column"]:
        return True
    return False

def guess_asked(guess, response_json):
    for object in response_json["guesses"]:
      if guess == object:
        return True
    return False

@app.route('/', methods=['POST'])
def hello_world():
    response_json = request.get_json()

    df = pd.read_csv("datasets/amazon_prime_titles.csv")

    df = preprocess(df)

    for object in response_json["questions"]:
      # print(object)
      
      if object["answer"] == "yes":
        df = df.loc[df[object["column"]] == object["data"]]
      elif object["answer"] == "no":
        df = df.loc[df[object["column"]] != object["data"]]

    df = df.reset_index(drop=True)

    if len(df) == 0:
      response_json["guesses"].append(None)
      return response_json

    attributes = [get_release_year(df), get_country(df), get_type(df)]
    attributes.sort(reverse=True)
    
    guess = False

    it = 0
    while question_asked(attributes[it][2], response_json):
      it += 1

      if it == len(attributes):
        guess = True
        break
    
    if guess:
      it = 0
      while guess_asked(df['title'].iloc[it], response_json):
        it += 1

        if it == len(df):
          response_json["guesses"].append(None)
          return response_json
      
      response_json["guesses"].append(df['title'].iloc[it])
    else:
      response_json["questions"].append({
        "column": str(attributes[it][2]),
        "data": str(attributes[it][1]),
        "answer": None
      })

    return response_json