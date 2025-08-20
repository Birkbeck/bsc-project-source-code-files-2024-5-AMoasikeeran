import streamlit as st
import requests
from pathlib import Path
import json
import time
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import plotly.express as px
import base64
from PIL import Image
import io
import pandas as pd

# ---------- Constants ----------
BACKEND = "http://localhost:8000"
CTX_OPTIONS = {
    "Summary": "summary",
    "Sample (200-400 rows)": "sample",
    "Full Dataset": "full",
}
LOGO = Path("assets/abacus_logo.jpeg")

ADMIN_EMAIL = "arvinmoasikeeran@gmail.com"

# Email Configuration
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email": "arvinmoasikeeran@gmail.com",
    "password": "eiku rvnn hsgx cptc"
}


def create_chart_request(chart_type, columns, title="", interactive=True, data=None):
    """Create a chart via the backend API"""
    try:
        payload = {
            "chart_type": chart_type,
            "columns": columns,
            "title": title,
            "interactive": interactive,
            "data": data
        }
        
        response = requests.post(f"{BACKEND}/finbot/create-chart", json=payload, timeout=120)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Chart creation error: {str(e)}"}

def smart_visualisation_request(user_prompt):
    try:
        payload = {"user_prompt": user_prompt}
        
        response = requests.post(f"{BACKEND}/finbot/smart-visualization", json=payload, timeout=180)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Smart visualisation error: {str(e)}"}

def upload_and_visualise_request(uploaded_file, chart_type="auto", columns="", interactive=True):
    try:
        files = {"file": uploaded_file}
        data = {
            "chart_type": chart_type,
            "columns": columns,
            "interactive": str(interactive).lower()
        }
        
        response = requests.post(f"{BACKEND}/finbot/upload-and-visualize", data=data, files=files, timeout=120)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Upload and visualise error: {str(e)}"}

def get_chart_types():
    try:
        response = requests.get(f"{BACKEND}/finbot/chart-types", timeout=30)
        response.raise_for_status()
        result = response.json()
        if result.get("success"):
            return result["chart_types"]
        return {}
    except Exception:
        return {}

def display_plotly_chart(chart_data, chart_key=None):
    try:
        if isinstance(chart_data, str):
            chart_data = json.loads(chart_data)
        
        fig = go.Figure(chart_data)
        if chart_key is None:
            chart_key = f"plotly_chart_{int(time.time() * 1000000)}"  
        
        st.plotly_chart(fig, use_container_width=True, key=chart_key, config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
        })
        return True
    except Exception as e:
        st.error(f"Chart display error: {e}")
        return False

def detect_chart_request(message):
    chart_keywords = [
        'chart', 'graph', 'plot', 'visualise', 'visualize', 'curve', 'graphique', 
        'bar', 'line', 'pie', 'scatter', 'histogram', 'box', 'violin',
        'heatmap', 'area', 'donut', 'histogramme',
        'show', 'display', 'draw', 'create', 'make', 'generate'
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in chart_keywords)

# ---------- Email Functions ----------
def send_forgot_password_notification(user_email):
    """Send notification to admin for forgotten password"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG["email"]
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = f"🔐 Password Reset Request - Abacus FinBot"
        
        body = f"""
Hello Admin,

A password reset request has been made on Abacus FinBot.

📧 User email: {user_email}
📅 Date and time: {datetime.now().strftime('%d/%m/%Y at %H:%M:%S')}
🌐 Platform: Abacus FinBot - Streamlit Interface

Action required:
Please contact this user to help with their password reset.

---
Automatic notification - Abacus FinBot System
🤖 Do not reply to this message
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.starttls()
        server.login(EMAIL_CONFIG["email"], EMAIL_CONFIG["password"])
        
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG["email"], ADMIN_EMAIL, text)
        server.quit()
        
        return {"success": True, "message": "Notification sent successfully"}
        
    except Exception as e:
        return {"success": False, "message": f"Error sending: {str(e)}"}

