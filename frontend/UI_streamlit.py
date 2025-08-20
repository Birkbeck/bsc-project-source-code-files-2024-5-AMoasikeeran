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
🎯 **ANALYSIS SUMMARY:**
- **Verdict:** {islamic_status}
- **Confidence:** {confidence_level}
- **Sources:** {len(sources_used)} types used
- **Internet Research:** ✅ Real-time data
"""
        
        ss.islamic_messages.append({
            "role": "bot", 
            "text": response,
            "status": islamic_status,
            "raw_result": result,
            "confidence": confidence_level,
            "research_based": True
        })
    else:
        error_message = f"""❌ **Expert Agent Error**

{result.get('message', 'Unknown error')}

🔧 **Possible Solutions:**
- Check your internet connection
- Rephrase your question
- Try again in a moment
"""
        ss.islamic_messages.append({
            "role": "bot", 
            "text": error_message
        })
    
    ss.clear_islamic_input = True

# ---------- Logo Component for Pages ----------
def show_page_logo():
    """Display logo at top of each page - ULTRA PERFECTLY CENTRED"""
    # Create a full-width centred container
    st.markdown("""
    <div style='width: 100%; height: auto; display: flex; justify-content: center; align-items: center; 
                margin: 20px auto; text-align: center; position: relative;'>
    """, unsafe_allow_html=True)
    
    if LOGO.exists():
        # Triple centring approach for images
        col_empty1, col_logo, col_empty2 = st.columns([2, 1, 2])
        with col_logo:
            st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; 
                        width: 100%; text-align: center; margin: 0 auto;'>
            """, unsafe_allow_html=True)
            st.image(str(LOGO), width=150)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Ultra-centred text logo
        st.markdown("""
        <div style='width: 100%; display: flex; justify-content: center; align-items: center; 
                    position: relative; left: 50%; transform: translateX(-50%);'>
            <div style='font-size: 1.5rem; font-weight: 700; margin: 0 auto; text-align: center;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                        background-clip: text; display: inline-block; position: relative;
                        left: 0; right: 0;'>
                🤖 ABACUS FinBot
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Top Navigation Bar ----------
def show_top_navigation():
    """Show top navigation bar with logout"""
    st.markdown("""
    <div class="top-navbar">
        <div class="navbar-left">
            <span class="navbar-title">🤖 Abacus FinBot</span>
        </div>
        <div class="navbar-right">
            <span class="user-info">👤 {user_name}</span>
        </div>
    </div>
    """.format(user_name=ss.user_info['name']), unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        if st.button("🚪 Logout", key="logout_btn", help="Sign out"):
            logout()
            st.rerun()

# ---------- Session State Initialisation ----------
ss = st.session_state
ss.setdefault("chat_started", False)
ss.setdefault("show_login", False)
ss.setdefault("show_forgot_password", False)
ss.setdefault("forgot_password_email", "")
ss.setdefault("forgot_password_message", "")
ss.setdefault("forgot_password_success", False)
ss.setdefault("login_error", "")
ss.setdefault("user_info", None)
ss.setdefault("current_page", "menu")

# FINBOT CHAT - 
ss.setdefault("finbot_session_id", None)
ss.setdefault("finbot_context", "sample")
ss.setdefault("finbot_messages", [])
ss.setdefault("finbot_uploader", False)

# STOCK ANALYSIS -  
ss.setdefault("stock_results", None)
ss.setdefault("last_analysed_symbol", "")
ss.setdefault("stock_chat_messages", [])

# ISLAMIC ANALYSIS - 
ss.setdefault("islamic_messages", [])
ss.setdefault("islamic_input_field", "")
ss.setdefault("clear_islamic_input", False)

st.set_page_config(
    page_title="Abacus FinBot", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- Enhanced CSS Styles ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    /* Gradients */
    --primary-gradient: linear-gradient(135deg, #FF8C42 0%, #FF6B35 100%);
    --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    --warning-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    --danger-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    --dark-gradient: linear-gradient(135deg, #434343 0%, #000000 100%);

    /* Orange Theme */
    --orange-primary: #FF8C42;
    --orange-secondary: #FF6B35;
    --orange-hover: #FF7A3D;

    /* Background colour */
    --main-bg: #FDF9F4;
    --light-bg: #fefcf9;

    /* Effects */
    --card-shadow: 0 10px 30px rgba(139, 69, 19, 0.08);
    --hover-shadow: 0 15px 40px rgba(139, 69, 19, 0.12);
    --border-radius: 16px;
    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* FORCE BACKGROUND #FDF9F4 EVERYWHERE */
html, body, [data-testid="stAppViewContainer"], .main, .block-container {
    background: #FDF9F4 !important;
    background-color: #FDF9F4 !important;
}

.stApp {
    background: #FDF9F4 !important;
    background-color: #FDF9F4 !important;
}

/* Override Streamlit default backgrounds */
.css-1d391kg, .css-1y4p8pa, .css-12oz5g7, .css-1lcbmhc {
    background: #FDF9F4 !important;
    background-color: #FDF9F4 !important;
}

/* Main content area */
.main > div {
    background: #FDF9F4 !important;
    background-color: #FDF9F4 !important;
    padding-top: 90px !important;
}

/* Container backgrounds */
div[data-testid="column"] {
    background: transparent !important;
}

/* Force #FDF9F4 on all containers */
.css-ocqkz7, .css-1kyxreq, .css-1v3fvcr {
    background: #FDF9F4 !important;
}

/* Streamlit specific backgrounds */
[data-testid="stAppViewContainer"] {
    background-color: #FDF9F4 !important;
}

/* Centre the main container vertically and horizontally */
[data-testid="stAppViewContainer"] > .main > .block-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh !important;
    gap: 24px;
    max-width: 100%;
    padding-top: 0;
    padding-bottom: 0;
    background-color: #FDF9F4 !important;
}

/* Card backgrounds adjusted for #FDF9F4 */
.service-card {
    background: #F8F4EE !important;
    border-radius: var(--border-radius);
    padding: 40px 30px;
    text-align: center;
    box-shadow: var(--card-shadow);
    transition: var(--transition);
    border: 1px solid rgba(210, 180, 140, 0.3);
    position: relative;
    overflow: hidden;
    cursor: pointer;
}

.service-card:hover {
    background: #F6F2EC !important;
    transform: translateY(-8px);
    box-shadow: var(--hover-shadow);
    border-color: rgba(102, 126, 234, 0.3);
}

/* Compact cards */
.compact-card {
    background: #F8F4EE !important;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    margin: 15px 0;
    border-left: 4px solid #667eea;
}

/* Upload modal and expanders */
.stExpander {
    background: #F8F4EE !important;
    border: 1px solid rgba(210, 180, 140, 0.3) !important;
    border-radius: 12px !important;
}

.stExpander > div {
    background: #F8F4EE !important;
}

/* TOP NAVIGATION BAR */
.top-navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 70px;
    background: linear-gradient(135deg, #FF8C42 0%, #FF6B35 100%);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 30px;
    z-index: 1000;
    box-shadow: 0 4px 20px rgba(255, 140, 66, 0.3);
    backdrop-filter: blur(10px);
}

.navbar-title {
    color: white;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.5px;
}

.user-info {
    color: white;
    font-size: 1rem;
    font-weight: 500;
    margin-right: 15px;
}

.main > div {
    padding-top: 90px !important;
}

/* CHAT BUBBLES */
.bub {
    border: none;
    border-radius: 20px;
    padding: 15px 20px;
    margin: 15px 0;
    font-weight: 500;
    position: relative;
    max-width: 80%;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    transition: var(--transition);
}

.user {
    background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 8px;
    box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
}

.user:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(33, 150, 243, 0.4);
}

/* BOT - ORANGE */
.bot {
    background: linear-gradient(135deg, #FF8C42 0%, #FF6B35 100%);
    color: white;
    margin-right: auto;
    border-bottom-left-radius: 8px;
    box-shadow: 0 4px 15px rgba(255, 140, 66, 0.3);
}

.bot:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(255, 140, 66, 0.4);
}

.islamic-bub {
    border: none;
    border-radius: 20px;
    padding: 18px 22px;
    margin: 15px 0;
    font-weight: 500;
    position: relative;
    max-width: 80%;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    transition: var(--transition);
}

/* ISLAMIC USER - BLUE */
.islamic-user {
    background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 8px;
    box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
}

.islamic-user:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(33, 150, 243, 0.4);
}

/* ISLAMIC BOT - ORANGE by default */
.islamic-bot {
    background: linear-gradient(135deg, #FF8C42 0%, #FF6B35 100%);
    color: white;
    margin-right: auto;
    border-bottom-left-radius: 8px;
    box-shadow: 0 4px 15px rgba(255, 140, 66, 0.3);
}

.islamic-bot:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(255, 140, 66, 0.4);
}

/* STATUS SPECIFIC COLOURS for Islamic Analysis */
/* HALAL - GREEN */
.islamic-halal {
    background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
    color: white;
}

/* HARAM - RED */
.islamic-haram {
    background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%) !important;
    color: white;
}

/* QUESTIONABLE - DARK ORANGE */
.islamic-questionable {
    background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%) !important;
    color: white;
}

/* LOGIN STYLES */
.login-error {
    color: #e53e3e !important;
    text-align: center !important;
    margin-bottom: 15px !important;
    font-weight: 600 !important;
    padding: 15px !important;
    background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%) !important;
    border-radius: 10px !important;
    border: 1px solid #fc8181 !important;
}

.forgot-password-message {
    text-align: center !important;
    margin: 15px 0 !important;
    font-weight: 600 !important;
    padding: 15px !important;
    border-radius: 10px !important;
}

.forgot-password-success {
    color: #38a169 !important;
    background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%) !important;
    border: 1px solid #68d391 !important;
}

.forgot-password-error {
    color: #e53e3e !important;
    background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%) !important;
    border: 1px solid #fc8181 !important;
}

/* STATUS CARDS */
.success-card {
    background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
    padding: 20px;
    border-radius: var(--border-radius);
    color: white;
    margin: 15px 0;
    text-align: center;
    box-shadow: var(--card-shadow);
    transition: var(--transition);
}

.stock-card {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    padding: 25px;
    border-radius: var(--border-radius);
    color: white;
    margin: 15px 0;
    box-shadow: var(--card-shadow);
    transition: var(--transition);
}

/* OPTIMISED BUTTONS - Orange Theme */
.stButton > button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #FF8C42 0%, #FF6B35 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 25px !important;
    padding: 15px 40px !important;
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 8px 25px rgba(255, 140, 66, 0.4) !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

.stButton > button[data-testid="baseButton-primary"]:hover {
    background: linear-gradient(135deg, #FF7A3D 0%, #FF5722 100%) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 15px 35px rgba(255, 140, 66, 0.6) !important;
}

/* FORM SUBMIT BUTTONS - Orange Theme */
.stForm button[type="submit"] {
    background: linear-gradient(135deg, #FF8C42 0%, #FF6B35 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(255, 140, 66, 0.3) !important;
}

.stForm button[type="submit"]:hover {
    background: linear-gradient(135deg, #FF7A3D 0%, #FF5722 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(255, 140, 66, 0.4) !important;
}

/* SPECIFIC FIX for Send button in FinBot */
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #FF8C42 0%, #FF6B35 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(255, 140, 66, 0.3) !important;
}

.stFormSubmitButton > button:hover {
    background: linear-gradient(135deg, #FF7A3D 0%, #FF5722 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(255, 140, 66, 0.4) !important;
}

/* ALL PRIMARY BUTTONS in orange */
button[kind="primary"], 
button[data-testid*="primary"],
.stButton > button:first-child {
    background: linear-gradient(135deg, #FF8C42 0%, #FF6B35 100%) !important;
    color: white !important;
    border: none !important;
}

button[kind="primary"]:hover, 
button[data-testid*="primary"]:hover,
.stButton > button:first-child:hover {
    background: linear-gradient(135deg, #FF7A3D 0%, #FF5722 100%) !important;
    transform: translateY(-1px) !important;
}

.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.6) !important;
}

/* TARGET SPECIFIC IMAGE CONTAINER CLASS */
.st-emotion-cache-83erdr {
    width: 100%;
    max-width: 100%;
    position: relative;
    display: flex !important;
    justify-content: center !important;
}

.st-emotion-cache-xhkv9f.et0utro2{
    margin: 0 auto;
}

/* TARGET IMAGE ELEMENT INSIDE THE CONTAINER */
.st-emotion-cache-83erdr img {
    display: block !important;
    margin: 0 auto !important;
}

/* CENTRE THE IMAGE (LOGO) */
[data-testid="image"] {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}

/* TARGET THE IMAGE ELEMENT SPECIFICALLY */
[data-testid="image"] > img {
    margin-left: auto !important;
    margin-right: auto !important;
    display: block !important;
}

/* ADDITIONAL TARGETING FOR THE CONTAINER OF THE IMAGE */
.element-container [data-testid="image"] {
    text-align: center !important;
}

/* CENTRE THE BUTTON */
.stButton {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}

/* LOGIN BUTTON FULL WIDTH STYLING */
.stButton > button[data-testid="baseButton-secondary"] {
    background: linear-gradient(135deg, #6c757d 0%, #495057 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3) !important;
    margin-bottom: 10px !important;
}

.stButton > button[data-testid="baseButton-secondary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(108, 117, 125, 0.4) !important;
}

/* CHART CONTAINER STYLES */
.chart-container {
    background: #F8F4EE !important;
    border-radius: 12px !important;
    padding: 20px !important;
    margin: 15px 0 !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
    border: 1px solid rgba(210, 180, 140, 0.3) !important;
}

/* ANIMATED ICONS FOR SERVICES */
@keyframes bounce {
    0%, 20%, 50%, 80%, 100% {
        transform: translateY(0);
    }
    40% {
        transform: translateY(-10px);
    }
    60% {
        transform: translateY(-5px);
    }
}

@keyframes pulse {
    0% {
        transform: scale(1);
        opacity: 1;
    }
    50% {
        transform: scale(1.1);
        opacity: 0.8;
    }
    100% {
        transform: scale(1);
        opacity: 1;
    }
}

@keyframes glow {
    from {
        filter: drop-shadow(0 0 10px #43e97b) drop-shadow(0 0 20px #43e97b);
        transform: scale(1);
    }
    to {
        filter: drop-shadow(0 0 20px #38f9d7) drop-shadow(0 0 30px #38f9d7);
        transform: scale(1.05);
    }
}
</style>
""", unsafe_allow_html=True)

