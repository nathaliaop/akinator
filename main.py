from flask import Flask, request
import pandas as pd
import numpy as np
from flask_cors import cross_origin
import os

app = Flask(__name__)

def get_release_year(df):
    if df["release_year"].isnull().all():
        return None
    total = len(df["release_year"])
    median = round( df["release_year"].sort_values().median() )
    left = right = 0
    for i in df[df["release_year"].notnull()]["release_year"]:
        if i <= median:
            left += 1
        else:
            right += 1
    return (min(left/total, right/total), median, "release_year")

def get_rating(df):
    if df["rating"].isnull().all():
        return None
    total = len(df["rating"])
    median = round( df["rating"].sort_values().median() )
    left = right = 0
    for i in df[df["rating"].notnull()]["rating"]:
        if i <= median:
            left += 1
        else:
            right += 1
    return (min(left/total, right/total), median, "rating")

def get_country(df):
    if df["country"].isnull().all():
        return None
    total = len(df["country"])
    countries = df["country"].value_counts().div(total)
    return (min(1 - countries[0], countries[0]), countries.index[0], "country")

def get_type(df):
    if df["type"].isnull().all():
        return None
    total = len(df["type"])
    types = df["type"].value_counts().div(total)
    return (min(1 - types[0], types[0]), types.index[0], "type")

def get_director(df):
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
    return (min(1-p, p), ordered[0][0], "director")

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
    return (min(1-p, p), ordered[0][0], "cast")

def get_duration(df):
    if df["duration"].isnull().all():
        return None
    if df["type"].nunique() > 1:
        return None
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
    if df["listed_in"].isnull().all():
        return None
    total = len(df["listed_in"]) 
    values = {}
    for collection in df["listed_in"]:
        for theme in list(collection):
            theme = theme.strip()
            if theme in values:
                values[theme] += 1
            else:
                values[theme] = 1
    ordered = [(key, val) for key, val in sorted(values.items(), key = lambda x: x[1], reverse = True)]
    p = ordered[0][1]/total
    return (min(1-p, p), ordered[0][0], "listed_in")

def preprocess(df):
    if "date_added" in df:
        del df["date_added"]
    if "show_id" in df:
        del df["show_id"]
    def str2list(i):
        if i.isinstance(str):
            return [j.strip() for j in i.split(',')]
        return [] # nan values
    def str2int(i):
        return int((i.split())[0])
    df["listed_in"] = df["listed_in"].apply( str2list )
    df["director"] = df["director"].apply( str2list )
    df["cast"] = df["cast"].apply( str2list )
    df["duration"] = df["duration"].apply( str2int )
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
    df["rating"] = df["rating"].apply( mergeRating )
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

def keep_category(df, object):
    return df.loc[(df[object["column"]] == object["data"]) | (df[object["column"]].isnull())]

def del_category(df, object):
    return df.loc[df[object["column"]] != object["data"]]

def keep_category_list(df, object):
    return df[df[object["column"]].apply(lambda x: (object["data"] in x) or (x == []))]

def del_category_list(df, object):
    return df[df[object["column"]].apply(lambda x: object["data"] not in x)]

def keep_greater_than(df, object):
    return df[ (df[object["column"]] > object["data"]) | (df[object["column"]].isnull()) ]

def del_greater_than(df, object):
    return df[ (df[object["column"]] <= object["data"]) | (df[object["column"]].isnull()) ]


@app.route('/', methods=['POST'])
@cross_origin()
def hello_world():
    response_json = request.get_json()

    df = pd.read_csv("datasets/amazon_prime_titles.csv")

    df = preprocess(df)

    # dividing the dataframe
    for object in response_json["questions"]:

        if object["column"] in ["type", "country"]:
            if object["answer"] == "yes":
                df = keep_category(df, object)
            elif object["answer"] == "no":
                df = del_category(df, object)
        elif object["column"] in ["director", "cast", "listed_in"]:
            if object["answer"] == "yes":
                df = keep_category_list(df, object)
            elif object["answer"] == "no":
                df = del_category_list(df, object)
        elif object["column"] in ["release_year", "rating", "duration"]:
            if object["answer"] == "yes":
                df = keep_greater_than(df, object)
            elif object["answer"] == "no":
                df = del_greater_than(df, object)

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

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=os.environ.get('PORT'))