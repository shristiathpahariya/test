import pytest
import joblib
import os
from src.predict import predict_sentiment, load_model


def test_model_prediction():
    """Test model prediction functionality"""
    if not os.path.exists("model/model.pkl"):
        pytest.skip("Model files not found")

    model = load_model("model/model.pkl")
    vectorizer = load_model("model/vectorizer.pkl")

    # Test positive sentiment
    positive_text = "I absolutely love this product!"
    prediction = predict_sentiment(model, vectorizer, positive_text)
    assert prediction is not None

    # Test negative sentiment
    negative_text = "This is terrible, worst experience ever"
    prediction = predict_sentiment(model, vectorizer, negative_text)
    assert prediction is not None


def test_model_files_exist():
    """Test that model files exist and are loadable"""
    if not os.path.exists("model/model.pkl"):
        pytest.skip("Model files not found")

    model = load_model("model/model.pkl")
    vectorizer = load_model("model/vectorizer.pkl")

    assert model is not None
    assert vectorizer is not None


def test_model_training_functions():
    """Test model training utility functions"""
    from src.model_training import clean_text

    # Test text cleaning
    dirty_text = "Hello World!!! @user #hashtag"
    cleaned = clean_text(dirty_text)

    assert isinstance(cleaned, str)
    assert cleaned.islower()
    assert "!" not in cleaned  # Punctuation should be removed