# ==================== ENHANCED HOME SCREEN (LOGIN) ====================
if not ss.chat_started:
    # Centred logo and minimal text
    col1, col2, col3 = st.columns([1, 2, 1])
    
    # Centred logo and minimal text
    st.markdown("""
    <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; 
                text-align: center; margin: 50px 0;'>
    """, unsafe_allow_html=True)
    
    # Logo
    if LOGO.exists():
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image(str(LOGO), width=280)
    else:
        st.markdown("""
        <div style='font-size: 4rem; font-weight: 800; margin: 30px auto; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                    background-clip: text; display: inline-block; text-align: center;'>
            🤖 ABACUS FinBot 📊
        </div>
        """, unsafe_allow_html=True)
    
    # Minimal subtitle
    st.markdown("""
    <div style='text-align: center; font-size: 1.2rem; color: #666; margin: 20px auto 40px auto; 
                font-weight: 500; max-width: 400px;'>
        AI-Powered Financial Intelligence with Advanced Data Visualisation
    </div>
    """, unsafe_allow_html=True)
    
    # Large centred login button
    col1, col2, col3 = st.columns([0.5, 1, 0.5])
    with col2:
        if st.button("🚀 GET STARTED", key="main_login", use_container_width=True, type="primary"):
            start_chat()
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Enhanced login modal
    if ss.show_login:
        with st.expander("🔐 Secure Login", expanded=True):
            if ss.login_error:
                st.markdown(f"<div class='login-error'>{ss.login_error}</div>", unsafe_allow_html=True)
            
            st.text_input("📧 Email", key="user_email", placeholder="Your professional email address")
            st.text_input("🔒 Password", key="user_password", type="password", placeholder="Your secure password")
            
            # Same level buttons
            col1, col2 = st.columns(2)
            with col1:
                st.button("❌ Cancel", on_click=cancel_login, key="cancel_login", use_container_width=True, type="secondary")
            with col2:
                st.button("✅ Sign In", on_click=submit_login, key="submit_login", type="primary", use_container_width=True)
            
            st.markdown("---")
            if st.button("🔐 Forgot Password?", on_click=show_forgot_password, key="forgot_password_btn", use_container_width=True):
                pass

    # Enhanced forgot password modal
    if ss.show_forgot_password:
        with st.expander("🔐 Password Recovery", expanded=True):
            st.markdown("### 📧 Secure Recovery")
            st.markdown("Our administrator will be automatically notified and will contact you quickly to reset your access.")
            
            if ss.forgot_password_message:
                if ss.get("forgot_password_success", False):
                    st.markdown(f"<div class='forgot-password-message forgot-password-success'>{ss.forgot_password_message}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='forgot-password-message forgot-password-error'>{ss.forgot_password_message}</div>", unsafe_allow_html=True)
            
            st.text_input("📧 Your email address", key="forgot_password_email", placeholder="example@company.com")
            
            col1, col2 = st.columns(2)
            with col1:
                st.button("← Back to Login", on_click=cancel_forgot_password, key="cancel_forgot_password", use_container_width=True)
            with col2:
                st.button("📤 Send Request", on_click=submit_forgot_password, key="submit_forgot_password", type="primary", use_container_width=True)
    
    st.stop()

