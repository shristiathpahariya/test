import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

def load_model(model_path):
    model = joblib.load(model_path)
    return model

def preprocess_input(text, vectorizer):
    text_transformed = vectorizer.transform([text])
    return text_transformed

def predict_sentiment(model, vectorizer, text):
    processed_text = preprocess_input(text, vectorizer)
    prediction = model.predict(processed_text)
    return prediction[0]

def load_data(file_path):
    data = pd.read_csv(r"D:\Esewa project\sentiment-analysis-project\data\sentimentdataset.csv")
    X = data['Text']      # Use your actual text column name
    y = data['Sentiment']     # Use your actual label column name
    return X, y

if __name__ == "__main__":
    model_path = r'd:/Esewa project/sentiment-analysis-project/model/model.pkl'  # Update with the actual model path
    vectorizer_path = r'd:/Esewa project/sentiment-analysis-project/model/vectorizer.pkl'  # Update with the actual vectorizer path

    model = load_model(model_path)
    vectorizer = load_model(vectorizer_path)

    X, y = load_data('d:/Esewa project/sentiment-analysis-project/data/dataset.csv')

    sample_text = "Your input text for sentiment analysis."
    sentiment = predict_sentiment(model, vectorizer, sample_text)
    print(f"The predicted sentiment is: {sentiment}")