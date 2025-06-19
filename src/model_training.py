import pandas as pd
import string
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# Data cleaning function
def clean_text(text):
    text = str(text).lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

# Load data
data = pd.read_csv(r"D:\Esewa project\sentiment-analysis-project\data\sentimentdataset.csv")
data.columns = data.columns.str.strip()
data = data.dropna(subset=['Text', 'Sentiment'])
data['Text'] = data['Text'].apply(clean_text)

X = data['Text']
y = data['Sentiment']

# Remove classes with only one sample
class_counts = y.value_counts()
valid_classes = class_counts[class_counts > 1].index
mask = y.isin(valid_classes)
X = X[mask]
y = y[mask]

print("Class distribution after filtering:\n", y.value_counts())

# Remove classes with fewer than 5 samples
min_samples = 5
class_counts = y.value_counts()
valid_classes = class_counts[class_counts >= min_samples].index
mask = y.isin(valid_classes)
X = X[mask]
y = y[mask]

print("Class distribution after filtering:\n", y.value_counts())

# Use a smaller test size
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=35, random_state=42, stratify=y
)

# Vectorize text
vectorizer = TfidfVectorizer(ngram_range=(1,2), min_df=2, max_df=0.95)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Model and hyperparameter tuning
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [None, 10, 20],
    'class_weight': ['balanced']
}
rf = RandomForestClassifier(random_state=42)
grid = GridSearchCV(rf, param_grid, cv=3, n_jobs=-1, verbose=1)
grid.fit(X_train_vec, y_train)

model = grid.best_estimator_

# Save model and vectorizer
os.makedirs(r'd:/Esewa project/sentiment-analysis-project/model', exist_ok=True)
joblib.dump(model, r'd:/Esewa project/sentiment-analysis-project/model/model.pkl')
joblib.dump(vectorizer, r'd:/Esewa project/sentiment-analysis-project/model/vectorizer.pkl')

# Evaluate
y_pred = model.predict(X_test_vec)
print("Training complete.")
print("Best parameters:", grid.best_params_)
print("Test accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))