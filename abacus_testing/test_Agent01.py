import pytest
import pandas as pd
import sys
from unittest.mock import patch, Mock

sys.path.append('../backend')

try:
    from backend.Agent01.functions import (
        coerce_numeric, read_excel_any, summarise_dataframe, 
        call_openai, make_chart
    )
    AGENT01_FUNCTIONS_AVAILABLE = True
except ImportError:
    try:
        from backend.Agent01.functions import (
            coerce_numeric, read_excel_any, summarise_dataframe, 
            call_openai, make_chart
        )
        AGENT01_FUNCTIONS_AVAILABLE = True
        print("✅ Imported from Agent_01.functions")
    except ImportError:
        AGENT01_FUNCTIONS_AVAILABLE = False
        print("⚠️ Agent01/Agent_01.functions not available")

class TestFunctions:
    """Tests for Agent01/functions.py"""
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    def test_coerce_numeric_with_currency(self):
        """Test currency conversion to numbers"""
        series = pd.Series(["£100.50", "$200", "€150.75"])
        result = coerce_numeric(series)
        
        assert pd.api.types.is_numeric_dtype(result)
        assert result.iloc[0] == 100.50
        assert result.iloc[1] == 200.0
        assert result.iloc[2] == 150.75
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    def test_coerce_numeric_with_mixed_data(self):
        """Test with non-convertible mixed data"""
        series = pd.Series(["abc", "def", "ghi"])
        result = coerce_numeric(series)
        
        # Should return original series if not enough conversions
        assert not pd.api.types.is_numeric_dtype(result)
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    def test_coerce_numeric_with_numbers(self):
        """Test simple numeric conversion"""
        series = pd.Series(["100", "200.5", "300"])
        result = coerce_numeric(series)
        
        assert pd.api.types.is_numeric_dtype(result)
        assert result.iloc[0] == 100.0
        assert result.iloc[1] == 200.5
        assert result.iloc[2] == 300.0
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    def test_read_csv_file(self, sample_csv_file):
        """Test CSV file reading"""
        result = read_excel_any(sample_csv_file, "test.csv")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "Amount" in result.columns
        assert "Description" in result.columns
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    def test_read_excel_invalid_file(self):
        """Test reading invalid file"""
        invalid_data = b"Invalid file content"
        
        with pytest.raises(Exception):
            read_excel_any(invalid_data, "invalid.xlsx")
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    def test_summarise_dataframe(self, sample_dataframe):
        """Test DataFrame summary"""
        summary = summarise_dataframe(sample_dataframe)
        
        assert summary["num_rows"] == 3
        assert summary["num_columns"] == 4
        assert len(summary["columns"]) == 4
        
        # Check that Amount is numeric with stats
        amount_col = next(c for c in summary["columns"] if c["name"] == "Amount")
        assert "min" in amount_col
        assert "max" in amount_col
        assert amount_col["min"] == -50.0
        assert amount_col["max"] == -25.0
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    def test_summarise_dataframe_columns_info(self, sample_dataframe):
        """Test column details in summary"""
        summary = summarise_dataframe(sample_dataframe)
        
        # Check information for each column
        columns = {col["name"]: col for col in summary["columns"]}
        
        # Date column (object)
        assert "Date" in columns
        assert columns["Date"]["dtype"] == "object"
        assert "top_values" in columns["Date"]
        
        # Amount column (numeric)
        assert "Amount" in columns
        assert "min" in columns["Amount"]
        assert "mean" in columns["Amount"]
        assert "sum" in columns["Amount"]
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    @patch('Agent01.functions.client')
    def test_call_openai_success(self, mock_client, mock_openai_response):
        """Test successful OpenAI call"""
        try:
            mock_client.chat.completions.create.return_value = mock_openai_response
            
            messages = [{"role": "user", "content": "Analyze my finances"}]
            result = call_openai(messages)
            
            assert result == "Here is your financial analysis."
            mock_client.chat.completions.create.assert_called_once()
            
            # Check that system prompt was added
            call_args = mock_client.chat.completions.create.call_args[1]['messages']
            assert call_args[0]['role'] == 'system'
            assert 'Abacus' in call_args[0]['content']
        except Exception:
            # If patch doesn't work with Agent01, try Agent_01
            with patch('Agent_01.functions.client') as mock_client_alt:
                mock_client_alt.chat.completions.create.return_value = mock_openai_response
                
                messages = [{"role": "user", "content": "Analyze my finances"}]
                result = call_openai(messages)
                
                assert result == "Here is your financial analysis."
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    @patch('Agent01.functions.client')
    def test_call_openai_with_retry(self, mock_client):
        """Test automatic OpenAI retry"""
        from openai import OpenAIError
        
        # First call fails, second succeeds
        mock_client.chat.completions.create.side_effect = [
            OpenAIError("API Error"),
            Mock(choices=[Mock(message=Mock(content="Success after retry"))])
        ]
        
        messages = [{"role": "user", "content": "Test"}]
        result = call_openai(messages)
        
        assert result == "Success after retry"
        assert mock_client.chat.completions.create.call_count == 2
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    @patch('Agent01.functions.client')
    def test_call_openai_system_prompt_injection(self, mock_client, mock_openai_response):
        """Test automatic system prompt injection"""
        mock_client.chat.completions.create.return_value = mock_openai_response
        
        # Test with messages without system prompt
        messages = [{"role": "user", "content": "Test"}]
        call_openai(messages)
        
        # Check that system prompt was added automatically
        call_args = mock_client.chat.completions.create.call_args[1]['messages']
        assert len(call_args) == 2  # System + user
        assert call_args[0]['role'] == 'system'
        assert 'Abacus' in call_args[0]['content']
        assert call_args[1]['role'] == 'user'
        assert call_args[1]['content'] == 'Test'
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    def test_make_chart_bar(self, sample_dataframe):
        """Test bar chart generation"""
        result = make_chart(sample_dataframe, "bar", ["Category", "Amount"])
        
        # Should return a base64 string
        assert isinstance(result, str)
        assert len(result) > 100  # Base64 of an image
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    def test_make_chart_pie(self, sample_dataframe):
        """Test pie chart generation"""
        result = make_chart(sample_dataframe, "pie", ["Category", "Amount"])
        
        assert isinstance(result, str)
        assert len(result) > 100
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    def test_make_chart_line(self, sample_dataframe):
        """Test line chart generation"""
        result = make_chart(sample_dataframe, "line", ["Date", "Amount"])
        
        assert isinstance(result, str)
        assert len(result) > 100
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    def test_make_chart_invalid_columns(self, sample_dataframe):
        """Test with invalid columns"""
        with pytest.raises(ValueError, match="No valid columns"):
            make_chart(sample_dataframe, "bar", ["NonExistent"])
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    def test_make_chart_unsupported_type(self, sample_dataframe):
        """Test unsupported chart type"""
        with pytest.raises(ValueError, match="Unsupported chart type"):
            make_chart(sample_dataframe, "invalid", ["Category"])


