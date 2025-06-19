import pandas as pd
from src.data_preprocessing import preprocess_data, clean_text, load_data


def test_clean_text():
    """Test text cleaning function"""
    text = "This is AMAZING!!! @user #hashtag http://example.com"
    cleaned = clean_text(text)

    assert isinstance(cleaned, str)
    assert len(cleaned) > 0
    assert "@user" not in cleaned
    assert "http://" not in cleaned
    assert cleaned.islower()


def test_load_data():
    """Test data loading"""
    # This assumes your test dataset exists
    df = load_data("data/sentimentdataset.csv")

    assert isinstance(df, pd.DataFrame)
    assert "Text" in df.columns
    assert "Sentiment" in df.columns
    assert len(df) > 0


def test_preprocess_data():
    """Test data preprocessing"""
    # Create sample data
    df = pd.DataFrame({
        "text": ["Good product!", "Bad service", "Okay experience"],
        "sentiment": ["positive", "negative", "neutral"],
    })

    processed = preprocess_data(df)

    assert "cleaned_text" in processed.columns
    assert len(processed) == len(df)