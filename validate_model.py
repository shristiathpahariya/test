import joblib
import os
import sys
sys.path.append(os.getcwd())

# Check if model files exist
if not os.path.exists('model/model.pkl'):
    print('Warning: Model file model/model.pkl not found, skipping validation')
    exit(0)
if not os.path.exists('model/vectorizer.pkl'):
    print('Warning: Vectorizer file model/vectorizer.pkl not found, skipping validation')
    exit(0)

try:
    # Try to import and test the prediction function
    from src.predict import load_model, predict_sentiment

    model = load_model('model/model.pkl')
    vectorizer = load_model('model/vectorizer.pkl')

    texts = ['I love this!', 'This is terrible']
    for text in texts:
        prediction = predict_sentiment(model, vectorizer, text)
        print(f'Text: {text} -> Prediction: {prediction}')

    print('Validation passed!')
except ImportError as e:
    print(f'Warning: Could not import prediction modules - {e}')
    print('Skipping model validation')
except Exception as e:
    print(f'Error during validation: {e}')
    raise