# ==================== TOP NAVIGATION BAR ====================
if ss.chat_started:
    show_top_navigation()

# ==================== OPTIMISED MAIN MENU ====================
if ss.current_page == "menu":
    show_page_logo()
    
    # ULTRA PERFECTLY CENTRED welcome with user name
    st.markdown(f"""
    <div style='width: 100%; display: flex; justify-content: center; align-items: center; 
                margin: 30px auto 50px auto; text-align: center; position: relative;'>
        <h1 style='font-size: 2.2rem; font-weight: 700; color: #2d3748; margin: 0 auto;
                   text-align: center; display: block; position: relative; 
                   left: 50%; transform: translateX(-50%);'>
            Welcome {ss.user_info['name']}! 👋
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # ULTRA CENTRED service buttons in single row
    col1, col2, col3, col4, col5 = st.columns([0.1, 1, 1, 1, 0.1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 20px; display: flex; 
                    flex-direction: column; align-items: center; justify-content: center;'>
            <div style='margin-bottom: 15px; animation: bounce 2s infinite; 
                        display: flex; justify-content: center; width: 100%;'>
                <svg width="80" height="80" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style="margin: 0 auto;">
                    <defs>
                        <linearGradient id="chatGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <circle cx="50" cy="50" r="45" fill="url(#chatGrad)" stroke="#fff" stroke-width="2"/>
                    <circle cx="35" cy="40" r="3" fill="white"/>
                    <circle cx="50" cy="40" r="3" fill="white"/>
                    <circle cx="65" cy="40" r="3" fill="white"/>
                    <path d="M25 60 Q50 75 75 60" stroke="white" stroke-width="3" fill="none"/>
                    <rect x="20" y="65" width="60" height="8" rx="4" fill="white" opacity="0.7"/>
                </svg>
            </div>
            <h3 style='margin: 0 0 10px 0; color: #2d3748; text-align: center;'>FinBot Chat & Viz</h3>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Chat", key="btn_finbot", use_container_width=True, type="primary"):
            go_to_finbot()
            st.rerun()
    
    with col3:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 20px; display: flex; 
                    flex-direction: column; align-items: center; justify-content: center;'>
            <div style='margin-bottom: 15px; animation: pulse 2s infinite;
                        display: flex; justify-content: center; width: 100%;'>
                <svg width="80" height="80" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style="margin: 0 auto;">
                    <defs>
                        <linearGradient id="stockGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#4facfe;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#00f2fe;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="10" y="10" width="80" height="80" rx="8" fill="url(#stockGrad)" stroke="#fff" stroke-width="2"/>
                    <rect x="20" y="70" width="8" height="15" fill="white" rx="2"/>
                    <rect x="35" y="60" width="8" height="25" fill="white" rx="2"/>
                    <rect x="50" y="45" width="8" height="40" fill="white" rx="2"/>
                    <rect x="65" y="55" width="8" height="30" fill="white" rx="2"/>
                    <path d="M20 35 L35 30 L50 25 L65 20 L80 25" stroke="white" stroke-width="3" fill="none"/>
                    <circle cx="20" cy="35" r="3" fill="white"/>
                    <circle cx="35" cy="30" r="3" fill="white"/>
                    <circle cx="50" cy="25" r="3" fill="white"/>
                    <circle cx="65" cy="20" r="3" fill="white"/>
                    <circle cx="80" cy="25" r="3" fill="white"/>
                </svg>
            </div>
            <h3 style='margin: 0 0 10px 0; color: #2d3748; text-align: center;'>Stock Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Analyse Stocks", key="btn_stocks", use_container_width=True, type="primary"):
            go_to_stocks()
            st.rerun()
    
    with col4:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 20px; display: flex; 
                    flex-direction: column; align-items: center; justify-content: center;'>
            <div style='margin-bottom: 15px; animation: glow 3s ease-in-out infinite alternate;
                        display: flex; justify-content: center; width: 100%;'>
                <svg width="80" height="80" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style="margin: 0 auto;">
                    <defs>
                        <linearGradient id="islamicGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#43e97b;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#38f9d7;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <circle cx="50" cy="50" r="45" fill="url(#islamicGrad)" stroke="#fff" stroke-width="2"/>
                    <!-- Mosque dome -->
                    <ellipse cx="50" cy="45" rx="25" ry="20" fill="white"/>
                    <!-- Minaret -->
                    <rect x="20" y="25" width="6" height="35" fill="white" rx="3"/>
                    <rect x="74" y="25" width="6" height="35" fill="white" rx="3"/>
                    <!-- Minaret tops -->
                    <ellipse cx="23" cy="22" rx="4" ry="3" fill="white"/>
                    <ellipse cx="77" cy="22" rx="4" ry="3" fill="white"/>
                    <!-- Central minaret -->
                    <rect x="47" y="15" width="6" height="25" fill="white" rx="3"/>
                    <ellipse cx="50" cy="12" rx="4" ry="3" fill="white"/>
                    <!-- Door -->
                    <path d="M45 65 Q50 60 55 65 L55 75 L45 75 Z" fill="white"/>
                    <!-- Stars -->
                    <text x="35" y="35" fill="gold" font-size="8">☪</text>
                    <text x="65" y="38" fill="gold" font-size="6">⭐</text>
                </svg>
            </div>
            <h3 style='margin: 0 0 10px 0; color: #2d3748; text-align: center;'>Islamic Finance</h3>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Islamic Analysis", key="btn_islamic", use_container_width=True, type="primary"):
            go_to_islamic()
            st.rerun()

# ==================== ENHANCED FINBOT PAGE WITH VISUALISATIONS ====================
elif ss.current_page == "finbot":
    show_page_logo()
    
    # Header
    st.markdown("""
    <div style='width: 100%; display: flex; justify-content: center; align-items: center; 
                margin: 20px 0; position: relative;'>
        <div style='position: absolute; left: 0;'>
    """, unsafe_allow_html=True)
    
    if st.button("← Menu", key="back_finbot"):
        ss.current_page = "menu"
        st.rerun()
    
    st.markdown("""
        </div>
        <div style='text-align: center; margin: 0 auto;'>
            <h2 style='text-align: center; margin: 0; color: #2d3748; font-weight: 700;'>
                💬 FinBot Chat & Visualisations
            </h2>
        </div>
        <div style='position: absolute; right: 0;'>
    """, unsafe_allow_html=True)
    
    if st.button("📁 Upload", key="finbot_upload_btn", help="Upload Excel/CSV"):
        open_finbot_uploader()
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # FinBot Chat History - INDEPENDENT
    for i, m in enumerate(ss.finbot_messages):
        cls = "user" if m["role"] == "user" else "bot"
        st.markdown(f"<div class='bub {cls}'>{m['text']}</div>", unsafe_allow_html=True)
        
        # Display charts
        if m.get("chart_data"):
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            chart_key = f"finbot_plotly_chart_msg_{i}"
            if display_plotly_chart(m["chart_data"], chart_key):
                col_download, col_space = st.columns([0.3, 0.7])
                with col_download:
                    if st.button(f"📊 Download Chart", key=f"finbot_download_interactive_{i}"):
                        chart_json = json.dumps(m["chart_data"], indent=2)
                        st.download_button(
                            "📄 Download Chart Data (.json)",
                            chart_json,
                            f"finbot_chart_{int(time.time())}.json",
                            "application/json",
                            key=f"finbot_download_json_{i}"
                        )
            st.markdown("</div>", unsafe_allow_html=True)
            
        elif m.get("chart"):
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.image(f"data:image/png;base64,{m['chart']}", use_column_width=True)
            col_download, col_space = st.columns([0.3, 0.7])
            with col_download:
                if st.button(f"💾 Download Image", key=f"finbot_download_static_{i}"):
                    image_data = base64.b64decode(m['chart'])
                    st.download_button(
                        "🖼️ Download Chart (.png)",
                        image_data,
                        f"finbot_chart_{int(time.time())}.png",
                        "image/png",
                        key=f"finbot_download_png_{i}"
                    )
            st.markdown("</div>", unsafe_allow_html=True)

    # FinBot Upload Modal
    if ss.finbot_uploader:
        with st.expander("📁 Upload Your Financial Data", expanded=True):
            uploaded_file = st.file_uploader(
                "Select Excel/CSV file",
                type=["xlsx", "xls", "csv", "xlsm", "ods"],
                key="finbot_file_uploader",
                help="Upload your financial data to analyse and visualise"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("❌ Cancel", key="finbot_cancel_upload", use_container_width=True):
                    cancel_finbot_upload()
            with col2:
                if st.button("📤 Upload & Link to Chat", key="finbot_confirm_upload", 
                           disabled=st.session_state.finbot_file_uploader is None, 
                           type="primary", use_container_width=True):
                    confirm_finbot_upload()

    # Helpful message
    if not ss.finbot_session_id and not ss.finbot_uploader:
        st.info("💡 **Tip**: Upload your financial data first, then ask me questions about it or request visualisations!")

    # FinBot Chat Input
    st.markdown("---")
    with st.form("finbot_chart_form", clear_on_submit=True):
        user_msg = st.text_input(
            "💭 Ask about your data or request visualisations", 
            key="finbot_user_input", 
            placeholder="Examples: 'Show me spending by category', 'Create a pie chart of expenses', 'What's my highest expense?'", 
            label_visibility="collapsed"
        )
        
        col_context, col_send = st.columns([0.8, 0.2])
        
        with col_send:
            submitted = st.form_submit_button("🚀 Send", use_container_width=True, type="primary")
        
        if submitted:
            submit_finbot_message(user_msg)
            st.rerun()

# ==================== STOCK ANALYSIS PAGE ====================
elif ss.current_page == "stocks":
    show_page_logo()
    
    # Header
    st.markdown("""
    <div style='width: 100%; display: flex; justify-content: center; align-items: center; 
                margin: 20px 0; position: relative;'>
        <div style='position: absolute; left: 0;'>
    """, unsafe_allow_html=True)
    
    if st.button("← Menu", key="back_stocks"):
        ss.current_page = "menu"
        st.rerun()
    
    st.markdown("""
        </div>
        <div style='text-align: center; margin: 0 auto;'>
            <h2 style='text-align: center; margin: 0; color: #2d3748; font-weight: 700;'>
                📊 Stock Analysis
            </h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_main, col_sidebar = st.columns([2, 1])
    
    with col_main:
        st.markdown("### 🎯 Analyse a Stock")
        
        stock_symbol = st.text_input(
            "Stock symbol:",
            placeholder="Ex: AAPL, TSLA, MSFT, GOOGL...",
            key="stock_input_main"
        )
        
        if stock_symbol:
            stock_symbol = stock_symbol.upper().strip()
            st.markdown(f"**Selected stock:** `{stock_symbol}`")
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("🚀 AI Analysis", disabled=not stock_symbol, type="primary", use_container_width=True):
                if stock_symbol:
                    result = analyse_stock_request(stock_symbol)
                    ss.stock_results = result
                    ss.last_analysed_symbol = stock_symbol
                    ss.stock_chat_messages.append({
                        "role": "user", 
                        "text": f"Analyse {stock_symbol}"
                    })
                    if result.get("status") == "success":
                        ss.stock_chat_messages.append({
                            "role": "bot", 
                            "text": f"✅ Analysis completed for {stock_symbol}"
                        })
                    st.rerun()
        
        with col_b:
            if st.button("💰 Price", disabled=not stock_symbol, use_container_width=True):
                if stock_symbol:
                    with st.spinner("Getting price..."):
                        result = get_stock_price_request(stock_symbol)
                    if result.get("status") == "success":
                        ss.stock_chat_messages.append({
                            "role": "user", 
                            "text": f"Get price for {stock_symbol}"
                        })
                        ss.stock_chat_messages.append({
                            "role": "bot", 
                            "text": f"💰 {stock_symbol}: {result['price']}"
                        })
                        st.rerun()
        
        with col_c:
            if st.button("ℹ️ Info", disabled=not stock_symbol, use_container_width=True):
                if stock_symbol:
                    with st.spinner("Getting information..."):
                        result = get_stock_info_request(stock_symbol)
                    if result.get("status") == "success":
                        ss.stock_chat_messages.append({
                            "role": "user", 
                            "text": f"Get info for {stock_symbol}"
                        })
                        ss.stock_chat_messages.append({
                            "role": "bot", 
                            "text": f"ℹ️ Company info retrieved for {stock_symbol}"
                        })
                        st.rerun()
        if ss.stock_results and ss.stock_results.get("status") == "success":
            st.markdown("---")
            analysed_symbol = ss.stock_results.get('symbol') or ss.last_analysed_symbol
            
            st.markdown(f"""
            <div class='stock-card'>
                <h2>🎉 Analysis Complete - {analysed_symbol}</h2>
                <p>Comprehensive report generated by FinBot AI</p>
            </div>
            """, unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["📈 Detailed Analysis", "💡 Recommendations"])
            
            with tab1:
                if ss.stock_results.get("analysis"):
                    st.markdown(ss.stock_results["analysis"])
                    
            with tab2:
                if ss.stock_results.get("recommendation"):
                    st.markdown(ss.stock_results["recommendation"])

    with col_sidebar:
        st.markdown("#### 💬 Stock Chat")
        for i, m in enumerate(ss.stock_chat_messages):
            cls = "user" if m["role"] == "user" else "bot"
            st.markdown(f"<div class='bub {cls}' style='font-size: 0.9rem; padding: 8px 12px;'>{m['text']}</div>", unsafe_allow_html=True)
        
        with st.form("stock_chat_form", clear_on_submit=True):
            stock_question = st.text_input(
                "Ask about stocks:",
                placeholder="Ex: What's Tesla's P/E ratio?",
                key="stock_chat_input"
            )
            if st.form_submit_button("💬 Ask", use_container_width=True):
                if stock_question.strip():
                    ss.stock_chat_messages.append({
                        "role": "user", 
                        "text": stock_question
                    })
                    ss.stock_chat_messages.append({
                        "role": "bot", 
                        "text": "I can help with stock analysis. Use the buttons above to analyse specific stocks!"
                    })
                    st.rerun()

# ==================== ISLAMIC ANALYSIS PAGE ====================
elif ss.current_page == "islamic":
    show_page_logo()
    
    # Simple header with back button - PERFECTLY CENTRED
    st.markdown("""
    <div style='width: 100%; display: flex; justify-content: center; align-items: center; 
                margin: 20px 0; position: relative;'>
        <div style='position: absolute; left: 0;'>
    """, unsafe_allow_html=True)
    
    if st.button("← Menu", key="back_islamic"):
        ss.current_page = "menu"
        st.rerun()
    
    st.markdown("""
        </div>
        <div style='text-align: center; margin: 0 auto;'>
            <h2 style='text-align: center; margin: 0; color: #2d3748; font-weight: 700;'>
                🕌 Islamic Investment Analysis
            </h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat history area
    if ss.islamic_messages:
        chat_container = st.container()
        with chat_container:
            for i, m in enumerate(ss.islamic_messages):
                if m["role"] == "user":
                    st.markdown(f"<div class='islamic-bub islamic-user'>👤 {m['text']}</div>", unsafe_allow_html=True)
                else:
                    status = m.get("status", "")
                    if status == "HALAL ✅":
                        st.markdown(f"<div class='islamic-bub islamic-bot' style='background: linear-gradient(135deg, #28a745 0%, #20c997 100%);'>🤖 {m['text']}</div>", unsafe_allow_html=True)
                    elif status == "HARAM ❌":
                        st.markdown(f"<div class='islamic-bub islamic-bot' style='background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);'>🤖 {m['text']}</div>", unsafe_allow_html=True)
                    elif status == "QUESTIONABLE ⚠️":
                        st.markdown(f"<div class='islamic-bub islamic-bot' style='background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%); color: #000;'>🤖 {m['text']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='islamic-bub islamic-bot'>🤖 {m['text']}</div>", unsafe_allow_html=True)
                    
                    # Download button only if we have a complete analysis
                    if m.get("raw_result"):
                        col_download, col_space = st.columns([0.3, 0.7])
                        with col_download:
                            if st.button(f"📝 Download", key=f"download_{i}", use_container_width=True):
                                analysis_text = m["raw_result"].get("expert_analysis", m["text"])
                                st.download_button(
                                    "📄 Download Analysis (.md)",
                                    analysis_text,
                                    f"islamic_analysis_{int(time.time())}.md",
                                    "text/markdown",
                                    key=f"download_btn_{i}"
                                )
    else:
        # Simplified welcome message
        st.markdown("""
        <div style='text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                    border-radius: 15px; color: white; margin: 20px 0;'>
            <h3>🕌 Islamic Investment Analysis</h3>
            <p><strong>Ask me about any investment and get instant Sharia compliance analysis</strong></p>
            <p>Examples: "Is Apple halal?" • "Can I invest in Tesla?" • "Is Bitcoin allowed in Islam?"</p>
            <p><strong>Answers:</strong> HALAL ✅ | HARAM ❌ | QUESTIONABLE ⚠️</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Simplified chat interface - CORRECTED VERSION
    st.markdown("---")
    
    # Clear button OUTSIDE the form
    col_clear_top, col_space = st.columns([0.2, 0.8])
    with col_clear_top:
        if st.button("🗑️ Clear Chat", help="Clear chat history", key="clear_islamic_chat"):
            ss.islamic_messages = []
            st.rerun()
    
    # Chat input form (without clear button inside)
    with st.form("islamic_chat_form", clear_on_submit=True):
        col_input, col_send = st.columns([0.8, 0.2])
        
        with col_input:
            user_input = st.text_input(
                "Ask your Islamic investment question:",
                placeholder="Ex: Is Microsoft halal? Can I invest in Amazon? Bitcoin Islamic analysis?",
                key="islamic_chat_input",
                label_visibility="collapsed"
            )
        
        with col_send:
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🕌 Ask", type="primary", use_container_width=True)
        
        # Process submission
        if submitted and user_input.strip():
            # Add user message
            ss.islamic_messages.append({"role": "user", "text": user_input.strip()})
            
            # Get response from expert agent
            result = analyse_islamic_investment_request(user_input.strip())
            
            if result.get("status") == "success":
                islamic_status = result.get("islamic_status", "QUESTIONABLE ⚠️")
                analysis = result.get("analysis", "Analysis not available")
                confidence_level = result.get("confidence_level", "MEDIUM")
                sources_used = result.get("sources_used", [])
                
                # Enriched message with research metadata
                response = f"""{analysis}

---
🎯 **Analysis Summary:**
- **Verdict:** {islamic_status}
- **Confidence:** {confidence_level}
- **Sources:** {len(sources_used)} types used
- **Internet Research:** ✅ Real-time data
"""
                
                ss.islamic_messages.append({
                    "role": "bot", 
                    "text": response,
                    "status": islamic_status,
                    "raw_result": result,
                    "confidence": confidence_level,
                    "research_based": True
                })
            else:
                error_message = f"""❌ **Expert Agent Error**

{result.get('message', 'Unknown error')}

🔧 **Possible Solutions:**
- Check your internet connection
- Rephrase your question
- Try again in a moment
"""
                ss.islamic_messages.append({
                    "role": "bot", 
                    "text": error_message
                })
            
            st.rerun()

# ---------- Minimal Footer ----------
if ss.current_page != "menu":
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; margin: 20px 0; color: #666; font-size: 0.9rem;'>
        🤖 <strong>Abacus FinBot</strong> - Multi-Agent AI Platform with Advanced Data Visualisation
    </div>
    """, unsafe_allow_html=True)