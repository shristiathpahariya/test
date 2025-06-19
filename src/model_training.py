import pandas as pd
import string
import os
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score


# Clean and normalize text
def clean_text(text):
    text = str(text).lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text


# Define paths (portable)
DATA_PATH = os.path.join("data", "sentimentdataset.csv")
MODEL_DIR = os.path.join("model")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")

# Load and prepare data
data = pd.read_csv(DATA_PATH)
data.columns = data.columns.str.strip()
data = data.dropna(subset=["Text", "Sentiment"])
data["Text"] = data["Text"].apply(clean_text)

X = data["Text"]
y = data["Sentiment"]

# Remove rare classes (fewer than 2 first, then fewer than 5)
class_counts = y.value_counts()
valid_classes = class_counts[class_counts > 1].index
mask = y.isin(valid_classes)
X, y = X[mask], y[mask]

print("Class distribution after filtering (1+ samples):\n", y.value_counts())

min_samples = 5
class_counts = y.value_counts()
valid_classes = class_counts[class_counts >= min_samples].index
mask = y.isin(valid_classes)
X, y = X[mask], y[mask]

print("Class distribution after filtering (5+ samples):\n", y.value_counts())

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=35, random_state=42, stratify=y
)

# Vectorize text using TF-IDF
vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.95)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Model + hyperparameter tuning
param_grid = {
    "n_estimators": [100, 200],
    "max_depth": [None, 10, 20],
    "class_weight": ["balanced"],
}
rf = RandomForestClassifier(random_state=42)
grid = GridSearchCV(rf, param_grid, cv=3, n_jobs=-1, verbose=1)
grid.fit(X_train_vec, y_train)

model = grid.best_estimator_

# Save model and vectorizer (portable directory)
os.makedirs(MODEL_DIR, exist_ok=True)
joblib.dump(model, MODEL_PATH)
joblib.dump(vectorizer, VECTORIZER_PATH)

# Evaluate performance
y_pred = model.predict(X_test_vec)
print("\nTraining complete.")
print("Best parameters:", grid.best_params_)
print("Test accuracy:", accuracy_score(y_test, y_pred))
print("Classification report:\n", classification_report(y_test, y_pred))