# ---------- Functions Agent03 (Islamic Analysis) - EXPERT VERSION ----------
def analyse_islamic_investment_request(investment_query):
    """Analyse an investment using the Expert Sharia Agent with internet research"""
    try:
        # Use expert endpoint instead of the old one
        payload = {"investment_query": investment_query}
        
        with st.spinner(f"🕌 EXPERT SHARIA ANALYSIS WITH INTERNET RESEARCH..."):
            # Use expert API that does internet research
            r = requests.post(f"{BACKEND}/islamic/expert-analyze", json=payload, timeout=240)
            r.raise_for_status()
            result = r.json()
            
            if result.get("status") == "success":
                # Expert agent returns a different structure
                analysis = result.get("expert_analysis", "")
                islamic_status = result.get("islamic_status", "QUESTIONABLE ⚠️")
                research_data = result.get("research_data", {})
                haram_screening = result.get("haram_screening", {})
                confidence_level = result.get("confidence_level", "MEDIUM")
                sources_used = result.get("sources_used", [])
                
                # Build enriched response with research data
                enhanced_response = f"""## 🕌 {islamic_status}

{analysis}

---
### 📊 **RESEARCH DATA COLLECTED**

"""
                
                # Add financial data if available
                if research_data.get("financial_data"):
                    financial = research_data["financial_data"]
                    if not financial.get("error"):
                        enhanced_response += f"""
**💰 Financial Data (Yahoo Finance):**
- Symbol: {financial.get('symbol', 'N/A')}
- Company: {financial.get('company_name', 'N/A')}
- Sector: {financial.get('sector', 'N/A')}
- Current Price: {financial.get('current_price', 'N/A')}
- Market Cap: {financial.get('market_cap', 'N/A')}

"""
                        # Add Sharia ratios if available
                        sharia_ratios = financial.get("sharia_ratios", {})
                        if sharia_ratios and not sharia_ratios.get("error"):
                            enhanced_response += f"""
**📈 Sharia Ratios:**
- Debt/Market Cap Ratio: {sharia_ratios.get('debt_to_market_cap', {}).get('value', 'N/A')}% (Limit: 33%)
- Debt Compliant: {'✅' if sharia_ratios.get('debt_to_market_cap', {}).get('compliant') else '❌'}
- Cash Ratio: {sharia_ratios.get('cash_to_market_cap', {}).get('value', 'N/A')}% (Limit: 33%)
"""
                
                # Add web search results
                if research_data.get("web_research", {}).get("results"):
                    enhanced_response += f"""
**🔍 Web Research:**
- Sources consulted: {len(research_data['web_research']['results'])} results
"""
                    for i, web_result in enumerate(research_data["web_research"]["results"][:2], 1):
                        enhanced_response += f"- [{web_result.get('title', 'Title not available')}]({web_result.get('url', '#')})\n"
                
                # Add news
                if research_data.get("recent_news", {}).get("news"):
                    news_items = research_data["recent_news"]["news"]
                    enhanced_response += f"""
**📰 Recent News:**
- Articles found: {len(news_items)}
"""
                    for news in news_items[:2]:
                        enhanced_response += f"- {news.get('title', 'Title not available')} ({news.get('source', 'Unknown source')})\n"
                
                # Add haram screening
                if haram_screening.get("haram_indicators_found"):
                    enhanced_response += f"""
**🚫 Automated Haram Screening:**
- Risk level: {haram_screening.get('risk_level', 'UNKNOWN')}
- Indicators found: {len(haram_screening['haram_indicators_found'])} categories
"""
                    for category, keywords in haram_screening["haram_indicators_found"].items():
                        enhanced_response += f"  - {category}: {', '.join(keywords[:3])}\n"
                
                enhanced_response += f"""

---
### 🎯 **ANALYSIS METADATA**
- **Confidence Level:** {confidence_level}
- **Agent Used:** {result.get('agent_type', 'Expert Sharia with research')}
- **Sources Consulted:** {len(sources_used)} types of sources
- **Timestamp:** {result.get('timestamp', 'N/A')}
- **Analysis Based On:** Real-time internet research + Islamic knowledge base

### 🔧 **Sources Used:**
{', '.join(sources_used) if sources_used else 'Multiple sources'}
"""
                
                return {
                    "status": "success",
                    "islamic_status": islamic_status,
                    "analysis": enhanced_response,
                    "research_data": research_data,
                    "haram_screening": haram_screening,
                    "confidence_level": confidence_level,
                    "sources_used": sources_used,
                    "raw_result": result
                }
            else:
                return {"status": "error", "message": result.get("message", "Expert analysis failed")}
            
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Timeout - Expert analysis taking longer than expected (internet research in progress...)"}
    except Exception as e:
        return {"status": "error", "message": f"Expert agent error: {str(e)}"}

