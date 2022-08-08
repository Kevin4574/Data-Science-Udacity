# import libraries
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import sys





def load_data(messages_filepath, categories_filepath):
    '''load and merge message and categories csv file
    Args:
        messages_filepath, categories_filepath
    Returns:
        df: loaded and merged dataframe
    '''
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)

    # merge datasets
    df = pd.merge(messages,categories,on = 'id')

    return df


def clean_data(df):
    '''clean the dataframe
    Args:
        df: uncleaned dataframe
    Returns:
        df: cleaned dataframe
    '''
    # create a dataframe of the 36 individual category columns
    categories = df['categories'].str.split(pat = ';',expand = True)
    category_colnames = [col.split('-')[0] for col in categories.iloc[1].values]
    # rename the columns of `categories`
    categories.columns = category_colnames

    for column in category_colnames:
        # set each value to be the last character of the string
        categories[column] = categories[column].apply(lambda x:x.split('-')[1])

        # convert column from string to numeric
        categories[column] = categories[column].astype(int)

    # drop the original categories column from `df`
    df = df.drop(columns = 'categories')
    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df,categories],axis = 1)
    
    # replace all the 2 in related column with 1
    df['related']=df['related'].map(lambda x: 1 if x == 2 else x)

    return df


def save_data(df, database_filename):
    '''save the cleaned dataframe to sql server
    Args:
        df: input cleaned dataframe
    '''
    engine = create_engine('sqlite:///' + database_filename)
    df.to_sql('message',
              engine,
              index=False,
              if_exists='replace')


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)

        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)

        print('Cleaned data saved to database!')

    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
