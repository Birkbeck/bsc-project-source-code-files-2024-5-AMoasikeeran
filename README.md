<div align="center">

# 🤖 Abacus FinBot
## AI-Powered Multi-Agent Financial Platform

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45+-red.svg)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-orange.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7.svg)](https://render.com/)

</div>

<div align="center">

> **Revolutionary AI-powered financial platform featuring 3 specialized agents: FinBot Chat with advanced visualizations, Stock Analysis with GPT-4o, and Islamic Finance Expert with real-time internet research.**

</div>

## 🌟 Features

### 🎯 **Multi-Agent Architecture**
- **Agent01 - FinBot Chat**: Financial analysis with 12+ interactive chart types
- **Agent02 - Stock Analysis**: Real-time stock analysis powered by GPT-4o
- **Agent03 - Sharia Expert**: Islamic finance compliance with internet research

### 💡 **Key Innovations**
- 🗣️ **Chat-to-Chart**: Natural language to visualization generation
- 🕌 **First Islamic Expert Agent**: Real-time Sharia compliance screening
- 📊 **Smart Visualizations**: AI-powered chart type suggestions
- 🔍 **Internet Research**: Live data integration from multiple sources
- 📈 **Professional Analytics**: 20+ financial metrics and ratios

### 🎨 **Advanced UI/UX**
- 🎨 Modern gradient design with animations
- 📱 Fully responsive mobile-first interface
- ♿ WCAG AA accessibility compliance
- 🔐 Secure authentication with dual-hash system

## 🏗️ Architecture

```mermaid
graph TB
    A[Streamlit Frontend] --> B[FastAPI Backend]
    B --> C[Agent01 - FinBot Chat]
    B --> D[Agent02 - Stock Analysis]
    B --> E[Agent03 - Sharia Expert]
    
    C --> F[OpenAI GPT-4o]
    D --> F
    E --> F
    E --> G[Yahoo Finance API]
    E --> H[Web Search APIs]
    
    B --> I[SQLite Database]
    B --> J[Authentication System]
```

## 🚀 Quick Start & Installation Guide

### Prerequisites

- **Python 3.9+** installed on your system
- **Git** for cloning the repository
- **OpenAI API Key** (get one at [OpenAI Platform](https://platform.openai.com/))
- **Internet connection** for AI features and real-time data

### 📥 Step-by-Step Installation

#### 1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/abacus-finbot.git
cd abacus-finbot
```

#### 2. **Create Virtual Environment**
```bash
# Create virtual environment
python -m venv abacus_env

# Activate virtual environment
# On Windows:
abacus_env\Scripts\activate

# On macOS/Linux:
source abacus_env/bin/activate
```

#### 3. **Install Dependencies**
```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

#### 4. **Configure OpenAI API Key**

**Option A: Environment Variable (Recommended)**
```bash
# Create .env file in root directory
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

# Replace 'your_openai_api_key_here' with your actual API key
```

**Option B: Direct Configuration**
```bash
# Edit backend configuration file
nano backend/config.py

# Or using any text editor, update this line:
# OPENAI_API_KEY: str = "your_openai_api_key_here"
```

**Option C: System Environment Variable**
```bash
# On Windows (Command Prompt):
set OPENAI_API_KEY=your_openai_api_key_here

# On Windows (PowerShell):
$env:OPENAI_API_KEY="your_openai_api_key_here"

# On macOS/Linux:
export OPENAI_API_KEY="your_openai_api_key_here"
```

#### 5. **Start the Backend Server**
```bash
# Navigate to project root and start backend
python main.py

# You should see:
# ✅ Agent01 (Enhanced Chat FinBot) ready!
# ✅ Agent02 (Stock Analysis) ready!
# ✅ Agent03 (Sharia Expert) ready with research tools!
# 🚀 ENHANCED BANKING ANALYTICS PLATFORM READY!
```

#### 6. **Launch the Frontend** (New Terminal)
```bash
# Open a new terminal/command prompt
cd abacus-finbot

# Activate virtual environment again
# Windows:
abacus_env\Scripts\activate
# macOS/Linux:
source abacus_env/bin/activate

# Start Streamlit frontend
streamlit run UI_streamlit.py
```

#### 7. **Access the Application**
- **Frontend Interface**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health/all

### 🔑 Demo Accounts (Ready to Use)

| Email | Password | Role | Features |
|-------|----------|------|----------|
| `admin@finbot.com` | `admin123` | Administrator | Full access to all agents |
| `test@finbot.com` | `test123` | Standard User | Complete functionality |
| `demo@finbot.com` | `demo123` | Demo User | Limited features for testing |

### ⚙️ Configuration Options

#### **Backend Configuration (config.py)**
```python
class Settings(BaseSettings):
    # 🔑 REQUIRED: Your OpenAI API Key
    OPENAI_API_KEY: str = "your_openai_api_key_here"
    
    # 🤖 AI Model Selection
    MODEL_NAME: str = "gpt-4o"  # or "gpt-4", "gpt-3.5-turbo"
    
    # 📊 Data Processing Limits
    SAMPLE_MIN_ROWS: int = 200
    SAMPLE_MAX_ROWS: int = 400
    MAX_FILE_BYTES: int = 10 * 1024 * 1024  # 10MB
    
    # 🌐 Environment Settings
    ENVIRONMENT: str = "development"  # or "production"
    PORT: int = 8000
    
    # 🔐 Security Settings
    ALLOWED_ORIGINS: list[str] = ["*"]  # Restrict in production
```

#### **Frontend Configuration (UI_streamlit.py)**
```python
# Backend URL Configuration
BACKEND = "http://localhost:8000"  # Change for production

# Email Configuration (for password reset)
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email": "your_admin_email@gmail.com",
    "password": "your_app_password"  # Gmail app password
}
```

### 🛠️ Troubleshooting

#### **Common Issues & Solutions**

**1. OpenAI API Key Error**
```bash
# Error: "OpenAI API key not found"
# Solution: Verify your API key is correctly set
echo $OPENAI_API_KEY  # Should display your key
```

**2. Module Not Found Errors**
```bash
# Error: "ModuleNotFoundError: No module named 'xyz'"
# Solution: Ensure virtual environment is activated and dependencies installed
pip install -r requirements.txt
```

**3. Port Already in Use**
```bash
# Error: "Port 8000 is already in use"
# Solution: Change port in config.py or kill existing process
netstat -ano | findstr :8000  # Windows
lsof -ti:8000 | xargs kill -9  # macOS/Linux
```

**4. Streamlit Not Starting**
```bash
# Error: "streamlit: command not found"
# Solution: Ensure Streamlit is installed and virtual environment is active
pip install streamlit==1.45.1
```

**5. Database Connection Issues**
```bash
# Error: "SQLite database locked"
# Solution: Restart the backend server
python main.py
```

### 🔧 Development Setup

#### **For Contributors & Developers**
```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/abacus-finbot.git
cd abacus-finbot

# 3. Add upstream remote
git remote add upstream https://github.com/original_username/abacus-finbot.git

# 4. Create development environment
python -m venv dev_env
source dev_env/bin/activate  # or dev_env\Scripts\activate on Windows

# 5. Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# 6. Set up pre-commit hooks (optional)
pre-commit install
```

### 📱 Production Deployment

#### **Environment Variables for Production**
```bash
# Production environment variables
OPENAI_API_KEY=your_production_api_key
ENVIRONMENT=production
PORT=8000
DATABASE_URL=postgresql://user:pass@host:port/db  # If using PostgreSQL
ALLOWED_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

### 🧪 Verify Installation

#### **Quick Test Commands**
```bash
# Test backend health
curl http://localhost:8000/health/all

# Test authentication
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@finbot.com", "password": "test123"}'

# Test OpenAI connection (should return analysis)
curl -X POST "http://localhost:8000/stock/analyze-sync" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL"}'
```

### 📚 Next Steps

1. **Explore the Interface**: Login with demo accounts
2. **Upload Financial Data**: Test with sample Excel/CSV files
3. **Try Stock Analysis**: Analyze popular stocks (AAPL, MSFT, TSLA)
4. **Test Islamic Expert**: Ask about investment compliance
5. **Generate Charts**: Use natural language to create visualizations
6. **Read Documentation**: Visit http://localhost:8000/docs for API details

---

## 📁 Complete Project Structure with Assets

```
abacus-finbot/
├── 🎨 FRONTEND/
│   ├── UI_streamlit.py           # Main Streamlit app (1800+ lines)
│   ├── assets/
│   │   └── abacus_logo.jpeg     # Application logo
│   └── requirements.txt          # Frontend dependencies
│
├── 🔧 BACKEND/
│   ├── main.py                   # FastAPI entry point (400+ lines)
│   ├── routes.py                 # API routes (1000+ lines)
│   ├── config.py                 # Global configuration
│   ├── finbot_users.db          # SQLite database
│   │
│   ├── Agent01/                  # 📊 FinBot Chat & Visualization
│   │   └── functions.py         # Financial analysis engine (500+ lines)
│   │
│   ├── Agent02/                  # 📈 Stock Analysis
│   │   ├── direct_analysis.py   # GPT-4o analysis pipeline (300+ lines)
│   │   ├── tools.py            # Financial APIs (200+ lines)
│   │   └── output/             # Generated reports
│   │
│   ├── Agent03/                  # 🕌 Sharia Expert
│   │   └── sharia_expert_agent.py # Expert agent with research (600+ lines)
│   │
│   └── Database/                 # 🛢️ Data Layer
│       ├── database.py          # SQLAlchemy models (400+ lines)
│       └── auth.py             # Authentication (100+ lines)
│
├── 📋 requirements.txt           # Backend dependencies
├── 📄 README.md                 # This file
├── 📜 LICENSE                   # MIT License

## 🎯 Agent Capabilities

### 🤖 Agent01 - FinBot Chat & Visualizations

**Features:**
- 💬 Conversational financial analysis with GPT-4o
- 📊 12+ chart types: Bar, Pie, Line, Scatter, Histogram, Box, Violin, Heatmap, Area, Donut
- 📁 Multi-format file support: .xlsx, .xls, .csv, .xlsm, .ods
- 🎨 Dual-format charts: Interactive (Plotly) + Static (Matplotlib)
- 💰 Smart financial categorization (Groceries, Transport, Utilities, etc.)
- 🔄 Automatic currency conversion (GBP focus)

**API Endpoints:**
```bash
POST /chat                    # AI chat with visualization
POST /finbot/create-chart     # Interactive chart generation
POST /finbot/smart-visualization  # AI-powered chart suggestions
POST /upload                  # File upload and processing
GET  /finbot/chart-types      # Available chart types
```

### 📈 Agent02 - Stock Analysis

**Features:**
- 🤖 GPT-4o powered comprehensive stock analysis
- 📊 20+ financial metrics: P/E, ROE, EBITDA, Market Cap, etc.
- 📰 Real-time news integration via DuckDuckGo
- 💹 Yahoo Finance API for live data
- 📝 Automated markdown report generation
- ⚡ 6-step analysis pipeline (< 60 seconds)

**API Endpoints:**
```bash
POST /stock/analyze-sync      # Complete stock analysis
POST /stock/price            # Real-time stock price
POST /stock/info             # Company information
GET  /stock/health           # Service status
```

### 🕌 Agent03 - Sharia Expert (Unique Innovation)

**Features:**
- 🌐 **First Islamic Expert Agent with Internet Research**
- 🔍 Real-time Yahoo Finance + web search integration
- 🚫 Automated haram screening (alcohol, gambling, tobacco, etc.)
- 📊 Automatic Sharia ratio calculations (debt/market cap < 33%)
- 💡 Halal investment alternatives with research
- 🎯 Confidence scoring (HIGH/MEDIUM/LOW)
- 📰 Recent news impact analysis

**Verdict System:**
- ✅ **HALAL**: Sharia compliant investments
- ❌ **HARAM**: Prohibited investments  
- ⚠️ **QUESTIONABLE**: Requires further analysis

**API Endpoints:**
```bash
POST /islamic/expert-analyze      # Comprehensive Sharia analysis
POST /islamic/expert-alternatives # Halal investment alternatives
POST /islamic/research-company    # Deep company research
GET  /islamic/expert-status       # Agent capabilities
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.115.12
- **AI Engine**: OpenAI GPT-4o
- **Database**: SQLite + SQLAlchemy 1.4.41
- **Authentication**: bcrypt 4.1.2 + passlib
- **Data Processing**: pandas 2.2.3, numpy 2.2.6
- **Financial APIs**: yfinance, DuckDuckGo Search
- **Web Scraping**: BeautifulSoup4, requests

### Frontend
- **Framework**: Streamlit 1.45.1
- **Visualization**: Plotly 5.17.0, Matplotlib 3.9.4
- **HTTP Client**: requests 2.32.3
- **File Processing**: openpyxl 3.1.5, xlrd 2.0.1
- **Styling**: Custom CSS3 + HTML5 injection
- **Email**: SMTP Gmail integration

### Deployment
- **Platform**: Render Cloud
- **Environment**: Production-ready with health checks
- **Monitoring**: Multi-level health endpoints
- **Security**: HTTPS, CORS, input validation

## 📊 Performance Metrics

| Component | Metric | Target | Actual |
|-----------|--------|--------|--------|
| **FinBot Chat** | Response Time | < 15s | < 12s |
| **Chart Generation** | Interactive Charts | < 5s | < 3s |
| **Stock Analysis** | Complete Analysis | < 90s | < 60s |
| **Islamic Expert** | Research + Analysis | < 180s | < 120s |
| **File Upload** | 10MB Processing | < 15s | < 10s |
| **Frontend** | Page Load | < 3s | < 2s |

## 🎨 Screenshots & Visual Gallery

### 🏠 Home Page with Logo
<div align="center">
<img src="assets/screenshot_home.png" alt="Abacus FinBot Home Page" width="600" style="border-radius: 10px; margin: 10px;">
</div>

### 💬 FinBot Chat Interface
<div align="center">
<img src="assets/screenshot_finbot_chat.png" alt="FinBot Chat Interface" width="600" style="border-radius: 10px; margin: 10px;">
</div>

### 📊 Smart Visualizations
<div align="center">
<img src="assets/screenshot_charts.png" alt="Interactive Charts" width="600" style="border-radius: 10px; margin: 10px;">
</div>

### 📈 Stock Analysis Dashboard
<div align="center">
<img src="assets/screenshot_stock_analysis.png" alt="Stock Analysis" width="600" style="border-radius: 10px; margin: 10px;">
</div>

### 🕌 Islamic Finance Expert
<div align="center">
<img src="assets/screenshot_islamic_expert.png" alt="Islamic Finance Expert" width="600" style="border-radius: 10px; margin: 10px;">
</div>

> **Note**: Screenshots will be automatically displayed once you add them to the `assets/` folder

---

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key

# Optional
MODEL_NAME=gpt-4o                 # AI model selection
ENVIRONMENT=development           # development/production
PORT=8000                        # Backend port
DATABASE_URL=sqlite:///./finbot_users.db
```

### Advanced Configuration
```python
# config.py
class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    MODEL_NAME: str = "gpt-4o"
    SAMPLE_MIN_ROWS: int = 200
    SAMPLE_MAX_ROWS: int = 400
    MAX_FILE_BYTES: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_ORIGINS: list[str] = ["*"]
```

## 🧪 Testing

### Manual Testing
```bash
# Test authentication
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@finbot.com", "password": "test123"}'

# Test stock analysis
curl -X POST "http://localhost:8000/stock/analyze-sync" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL"}'

# Test Islamic analysis
curl -X POST "http://localhost:8000/islamic/expert-analyze" \
  -H "Content-Type: application/json" \
  -d '{"investment_query": "Apple Inc"}'
```

### Health Checks
```bash
# Global health status
curl http://localhost:8000/health/all

# Individual agent status
curl http://localhost:8000/stock/health
curl http://localhost:8000/islamic/expert-status
```

## 🚀 Deployment

### Local Development
```bash
# Start backend
python main.py

# Start frontend (new terminal)
streamlit run UI_streamlit.py
```

### Production Deployment (Render)
1. **Backend**: Deploy `main.py` with auto-build
2. **Frontend**: Deploy Streamlit app
3. **Environment**: Set `OPENAI_API_KEY` in Render dashboard
4. **Health Checks**: Configure `/ready` endpoint


WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation

## 🐛 Issues & Support
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Achievements & Recognition

- 🥇 **First Islamic Expert Agent** with real-time internet research
- 🎨 **Innovative Chat-to-Chart** natural language visualization
- 🏗️ **Modern Multi-Agent Architecture** with specialized domains
- 📊 **Professional-Grade Analytics** with 20+ financial metrics
- 🔐 **Enterprise-Ready Security** with dual-hash authentication

### 🔮 Future Enhancements

- 🔗 **WebSocket Integration**: Real-time streaming responses
- 📱 **Progressive Web App**: Offline capabilities  
- 🎨 **Advanced Visualizations**: 3D charts and dashboards
- 🗣️ **Voice Commands**: Speech-to-text chart generation
- 🤖 **Agent04 - Crypto Expert**: Cryptocurrency and DeFi analysis
- 🏢 **Enterprise Features**: Multi-tenancy and RBAC
- 📱 **Mobile Native App**: React Native implementation
- 🔐 **Enhanced Security**: Biometric authentication
- 🌍 **Global Deployment**: Multi-region support

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/abacus-finbot&type=Date)](https://star-history.com/#yourusername/abacus-finbot&Date)

---

<div align="center">

**Made with ❤️ by the Abacus FinBot Team**

📧 [Email](mailto:contact@abacusfinbot.com) • 💼 [LinkedIn](https://linkedin.com/company/abacusfinbot)

</div>