def get_islamic_alternatives_request(haram_investment):
    """Get halal alternatives using Expert Agent research capabilities"""
    try:
        payload = {"haram_investment": haram_investment}
        with st.spinner(f"🔍 SEARCHING FOR HALAL ALTERNATIVES VIA EXPERT AGENT..."):
            # Use expert endpoint for alternatives
            r = requests.post(f"{BACKEND}/islamic/expert-alternatives", json=payload, timeout=180)
            r.raise_for_status()
            result = r.json()
            
            if result.get("status") == "success":
                alternatives = result.get("expert_alternatives", "No alternatives found")
                sector_research = result.get("sector_research", {})
                
                # Build enriched response
                enhanced_alternatives = f"""## 💡 HALAL ALTERNATIVES (EXPERT RESEARCH)

{alternatives}

---
### 📊 **SECTOR RESEARCH**
"""
                
                if sector_research.get("suggested_alternatives"):
                    enhanced_alternatives += f"""
**🎯 Suggested Alternatives:**
{', '.join(sector_research['suggested_alternatives'])}

**📈 Company Details:**
"""
                    for symbol, details in sector_research.get("alternative_details", {}).items():
                        enhanced_alternatives += f"""
- **{symbol}**: {details.get('name', 'N/A')} 
  - Sector: {details.get('sector', 'N/A')}
  - Price: {details.get('price', 'N/A')}
"""
                
                enhanced_alternatives += f"""

---
**🤖 Analysis Generated By:** {result.get('agent_type', 'Expert Sharia with research')}
**⏰ Timestamp:** {result.get('timestamp', 'N/A')}
**🔍 Based On:** Real-time internet research
"""
                
                return {
                    "status": "success",
                    "alternatives": enhanced_alternatives,
                    "sector_research": sector_research
                }
            else:
                return {"status": "error", "message": result.get("message", "Alternative search failed")}
                
    except Exception as e:
        return {"status": "error", "message": f"Alternative search error: {str(e)}"}

def get_islamic_status_request():
    """Get Expert Islamic Agent status"""
    try:
        r = requests.get(f"{BACKEND}/islamic/expert-status", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "message": f"Status error: {str(e)}"}

