import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer

def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

def clean_text(text):
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    return text

def preprocess_data(data):
    data['cleaned_text'] = data['text'].apply(clean_text)
    return data

def split_data(data, test_size=0.2, random_state=42):
    X = data['cleaned_text']
    y = data['label']
    return train_test_split(X, y, test_size=test_size, random_state=random_state)

def vectorize_data(X_train, X_test):
    vectorizer = CountVectorizer()
    X_train_vectorized = vectorizer.fit_transform(X_train)
    X_test_vectorized = vectorizer.transform(X_test)
    return X_train_vectorized, X_test_vectorized, vectorizer