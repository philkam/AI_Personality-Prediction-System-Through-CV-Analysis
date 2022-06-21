import pickle
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import contractions
import re
from nltk.tokenize import word_tokenize
import pandas as pd
import snscrape.modules.twitter as sntwitter

# Using TwitterSearchScraper to scrape data and append tweets to list
def get_tweets(username):
    tweets = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'from:{username}').get_items()):
        tweets.append(tweet.content)
        if i == 50: break
    return tweets

def load_files():
    try:
        with open("saved-models/RandomForest_E-I.sav", "rb") as file:
            ei_classifier = pickle.load(file)
        with  open("saved-models/RandomForest_N-S.sav", "rb") as file:
            ns_classifier = pickle.load(file)
        with open("saved-models/SVM_F-T.sav", "rb") as file:
            ft_classifier = pickle.load(file)
        with  open("saved-models/Xgboost_J-P.sav", "rb") as file:
            jp_classifier = pickle.load(file)
    except FileNotFoundError:
        print("Model not found!")

    try:
        with open("vectorizer/vectorizer.pkl", "rb") as file:
            vectorizer = pickle.load(file)
    except FileNotFoundError:
        print("Tokenizer not found!")

    return ei_classifier, ns_classifier, ft_classifier, jp_classifier, vectorizer
    
def preprocessing(text):
    stopword_list = stopwords.words("english")
    lemmatizer = WordNetLemmatizer()
    
    text = contractions.fix(text)
    text = text.lower()
    text = re.sub(r'@([a-zA-Z0-9_]{1,50})', '', text)
    text = re.sub(r'#([a-zA-Z0-9_]{1,50})', '', text)
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'[^A-Za-z0-9]+', ' ', text)
    text = re.sub(r' +', ' ', text)
    text = " ".join([word for word in text.split() if not len(word) <3])
    text = word_tokenize(text)
    text = [word for word in text if not word in stopword_list]
    text = [lemmatizer.lemmatize(word) for word in text]
    text = " ".join(text)
    return text

def get_prediction(username):
    ei_classifier, ns_classifier, ft_classifier, jp_classifier, vectorizer = load_files()
    tweets = get_tweets(username)
    text   = " ".join(tweets)
    text   = preprocessing(text)
    text   = vectorizer.transform([text])
    
    prediction = ""
    e_or_i = "E" if ei_classifier.predict(text)[0] == 1 else "I"
    n_or_s = "N" if ns_classifier.predict(text)[0] == 1 else "S"
    f_or_t = "F" if ft_classifier.predict(text)[0] == 1 else "T"
    j_or_p = "J" if jp_classifier.predict(text)[0] == 1 else "P"
    prediction = e_or_i + n_or_s + f_or_t + j_or_p

    return prediction, tweets