def research_company_islamic_request(company_name):
    """Research a company for Islamic analysis"""
    try:
        payload = {"company_name": company_name}
        with st.spinner(f"🔍 DEEP RESEARCH: {company_name}..."):
            r = requests.post(f"{BACKEND}/islamic/research-company", json=payload, timeout=180)
            r.raise_for_status()
            result = r.json()
            
            if result.get("status") == "success":
                research_data = result.get("research_data", {})
                haram_screening = result.get("haram_screening", {})
                
                response = f"""## 🔍 COMPANY RESEARCH: {company_name}

### 📊 **DATA COLLECTED**
"""
                
                # Display research data
                if research_data.get("financial_data"):
                    fin_data = research_data["financial_data"]
                    if not fin_data.get("error"):
                        response += f"""
**💰 Financial Information:**
- Company: {fin_data.get('company_name', 'N/A')}
- Sector: {fin_data.get('sector', 'N/A')}
- Industry: {fin_data.get('industry', 'N/A')}
- Website: {fin_data.get('website', 'N/A')}
- Employees: {fin_data.get('employees', 'N/A')}
"""
                
                # Haram screening
                if haram_screening.get("is_likely_haram"):
                    response += f"""
### 🚫 **HARAM SCREENING ALERT**
- Risk Level: {haram_screening.get('risk_level', 'UNKNOWN')}
- Issues Detected: {len(haram_screening.get('haram_indicators_found', {}))} categories
"""
                    for category, keywords in haram_screening.get("haram_indicators_found", {}).items():
                        response += f"  - {category.upper()}: {', '.join(keywords)}\n"
                else:
                    response += "\n### ✅ **HARAM SCREENING**: No problematic indicators detected\n"
                
                response += f"""

---
**🤖 Research Performed By:** Expert Sharia Agent
**⏰ Timestamp:** {result.get('timestamp', 'N/A')}
"""
                
                return {
                    "status": "success",
                    "research_summary": response,
                    "research_data": research_data,
                    "haram_screening": haram_screening
                }
            else:
                return {"status": "error", "message": result.get("message", "Research failed")}
                
    except Exception as e:
        return {"status": "error", "message": f"Research error: {str(e)}"}

# ---------- Stock Functions ----------
def analyse_stock_request(symbol):
    """Launch synchronous stock analysis"""
    try:
        payload = {"symbol": symbol}
        with st.spinner(f"🤖 FINBOT ANALYSING YOUR STOCK {symbol}"):
            r = requests.post(f"{BACKEND}/stock/analyze-sync", json=payload, timeout=300)
            r.raise_for_status()
            return r.json()
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Timeout - Analysis taking longer than expected."}
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}

def get_stock_price_request(symbol):
    """Get stock price"""
    try:
        payload = {"symbol": symbol}
        r = requests.post(f"{BACKEND}/stock/price", json=payload, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}

def get_stock_info_request(symbol):
    """Get company information"""
    try:
        payload = {"symbol": symbol}
        r = requests.post(f"{BACKEND}/stock/info", json=payload, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}

# ---------- Authentication Functions ----------
def authenticate_user(email, password):
    """Authenticate user via API"""
    try:
        payload = {"email": email.strip(), "password": password}
        r = requests.post(f"{BACKEND}/login", json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"success": False, "message": f"Connection error: {str(e)}"}

# ---------- Session helpers ----------
def ensure_session():
    """Guarantee that we have a valid session_id from the backend."""
    if st.session_state.get("session_id") is None:
        r = requests.post(f"{BACKEND}/session", timeout=10)
        r.raise_for_status()
        st.session_state.session_id = r.json()["session_id"]

# ---------- Navigation Functions ----------
def go_to_finbot():
    st.session_state.current_page = "finbot"

def go_to_stocks():
    st.session_state.current_page = "stocks"

def go_to_islamic():
    st.session_state.current_page = "islamic"

def logout():
    """Logout user and clear ALL chat sessions"""
    st.session_state.chat_started = False
    st.session_state.user_info = None
    st.session_state.current_page = "menu"
    
    # Clear FinBot session
    st.session_state.finbot_session_id = None
    st.session_state.finbot_messages = []
    st.session_state.finbot_uploader = False
    st.session_state.finbot_context = "sample"
    
    # Clear Stock session
    st.session_state.stock_results = None
    st.session_state.last_analysed_symbol = ""
    st.session_state.stock_chat_messages = []
    
    # Clear Islamic session
    st.session_state.islamic_messages = []
    st.session_state.islamic_input_field = ""

def ensure_finbot_session():
    """Guarantee that we have a valid session_id for FinBot."""
    if st.session_state.get("finbot_session_id") is None:
        r = requests.post(f"{BACKEND}/session", timeout=10)
        r.raise_for_status()
        st.session_state.finbot_session_id = r.json()["session_id"]

def open_finbot_uploader():
    st.session_state.finbot_uploader = True

