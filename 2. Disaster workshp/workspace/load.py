import joblib
import re
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.base import BaseEstimator,TransformerMixin
from sklearn.tree import DecisionTreeClassifier
 
import pandas as pd


# define a function to tokenize and clean the feature
def tokenize(text):
    url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    detected_urls = re.findall(url_regex, text)
    for url in detected_urls:
        text = text.replace(url, "urlplaceholder")
 
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
 
    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)
 
    return clean_tokens
 
# Build a custom transformer which will extract the starting verb of a sentence
class toarray(BaseEstimator, TransformerMixin):
 
    # Given it is a tranformer we can return the self
    def fit(self, X, y=None):
        return self
 
    def transform(self, X):
        return pd.DataFrame(X.toarray())
 
class length(BaseEstimator, TransformerMixin):
 
    # Given it is a tranformer we can return the self
    def fit(self, X, y=None):
        return self
 
    def transform(self, X):
 
        return pd.DataFrame([len(txt) for txt in X])


model = joblib.load('ML_Model')

model






