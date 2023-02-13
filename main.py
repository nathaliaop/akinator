from flask import Flask, request
from flask_cors import cross_origin
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os

app = Flask(__name__)

def str2list(i):
    if type(i) is str:
        return [j.strip() for j in i.split(',')];
    else: # nan values
        return []

def str2int(i):
    return int((i.split())[0])

def mergeRating(i):
    if i in ["G", "ALL", "ALL_AGES", "TV-Y", "TV-G"]:
        return 0
    elif i in ["TV-Y7", "7+"]:
        return 7
    elif i in ["13+", "PG-13"]:
        return 13
    elif i in ["TV-14"]:
        return 14
    elif i in ["16+", "16", "AGES_16_"]:
        return 16
    elif i in ["TV-MA", "NC-17"]:
        return 17
    elif i in ["18+", "AGES_18_", "R"]:
        return 18
    elif i in ["NR", 'TV-NR', 'UNRATED', 'NOT_RATE', "PG", "TV-PG"]:
        return np.nan
    return i

def preprocess(df):
    if "date_added" in df:
      del df["date_added"]

    if "show_id" in df:
      del df["show_id"]

    df["listed_in"] = df["listed_in"].apply( str2list )
    df["director"] = df["director"].apply( str2list )
    df["cast"] = df["cast"].apply( str2list )
    df["duration"] = df["duration"].apply( str2int )
    df["rating"] = df["rating"].apply( mergeRating )

    return df

def get_type(df):
    total = len(df["type"]) 
    types = df["type"].value_counts().div(total)

    return (min(1 - types[0], types[0]), types.index[0], "type")

def get_director(df):
    # only nan remaining
    if df["director"].isnull().all():
        return None
    
    total = len(df["director"])
    
    values = {};
    for collection in df["director"]:
        for director in list(collection):
            director = director.strip()
            if director in values:
                values[director] += 1
            else:
                values[director] = 1

    ordered = [(key, val) for key, val in sorted(values.items(), key = lambda x: x[1], reverse = True)]
    p = ordered[0][1]/total
    return ( min(1-p, p), ordered[0][0], "director")

def get_cast(df):
    if df["cast"].isnull().all():
        return None
    
    total = len(df["cast"]) 
    
    values = {};
    for collection in df["cast"]:
        for actor in list(collection):
            actor = actor.strip()
            if actor in values:
                values[actor] += 1
            else:
                values[actor] = 1
      
    ordered = [(key, val) for key, val in sorted(values.items(), key = lambda x: x[1], reverse = True)]
    p = ordered[0][1]/total
    return ( min(1-p, p), ordered[0][0], "cast")

def get_country(df):
    if df["country"].isnull().all():
        return None
    
    total = len(df["country"]) 
    
    countries = df["country"].value_counts().div(total)

    return (min(1 - countries[0], countries[0]), countries.index[0], "country")

def get_release_year(df):
    total = len(df["release_year"]) 
    
    median = round( df["release_year"].sort_values().median() )
    left = right = 0
    for i in df["release_year"]:
        if i <= median:
            left += 1
        else:
            right += 1
    
    return (min(left/total, right/total), median, "release_year")

def get_rating(df):
    total = len(df["rating"])
    
    if df["rating"].isnull().all():
        return None
    
    median = round( df["rating"].sort_values().median() )
    
    left = right = 0
    for i in df[df["rating"].notnull()]["rating"]:
        if i <= median:
            left += 1
        else:
            right += 1
    
    return (min(left/total, right/total), median, "rating")

def get_duration(df):
    total = len(df["type"])
    
    isMovie = df["type"].unique()[0] == "Movie";

    if isMovie:
        median = round(df[ df["type"] == "Movie" ]["duration"].sort_values().median())
        left = right = 0
        for i in df[ df["type"] == "Movie" ]["duration"]:
            if i <= median:
                left += 1
            else:
                right += 1
        return (min(left/total, right/total), median, "duration")
    
    else:
        median = round(df[ df["type"] == "TV Show" ]["duration"].sort_values().median())
        left = right = 0
        for i in df[ df["type"] == "TV Show" ]["duration"]:
            if i <= median:
                left += 1
            else:
                right += 1
        
        return (min(left/total, right/total), median, "duration")

