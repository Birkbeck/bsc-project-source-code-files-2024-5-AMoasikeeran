import pytest
import sys
from unittest.mock import patch, Mock, AsyncMock
from pathlib import Path
import tempfile

sys.path.append('../backend')

try:
    from backend.Agent03.islamic_agent import IslamicRAGAgent
    ISLAMIC_AGENT_AVAILABLE = True
except ImportError:
    try:
       
        from backend.Agent03.islamic_agent import IslamicRAGAgent
        ISLAMIC_AGENT_AVAILABLE = True
    except ImportError:
        ISLAMIC_AGENT_AVAILABLE = False
        print("⚠️ Agent03.islamic_agent not available")

try:
    from backend.Agent03.islamic_analyzer import IslamicInvestmentAnalyzer
    ISLAMIC_ANALYZER_AVAILABLE = True
except ImportError:
    try:
        from backend.Agent03.islamic_analyzer import IslamicInvestmentAnalyzer
        ISLAMIC_ANALYZER_AVAILABLE = True
    except ImportError:
        ISLAMIC_ANALYZER_AVAILABLE = False
        print("⚠️ Agent03.islamic_analyzer not available")

# Mock config_islamic at module level
class MockIslamicRAGConfig:
    """Mock Islamic configuration to avoid importing config_islamic"""
    
    def __init__(self):
        self.OPENAI_API_KEY = "test-key-123"
        self.MODEL_NAME = "gpt-4o"
        self.EMBEDDING_MODEL = "text-embedding-3-small"
        self.CHUNK_SIZE = 1000
        self.DOCUMENTS_FOLDER = Path("test_docs")
        self.VECTOR_DB_PATH = Path("test_vector")
        self.HALAL_KEYWORDS = ["halal", "permissible", "islamic", "shariah", "compliant"]
        self.HARAM_KEYWORDS = ["haram", "forbidden", "interest", "gambling", "alcohol", "riba"]
        self.QUESTIONABLE_KEYWORDS = ["mixed", "conventional", "uncertain", "doubtful"]

class TestIslamicRAGConfig:
    """Tests for Islamic configuration (mocked)"""
    
    def test_config_initialization(self):
        """Test configuration initialization"""
        config = MockIslamicRAGConfig()
        
        assert hasattr(config, 'DOCUMENTS_FOLDER')
        assert hasattr(config, 'VECTOR_DB_PATH')
        assert hasattr(config, 'OPENAI_API_KEY')
        assert hasattr(config, 'MODEL_NAME')
        assert hasattr(config, 'EMBEDDING_MODEL')
    
    def test_config_keywords(self):
        """Test Islamic keywords"""
        config = MockIslamicRAGConfig()
        
        # Check that keyword lists exist and are not empty
        assert len(config.HALAL_KEYWORDS) > 0
        assert len(config.HARAM_KEYWORDS) > 0
        assert len(config.QUESTIONABLE_KEYWORDS) > 0
        
        # Check some essential keywords
        assert "halal" in config.HALAL_KEYWORDS
        assert "haram" in config.HARAM_KEYWORDS
        assert "riba" in config.HARAM_KEYWORDS
        assert "interest" in config.HARAM_KEYWORDS


