import pytest
import pandas as pd
import io
import json
from pathlib import Path
import tempfile
import os
import sys
from unittest.mock import Mock, patch, AsyncMock

sys.path.append('../backend')

try:
    from fastapi.testclient import TestClient
    from backend.main import app
    MAIN_APP_AVAILABLE = True
except ImportError:
    try:
        sys.path.append('..')
        from backend.main import app
        from fastapi.testclient import TestClient
        MAIN_APP_AVAILABLE = True
    except ImportError:
        MAIN_APP_AVAILABLE = False
        print("⚠️ Main app not available for testing")

@pytest.fixture
def client():
    """FastAPI test client"""
    if not MAIN_APP_AVAILABLE:
        pytest.skip("Main app not available")
    return TestClient(app)

@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for testing"""
    return pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Transaction': ['Grocery Store', 'Fuel Station', 'Restaurant'],
        'Amount': [-50.00, -30.00, -25.00],
        'Category': ['Groceries', 'Transport', 'Dining']
    })

@pytest.fixture
def sample_csv_file():
    """Sample CSV file in bytes"""
    csv_content = "Date,Amount,Description\n2024-01-01,100,Income\n2024-01-02,-50,Grocery"
    return csv_content.encode('utf-8')

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI responses"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Here is your financial analysis."
    return mock_response

@pytest.fixture
def mock_yfinance_stock():
    """Mock yfinance data - MISSING FIXTURE ADDED"""
    mock_stock = Mock()
    mock_stock.info = {
        'symbol': 'AAPL',
        'shortName': 'Apple Inc.',
        'regularMarketPrice': 150.25,
        'currency': 'USD',
        'marketCap': 2500000000000,
        'sector': 'Technology',
        'trailingPE': 25.5,
        'fiftyTwoWeekLow': 120.00,
        'fiftyTwoWeekHigh': 180.00
    }
    return mock_stock

@pytest.fixture
def temp_documents_folder():
    """Temporary folder for Islamic documents"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test documents
        (temp_path / "halal_guide.txt").write_text(
            "Investment in technology companies is generally halal if they avoid haram activities like gambling and alcohol. "
            "Shariah-compliant investments must avoid riba (interest), gharar (excessive uncertainty), and haram sectors."
        )
        
        (temp_path / "banking_rules.txt").write_text(
            "Conventional banking with interest is strictly haram in Islam. "
            "Islamic banking alternatives include murabaha, ijara, and musharaka financing."
        )
        
        yield temp_path

@pytest.fixture
def mock_islamic_config():
    """Mock configuration for Agent03"""
    config_mock = Mock()
    config_mock.OPENAI_API_KEY = "test-key-123"
    config_mock.MODEL_NAME = "gpt-4o"
    config_mock.EMBEDDING_MODEL = "text-embedding-3-small"
    config_mock.CHUNK_SIZE = 1000
    config_mock.DOCUMENTS_FOLDER = Path("test_docs")
    config_mock.VECTOR_DB_PATH = Path("test_vector")
    config_mock.HALAL_KEYWORDS = ["halal", "permissible", "islamic", "shariah", "compliant"]
    config_mock.HARAM_KEYWORDS = ["haram", "forbidden", "interest", "gambling", "alcohol", "riba"]
    config_mock.QUESTIONABLE_KEYWORDS = ["mixed", "conventional", "uncertain", "doubtful"]
    return config_mock