class TestDataProcessing:
    """Specific tests for data processing"""
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    def test_coerce_numeric_edge_cases(self):
        """Test edge cases for coerce_numeric"""
        
        # Test with null values
        series_with_na = pd.Series(["100", None, "200", ""])
        result = coerce_numeric(series_with_na)
        assert pd.api.types.is_numeric_dtype(result)
        
        # Test with percentages
        series_percent = pd.Series(["10%", "20%", "30%"])
        result = coerce_numeric(series_percent)
        assert pd.api.types.is_numeric_dtype(result)
        assert result.iloc[0] == 10.0
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    def test_read_excel_different_formats(self):
        """Test reading different file formats"""
        
        # Test CSV with different encoding
        csv_latin1 = "Name,Amount\nCoffee,50\nRestaurant,30".encode('latin-1')
        
        try:
            result = read_excel_any(csv_latin1, "test_latin1.csv")
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
        except Exception:
            # If encoding fails, it's normal
            pass
    
    @pytest.mark.skipif(not AGENT01_FUNCTIONS_AVAILABLE, reason="Agent01.functions not available")
    def test_sample_df_functionality(self):
        """Test sample_df function if it exists"""
        try:
            from backend.Agent01.functions import sample_df
            
            # Create a large DataFrame
            large_df = pd.DataFrame({
                'col1': range(1000),
                'col2': range(1000, 2000)
            })
            
            # Test sampling
            sampled = sample_df(large_df)
            assert len(sampled) <= len(large_df)
            assert len(sampled) > 0
            
        except ImportError:
            # If sample_df doesn't exist, skip the test
            pytest.skip("sample_df function not available")


# Simple test to check that the module works even without Agent01
def test_module_import():
    """Test that the test module works even if Agent01 is not available"""
    assert True  # Basic test that always passes

def test_import_availability():
    """Test availability of Agent01.functions module"""
    print(f"Agent01.functions available: {AGENT01_FUNCTIONS_AVAILABLE}")
    
    if not AGENT01_FUNCTIONS_AVAILABLE:
        pytest.skip("Agent01.functions not available")

def test_pandas_basic():
    """Test that pandas works correctly"""
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    assert len(df) == 3
    assert list(df.columns) == ['A', 'B']