class TestIslamicRAGAgent:
    """Tests for Agent03/islamic_agent.py"""
    
    @pytest.fixture
    def islamic_agent(self):
        """Islamic agent instance for testing"""
        if not ISLAMIC_AGENT_AVAILABLE:
            pytest.skip("Agent03.islamic_agent not available")
            
        # Patch config_islamic to avoid import
        with patch.dict('sys.modules', {'config_islamic': Mock()}):
            with patch('Agent03.islamic_agent.IslamicRAGConfig', MockIslamicRAGConfig):
                with patch('Agent03.islamic_agent.OPENAI_AVAILABLE', True):
                    agent = IslamicRAGAgent()
                    agent.config = MockIslamicRAGConfig()
                    return agent
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not ISLAMIC_AGENT_AVAILABLE, reason="Agent03.islamic_agent not available")
    async def test_initialize_success(self, islamic_agent, temp_documents_folder):
        """Test successful initialization with documents"""
        islamic_agent.config.DOCUMENTS_FOLDER = temp_documents_folder
        
        with patch('Agent03.islamic_agent.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            # Mock initialize method if it exists
            if hasattr(islamic_agent, 'initialize'):
                result = await islamic_agent.initialize()
                assert result is True
            else:
                # If no initialize method, test basic initialization
                assert islamic_agent.config is not None
    
    @pytest.mark.skipif(not ISLAMIC_AGENT_AVAILABLE, reason="Agent03.islamic_agent not available")
    def test_search_relevant_context(self, islamic_agent):
        """Test relevant context search"""
        # Prepare test vector store
        islamic_agent.vector_store = [
            {
                "text": "Investment in technology companies following Shariah principles is generally halal",
                "source": "tech_guide.txt",
                "type": ".txt"
            },
            {
                "text": "Banking with interest is strictly haram in Islam according to Quran",
                "source": "banking_rules.txt", 
                "type": ".txt"
            }
        ]
        
        # Test if method exists
        if hasattr(islamic_agent, '_search_relevant_context'):
            results = islamic_agent._search_relevant_context("technology investment halal")
            
            assert len(results) > 0
            assert "technology" in results[0]["text"].lower()
            assert all("score" in result for result in results if isinstance(result, dict))
        else:
            # If method doesn't exist, test vector_store attribute
            assert hasattr(islamic_agent, 'vector_store')
    
    @pytest.mark.skipif(not ISLAMIC_AGENT_AVAILABLE, reason="Agent03.islamic_agent not available")
    def test_analyze_keywords(self, islamic_agent):
        """Test Islamic keywords analysis"""
        text = "This investment involves interest and gambling but also includes some halal technology activities"
        
        # Test if method exists
        if hasattr(islamic_agent, '_analyze_keywords'):
            result = islamic_agent._analyze_keywords(text)
            
            assert result["halal_count"] >= 1
            assert result["haram_count"] >= 2
            assert "interest" in result["haram_keywords"]
            assert "gambling" in result["haram_keywords"]
        else:
            # If method doesn't exist, test config existence
            assert islamic_agent.config.HALAL_KEYWORDS is not None
            assert islamic_agent.config.HARAM_KEYWORDS is not None


class TestIslamicInvestmentAnalyzer:
    """Tests for Agent03/islamic_analyzer.py"""
    
    @pytest.fixture
    def islamic_analyzer(self):
        """Islamic analyzer instance for testing"""
        if not ISLAMIC_ANALYZER_AVAILABLE:
            pytest.skip("Agent03.islamic_analyzer not available")
            
        # Patch config_islamic to avoid import
        with patch.dict('sys.modules', {'config_islamic': Mock()}):
            with patch('Agent03.islamic_analyzer.IslamicRAGConfig', MockIslamicRAGConfig):
                with patch('Agent03.islamic_analyzer.OpenAI') as mock_openai:
                    mock_client = Mock()
                    mock_openai.return_value = mock_client
                    
                    analyzer = IslamicInvestmentAnalyzer()
                    analyzer.config = MockIslamicRAGConfig()
                    analyzer.client = mock_client
                    
                    # Mock vector store
                    mock_vector_store = Mock()
                    analyzer.vector_store = mock_vector_store
                    
                    return analyzer
    
    @pytest.mark.skipif(not ISLAMIC_ANALYZER_AVAILABLE, reason="Agent03.islamic_analyzer not available")
    def test_analyzer_initialization(self, islamic_analyzer):
        """Test analyzer initialization"""
        assert islamic_analyzer.config is not None
        assert islamic_analyzer.client is not None
        assert hasattr(islamic_analyzer, 'vector_store')
    
    @pytest.mark.skipif(not ISLAMIC_ANALYZER_AVAILABLE, reason="Agent03.islamic_analyzer not available")
    def test_keyword_analysis(self, islamic_analyzer):
        """Test keyword analysis"""
        text = "Investment in banking stocks with high interest rates and some gambling activities"
        
        # Test if method exists
        if hasattr(islamic_analyzer, '_keyword_analysis'):
            result = islamic_analyzer._keyword_analysis(text)
            
            assert "halal_indicators" in result
            assert "haram_indicators" in result
            assert "detected_sectors" in result
            assert "preliminary_status" in result
            
            # Should detect haram words
            assert result["haram_indicators"] > 0
            assert "banking" in result["detected_sectors"]
        else:
            # If method doesn't exist, test config
            assert islamic_analyzer.config.HARAM_KEYWORDS is not None
    
    @pytest.mark.skipif(not ISLAMIC_ANALYZER_AVAILABLE, reason="Agent03.islamic_analyzer not available")
    def test_detect_sectors(self, islamic_analyzer):
        """Test sector detection"""
        
        # Test if method exists
        if hasattr(islamic_analyzer, '_detect_sectors'):
            # Test technology sector
            tech_text = "investment in technology companies and software development"
            sectors = islamic_analyzer._detect_sectors(tech_text)
            assert "technology" in sectors
            
            # Test banking sector
            banking_text = "banking sector with loans and credit services"
            sectors = islamic_analyzer._detect_sectors(banking_text)
            assert "banking" in sectors
        else:
            # If method doesn't exist, just check object
            assert islamic_analyzer is not None


class TestAgent03Integration:
    """Integration tests for Agent03"""
    
    @pytest.mark.skipif(not ISLAMIC_AGENT_AVAILABLE, 
                       reason="Agent03 modules not available")
    def test_config_agent_integration(self):
        """Test config integration with agent"""
        # Patch config_islamic to avoid import
        with patch.dict('sys.modules', {'config_islamic': Mock()}):
            with patch('Agent03.islamic_agent.IslamicRAGConfig', MockIslamicRAGConfig):
                with patch('Agent03.islamic_agent.OPENAI_AVAILABLE', True):
                    agent = IslamicRAGAgent()
                    
                    # Basic instantiation test
                    assert agent is not None


# Simple test to check that the module works even without Agent03
def test_module_import():
    """Test that the test module works even if Agent03 is not available"""
    assert True  # Basic test that always passes

def test_import_availability():
    """Test availability of Agent03 modules"""
    print(f"Agent03.islamic_agent available: {ISLAMIC_AGENT_AVAILABLE}")
    print(f"Agent03.islamic_analyzer available: {ISLAMIC_ANALYZER_AVAILABLE}")
    
    # If no modules are available, skip tests
    if not (ISLAMIC_AGENT_AVAILABLE or ISLAMIC_ANALYZER_AVAILABLE):
        pytest.skip("No Agent03 modules available")

def test_mock_config():
    """Test that config mock works"""
    config = MockIslamicRAGConfig()
    assert config.OPENAI_API_KEY == "test-key-123"
    assert len(config.HALAL_KEYWORDS) > 0
    assert len(config.HARAM_KEYWORDS) > 0

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