def get_topics(df):
    total = len(df["listed_in"]) 
    values = {};
    for collection in df["listed_in"]:
        for theme in list(collection):
            theme = theme.strip()
            if theme in values:
                values[theme] += 1
            else:
                values[theme] = 1
    
    if (len(values) == 0):
        return None #only nan left
    
    ordered = [(key, val) for key, val in sorted(values.items(), key = lambda x: x[1], reverse = True)]
    p = ordered[0][1]/total
    return ( min(1-p, p), ordered[0][0], "listed_in")

def str2list(i):
    if type(i) is str:
        return [j.strip() for j in i.split(',')];
    else: # nan values
        return []

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

# funções de divisão
def del_type(i, df):
    return df[df["type"] != i]

def keep_type(i, df):
    return df[df["type"] == i]

def del_director(i, df):
    return df[df["director"].apply(lambda x: i not in x)]

def keep_director(i, df):
    return df[ df["director"].apply(lambda x: (i in x) or (x == []) ) ]

def del_cast(i, df):
    return df[df["cast"].apply(lambda x: i not in x)]

def keep_cast(i, df):
    return df[ df["cast"].apply(lambda x: (i in x) or (x == []) ) ]

def del_country(i, df):
    return df[df["country"] != i]

def keep_country(i, df):
    return df[ (df["country"].isnull()) | (df["country"] == i) ]

def del_smaller_equal_than_release_year(i, df):
    return df[df["release_year"] > i]

def del_greater_than_release_year(i, df):
    return df[df["release_year"] <= i]
def del_smaller_equal_than_rating(i, df):
    return df[ (df["rating"] > i) | (df["rating"].isnull()) ]

def del_greater_than_rating(i, df):
    return df[ (df["rating"] <= i) | (df["rating"].isnull()) ]

def del_smaller_equal_than_duration(i, df):
    return df[df["duration"] > i]

def del_greater_than_duration(i, df):
    return df[df["duration"] <= i]

def del_topic(i, df):
    return df[df["listed_in"].apply(lambda x: i not in x)]

def keep_topic(i, df):
    return df[ df["listed_in"].apply(lambda x: (i in x) or (x == []) ) ]

@app.route('/', methods=['POST'])
@cross_origin()
def get_game_state():
    response_json = request.get_json()
    
    df = pd.read_csv("datasets/amazon_prime_titles.csv")

    df = preprocess(df)
    
    for object in response_json["questions"]:

      if object["answer"] == "yes":
        if object["column"] == "type":
            df = keep_type(object["data"], df)
        elif object["column"] == "director":
            df = keep_director(object["data"], df)  
        elif object["column"] == "cast":
            df = keep_cast(object["data"], df)
        elif object["column"] == "country":
            df = keep_country(object["data"], df)
        elif object["column"] == "release_year":
            df = del_smaller_equal_than_release_year(object["data"], df)
        elif object["column"] == "rating":
            df = del_smaller_equal_than_rating(object["data"], df)
        elif object["column"] == "listed_in":
            df = keep_topic(object["data"], df)
        elif object["column"] == "duration":
            df = del_smaller_equal_than_duration(object["data"], df)
        
        # df = df.loc[df[object["column"]] == object["data"]]
      elif object["answer"] == "no":
        if object["answer"] == "type":
            df = del_type(object["data"], df)
        elif object["answer"] == "director":
            df = del_director(object["data"], df)
        elif object["answer"] == "cast":
            df = del_cast(object["data"], df)
        elif object["answer"] == "country":
            df = del_country(object["data"], df)
        elif object["answer"] == "release_year":
            df = del_greater_than_release_year(object["data"], df) 
        elif object["answer"] == "rating":
            df = del_greater_than_rating(object["data"], df)  
        elif object["answer"] == "listed_in":
            df = del_topic(object["data"], df)  
        elif object["answer"] == "duration":
            df = del_greater_than_duration(object["data"], df)
        
        # df = df.loc[df[object["column"]] != object["data"]]
    
    df = df.reset_index(drop=True)

    if len(df) == 0:
      response_json["guesses"].append(None)
      return response_json

    attributes = []
    
    attributes.append( get_type(df) )     
    attributes.append( get_director(df) )  
    attributes.append( get_cast(df) )
    attributes.append( get_country(df) )
    attributes.append( get_release_year(df) )
    attributes.append( get_rating(df) )
    attributes.append( get_topics(df) )
    attributes.append( get_duration(df) )

    attributes.sort(reverse = True)
    
    # print(attributes)

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

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=os.environ.get('PORT'))