def cancel_finbot_upload():
    st.session_state.finbot_uploader = False

def confirm_finbot_upload():
    file = st.session_state.finbot_file_uploader
    ensure_finbot_session()

    try:
        files = {"file": (file.name, file.getvalue())}
        data = {"session_id": st.session_state.finbot_session_id}
        r = requests.post(f"{BACKEND}/upload", files=files, data=data, timeout=60)
        r.raise_for_status()
        res = r.json()

        st.session_state.finbot_session_id = res["session_id"]
        st.session_state.finbot_context = "sample"
        st.success("✅ File uploaded and linked to FinBot chat!")
    except Exception as e:
        st.error(f"❌ Upload failed: {e}")
    st.session_state.finbot_uploader = False

def submit_finbot_message(msg: str):
    """Handle user sending a message in FinBot chat."""
    msg = (msg or "").strip()
    if not msg:
        return

    ensure_finbot_session()
    ss.finbot_messages.append({"role": "user", "text": msg})
    if detect_chart_request(msg):
        with st.spinner("🎨 Creating your visualisation..."):
            viz_result = smart_visualisation_request(msg)
            
            if viz_result.get("success") and viz_result.get("chart_data"):
                if viz_result.get("ai_interpretation"):
                    interpretation = viz_result["ai_interpretation"]
                    ai_msg = f"📊 I'll create a {interpretation.get('kind', 'chart')} for you using {', '.join(interpretation.get('columns', []))}"
                    ss.finbot_messages.append({"role": "bot", "text": ai_msg})
                ss.finbot_messages.append({
                    "role": "bot", 
                    "text": "📈 Here's your visualisation:",
                    "chart_data": viz_result["chart_data"],
                    "chart_type": "interactive"
                })
                return
            elif viz_result.get("ai_response"):
                ss.finbot_messages.append({"role": "bot", "text": viz_result["ai_response"]})
                return
    try:
        payload = {
            "session_id": ss.finbot_session_id,
            "message": msg,
            "context_mode": ss.finbot_context,
        }
        r = requests.post(f"{BACKEND}/chat", json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        ss.finbot_session_id = data.get("session_id", ss.finbot_session_id)
        bot_msg = data.get("answer", "(no response)")
        chart64 = data.get("chart_base64")
        
        message_data = {"role": "bot", "text": bot_msg}
        if chart64:
            message_data["chart"] = chart64
            message_data["chart_type"] = "static"
        
        ss.finbot_messages.append(message_data)
    except Exception as e:
        ss.finbot_messages.append({"role": "bot", "text": f"⚠️ Error: {e}"})


# ---------- Login Functions ----------
def start_chat():
    st.session_state.show_login = True

def show_forgot_password():
    """Show forgotten password form"""
    st.session_state.show_forgot_password = True
    st.session_state.show_login = False

def cancel_forgot_password():
    """Cancel forgotten password form"""
    st.session_state.show_forgot_password = False
    st.session_state.show_login = True
    st.session_state.forgot_password_email = ""
    st.session_state.forgot_password_message = ""

def submit_forgot_password():
    """Process forgotten password request"""
    email = st.session_state.forgot_password_email.strip()
    
    if not email:
        st.session_state.forgot_password_message = "Please enter your email address"
        return
    
    if "@" not in email or "." not in email:
        st.session_state.forgot_password_message = "Invalid email format"
        return
    
    result = send_forgot_password_notification(email)
    
    if result["success"]:
        st.session_state.forgot_password_message = f"✅ Request sent! The administrator will contact you at {email}"
        st.session_state.forgot_password_success = True
    else:
        st.session_state.forgot_password_message = f"❌ Error: {result['message']}"
        st.session_state.forgot_password_success = False

def submit_login():
    email = st.session_state.user_email.strip()
    password = st.session_state.user_password.strip()

    if not email or not password:
        st.session_state.login_error = "Please enter email and password"
        return

    if "@" not in email or "." not in email:
        st.session_state.login_error = "Invalid email format"
        return

    auth_result = authenticate_user(email, password)
    
    if not auth_result["success"]:
        st.session_state.login_error = auth_result["message"]
        return

    st.session_state.user_info = {
        "name": auth_result["user_name"], 
        "email": auth_result["user_email"]
    }
    st.session_state.show_login = False
    st.session_state.chat_started = True
    st.session_state.login_error = ""
    st.session_state.user_password = ""
    st.session_state.current_page = "menu"
    ensure_session()

def cancel_login():
    st.session_state.show_login = False
    st.session_state.login_error = ""
    st.session_state.user_password = ""

# ---------- Chat Functions ----------
def open_uploader():
    st.session_state.uploader = True

def cancel_upload():
    st.session_state.uploader = False

def confirm_upload():
    file = st.session_state.file_uploader
    ensure_session()

    try:
        files = {"file": (file.name, file.getvalue())}
        data = {"session_id": st.session_state.session_id}
        r = requests.post(f"{BACKEND}/upload", files=files, data=data, timeout=60)
        r.raise_for_status()
        res = r.json()

        st.session_state.session_id = res["session_id"]
        st.session_state.context = "sample"
        st.success("✅ File uploaded and linked to current chat!")
    except Exception as e:
        st.error(f"❌ Upload failed: {e}")
    st.session_state.uploader = False
def submit_message(msg: str):
    """Handle user sending a chat message with enhanced visualisation support."""
    msg = (msg or "").strip()
    if not msg:
        return

    ensure_session()
    ss.messages.append({"role": "user", "text": msg})
    if detect_chart_request(msg):
        with st.spinner("🎨 Creating your visualisation..."):
            viz_result = smart_visualisation_request(msg)
            
            if viz_result.get("success") and viz_result.get("chart_data"):
                if viz_result.get("ai_interpretation"):
                    interpretation = viz_result["ai_interpretation"]
                    ai_msg = f"📊 I'll create a {interpretation.get('kind', 'chart')} for you using {', '.join(interpretation.get('columns', []))}"
                    ss.messages.append({"role": "bot", "text": ai_msg})
                ss.messages.append({
                    "role": "bot", 
                    "text": "📈 Here's your visualisation:",
                    "chart_data": viz_result["chart_data"],
                    "chart_type": "interactive"
                })
                return
            elif viz_result.get("ai_response"):
                ss.messages.append({"role": "bot", "text": viz_result["ai_response"]})
                return
    try:
        payload = {
            "session_id": ss.session_id,
            "message": msg,
            "context_mode": ss.context,
        }
        r = requests.post(f"{BACKEND}/chat", json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        ss.session_id = data.get("session_id", ss.session_id)
        bot_msg = data.get("answer", "(no response)")
        chart64 = data.get("chart_base64")
        
        message_data = {"role": "bot", "text": bot_msg}
        if chart64:
            message_data["chart"] = chart64
            message_data["chart_type"] = "static"
        
        ss.messages.append(message_data)
    except Exception as e:
        ss.messages.append({"role": "bot", "text": f"⚠️ Error: {e}"})

# ---------- ISLAMIC CHAT FUNCTION - EXPERT VERSION ----------
def submit_islamic_message():
    """Send message in Islamic chat with enhanced Expert Agent"""
    if "islamic_input_field" not in ss or not ss.islamic_input_field:
        return
    
    msg = ss.islamic_input_field.strip()
    if not msg:
        return

    ss.islamic_messages.append({"role": "user", "text": msg})
    
    # Use expert agent with internet research
    result = analyse_islamic_investment_request(msg)
    
    if result.get("status") == "success":
        islamic_status = result.get("islamic_status", "QUESTIONABLE ⚠️")
        analysis = result.get("analysis", "Analysis not available")
        confidence_level = result.get("confidence_level", "MEDIUM")
        sources_used = result.get("sources_used", [])
        
        # Enriched message with research metadata
        response = f"""{analysis}

---
🎯 **
