# import libraries
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import sqlite3
import re
import time
import joblib
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import fbeta_score, make_scorer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, AdaBoostClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.base import BaseEstimator,TransformerMixin
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import *
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
import sys

path = r'D:\金融股票\Udacity\Data Science\3. Data Engineering\5. Project - Disaster Response Pipeline\data\ETL_Cleaned.db'

def load_data(database_filepath):
    '''load data and return X,Y and category
    Args:
        database
    Returns:
        X, Y , category
    '''
    engine = create_engine('sqlite:///' + database_filepath)
    df = pd.read_sql_table('message',engine)

    # define x and y variable
    feature = df['message']
    label =  df.iloc[:,4:]

    X,Y,category_names = feature,label,label.columns.values

    return X,Y,category_names

def tokenize(text):
    '''clean text and return cleaned tokens

    Args:
        text: original input text

    Returns:
        tokens/words: cleaned token after remove URL and lemmatization
    '''
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
    '''convert data to array

    Args:
        X: data

    Returns:
        output: array format data

    '''
    # Given it is a tranformer we can return the self
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return pd.DataFrame(X.toarray())

class length(BaseEstimator, TransformerMixin):
    '''return the length of the data

    Args:
        X: data

    Returns:
        output: the length of the data

    '''
    # Given it is a tranformer we can return the self
    def fit(self, X, y=None):
        return self

    def transform(self, X):

        return pd.DataFrame([len(txt) for txt in X])

def build_model():
    '''build model for disaster prediction
    Returns:
        predictive model
    '''
    # define a pipeline
    pipeline4 = Pipeline([
        ('features', FeatureUnion([

            ('text_pipeline', Pipeline([
                ('vectorizer', CountVectorizer(tokenizer=tokenize)),
                ('toa',toarray()),
                ('tfidf', TfidfTransformer())
            ])),

            ('get_len', length())
        ])),

        ('classifier', MultiOutputClassifier(DecisionTreeClassifier()))
    ])

    # define the parameter for pipeline in gridsearchCV
    param4 = {}
    param4['classifier__estimator__max_depth'] = [5,10,25,None]
    param4['classifier__estimator__min_samples_split'] = [2,5,10]
    param4['classifier__estimator__class_weight'] = [None, {0:1,1:5}, {0:1,1:10}, {0:1,1:25}]

    # gridsearch to output best model
    start = time.time()
    cv = GridSearchCV(pipeline4,param4,cv = 5,n_jobs = -1)

    return cv

def evaluate_model(model, X_test, Y_test, category_names):
    '''print out model evaluation
    Args:
        model , label and features
    Returns:
        model evaluation output
    '''
    # print out prediction using feature_test
    print('Prediction of label:')
    label_predCV = model.predict(X_test)
    print(label_predCV)

    # print out accuary
    print('Accuary/score',accuracy_score(label_predCV,Y_test))
    print('Accuary/score',model.score(X_test,Y_test))

    # Print classification report on test data
    print(classification_report(Y_test.values,
                                label_predCV,
                                target_names=category_names))

def save_model(model, model_filepath):
    '''save the final model
    Args:
        model you build above
    '''
    # save the mode
    joblib.dump(model, model_filepath)

def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        feature_train, feature_test, label_train, label_test = train_test_split(X, Y, test_size=0.999)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        start = time.time()
        model.fit(feature_train, label_train)
        print(f'time per train:{(time.time() - start)/3:.3f} second')
        
        print('Evaluating model...')
        evaluate_model(model, feature_test, label_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')

if __name__ == '__main__':
    main()