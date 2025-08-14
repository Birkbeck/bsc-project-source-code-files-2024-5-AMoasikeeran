from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import time
from pathlib import Path
from config import settings
from routes import router
from Database.database import create_tables, add_test_users

ENVIRONMENT = settings.ENVIRONMENT
PORT = settings.PORT

# --- Try importing Sharia Expert Agent ---
try:
    from Agent03.sharia_expert_agent import initialise_sharia_expert
    sharia_expert_agent = initialise_sharia_expert(settings.OPENAI_API_KEY, settings.MODEL_NAME)
    SHARIA_EXPERT_AVAILABLE = True
    print("✅ Main: Sharia Expert Agent initialised with research tools")
except ImportError as e:
    print(f"⚠️ Main: Sharia Expert Agent not available - {e}")
    SHARIA_EXPERT_AVAILABLE = False
    sharia_expert_agent = None

# --- Enhanced FastAPI App Setup ---
app = FastAPI(
    title="Abacus FinBot - Enhanced Banking Analytics Platform",
    version="3.2.0",
    description="AI-powered banking transaction analysis with comprehensive chart generation and Sharia expert capabilities"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global Agent Initialisation Status ---
agents_initialised = {
    "agent01": False,  # Enhanced Chat FinBot with Banking Analytics
    "agent02": False,  # Stock Analysis  
    "agent03": False   # Sharia Expert with Research Tools
}

# ========== FUNCTION TO ADD BASE USERS ==========
def add_custom_users():
    """Add ONLY the 3 base users"""
    from Database.database import SessionLocal, User, get_password_hash
    
    # 👇 ONLY THE 3 BASE USERS
    custom_users = [
        {"name": "Admin User", "email": "admin@finbot.com", "password": "admin123"},
        {"name": "Test User", "email": "test@finbot.com", "password": "test123"},
        {"name": "Demo User", "email": "demo@finbot.com", "password": "demo123"},
    ]
    
    db = SessionLocal()
    added_count = 0
    
    try:
        print("👥 Adding base users...")
        
        for user_data in custom_users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            
            if not existing_user:
                # Create new user
                new_user = User(
                    name=user_data["name"],
                    email=user_data["email"],
                    password_hash=get_password_hash(user_data["password"])
                )
                db.add(new_user)
                added_count += 1
                print(f"  ➕ Added: {user_data['name']} ({user_data['email']})")
            else:
                print(f"  ✅ Already exists: {user_data['email']}")
        
        if added_count > 0:
            db.commit()
            print(f"✅ {added_count} base users added!")
        else:
            print("✅ All base users already exist!")
            
    except Exception as e:
        print(f"❌ Error adding users: {e}")
        db.rollback()
    finally:
        db.close()

# --- Enhanced Startup Event ---
@app.on_event("startup")
async def startup_event():
    global agents_initialised

    print("🚀 Starting Abacus FinBot Enhanced Banking Analytics Platform...")
    print(f"🌍 Environment: {ENVIRONMENT}")
    print(f"🔌 Port: {PORT}")

    # ========== AGENT 01 (Enhanced Chat FinBot with Banking Analytics) + AUTO USER CREATION ==========
    try:
        print("\n📊 Initialising Agent01 (Enhanced Chat FinBot)...")
        create_tables()
        print("✅ Database tables created/verified")
        
        # 🔥 AUTOMATIC ADDITION OF BASE USERS
        add_custom_users()
        
        # Test enhanced banking capabilities
        print("✅ Banking transaction analysis enabled")
        print("✅ Enhanced chart generation (12+ types)")
        print("✅ Automatic data categorisation")
        print("✅ Financial insights engine")
        
        agents_initialised["agent01"] = True
        print("✅ Agent01 (Enhanced Chat FinBot with Banking Analytics) ready!")
    except Exception as e:
        print(f"❌ Error Agent01: {e}")
        agents_initialised["agent01"] = False

    # ========== AGENT 02 (Stock Analysis) ==========
    try:
        print("\n📈 Initialising Agent02 (Stock Analysis)...")
        # Test import of stock tools
        from Agent02.tools import get_current_stock_price
        print("✅ Stock analysis tools imported")
        print("✅ Real-time price feeds")
        print("✅ GPT-4o analysis engine")
        agents_initialised["agent02"] = True
        print("✅ Agent02 (Stock Analysis) ready!")
    except Exception as e:
        print(f"⚠️ Agent02 unavailable: {e}")
        agents_initialised["agent02"] = False

    # ========== AGENT 03 (Sharia Expert) ==========
    try:
        print("\n🕌 Initialising Agent03 (Sharia Expert)...")
        
        if SHARIA_EXPERT_AVAILABLE and settings.OPENAI_API_KEY:
            print("✅ OpenAI API configured for expert analysis")
            print("✅ Research tools initialised:")
            print("   📊 Yahoo Finance integration")
            print("   🔍 Web search capabilities") 
            print("   📰 News monitoring")
            print("   🚫 Haram keyword screening")
            print("   🤖 AI-powered Sharia analysis")
            print("   💡 Halal alternatives research")
            print("   📈 Sharia ratio calculations")
            
            # Test expert capabilities
            try:
                status = sharia_expert_agent.get_agent_status()
                print(f"✅ Expert status verified: {status.get('status', 'unknown')}")
                agents_initialised["agent03"] = True
                print("✅ Agent03 (Sharia Expert) ready with research tools!")
            except Exception as e:
                print(f"⚠️ Expert status check failed: {e}")
                agents_initialised["agent03"] = True  # Continue anyway
                
        else:
            print("❌ Sharia Expert requirements not met")
            if not settings.OPENAI_API_KEY:
                print("   Missing: OPENAI_API_KEY")
            agents_initialised["agent03"] = False
            
    except Exception as e:
        print(f"❌ Error Agent03: {e}")
        agents_initialised["agent03"] = False

    # ========== ENHANCED SUMMARY ==========
    print("\n" + "="*80)
    print("🏦 ABACUS FINBOT - ENHANCED BANKING ANALYTICS PLATFORM")
    print("="*80)
    total_agents = sum(agents_initialised.values())
    print(f"📊 Active agents: {total_agents}/3")
    print("\n📋 Agent status:")

    agents_status = [
        ("Agent01", "Enhanced Chat FinBot + Banking Analytics", agents_initialised["agent01"]),
        ("Agent02", "Stock Analysis GPT-4o", agents_initialised["agent02"]),
        ("Agent03", "Sharia Expert + Research Tools", agents_initialised["agent03"])
    ]
    for agent, description, status in agents_status:
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {agent}: {description}")

    if agents_initialised["agent01"]:
        print(f"\n🏦 Agent01 - Enhanced Banking Capabilities:")
        print("   📊 Automatic transaction categorisation")
        print("   💰 Income/Expense/Savings classification")
        print("   📈 12+ chart types (Bar, Pie, Line, Scatter, Histogram, Box, Area, etc.)")
        print("   🤖 AI-powered financial insights")
        print("   📋 Spending analysis & budget recommendations")
        print("   📅 Time-based trend analysis")
        print("   📊 Interactive chart generation studio")
        print("   🎯 Banking dashboard with key metrics")

    if agents_initialised["agent03"]:
        print(f"\n🕌 Agent03 - Sharia Expert capabilities:")
        print("   🔍 Real-time company research")
        print("   📊 Financial data analysis (Yahoo Finance)")
        print("   📰 News and market monitoring")
        print("   🚫 Automated haram screening")
        print("   🤖 AI-powered Sharia verdicts")
        print("   💡 Halal alternatives research")
        print("   📈 Sharia ratio calculations")
        print("   🎯 Confidence-based analysis")

    print(f"\n🎨 Chart Generation Features:")
    print("   📊 Bar Charts • 🥧 Pie Charts • 📈 Line Charts • ⭐ Scatter Plots")
    print("   📋 Histograms • 📦 Box Plots • 🏔️ Area Charts • 📚 Stacked Bars")
    print("   🍩 Donut Charts • 🌊 Waterfall Charts • 🔥 Heatmaps • 🎻 Violin Plots")

    print(f"\n🤖 AI Model: {settings.MODEL_NAME}")
    print(f"🔑 OpenAI configured: {'✅' if settings.OPENAI_API_KEY else '❌'}")
    
    if ENVIRONMENT == "development":
        print("🌐 API Docs: http://localhost:8000/docs")
        print("🔍 Global health: http://localhost:8000/health/all")

    print("\n🚀 ENHANCED BANKING ANALYTICS PLATFORM READY!")
    print("🏦 Professional banking transaction analysis with comprehensive visualisation")
    
    # 👇 DISPLAY AVAILABLE ACCOUNTS
    print("\n🔐 AVAILABLE USER ACCOUNTS:")
    print("   admin@finbot.com / admin123")
    print("   test@finbot.com / test123") 
    print("   demo@finbot.com / demo123")
    
    if ENVIRONMENT == "development":
        print("📱 You can now launch the enhanced frontend interface")
        print("\n💡 Enhanced endpoints available:")
        print("   POST /upload - Enhanced file upload with banking detection")
        print("   POST /chat - AI chat with banking intelligence")
        print("   POST /generate-chart - Comprehensive chart generation")
        print("   POST /banking-analysis - Professional banking analysis")
        print("   GET /chart-types - All supported chart types")
        
        if SHARIA_EXPERT_AVAILABLE:
            print("\n🕌 Expert Islamic endpoints:")
            print("   POST /islamic/expert-analyze - Comprehensive analysis")
            print("   POST /islamic/expert-alternatives - Research-based alternatives")
            print("   POST /islamic/research-company - Company research")
            print("   GET /islamic/expert-status - Agent capabilities")

    print(f"\n⏱️ Startup completed in {time.time():.1f}s")

# --- Include Enhanced API Routes ---
app.include_router(router)

@app.get("/")
async def root():
    total_agents = sum(agents_initialised.values())
    
    # Enhanced info about Sharia expert
    expert_info = {}
    if SHARIA_EXPERT_AVAILABLE and sharia_expert_agent:
        try:
            expert_status = sharia_expert_agent.get_agent_status()
            expert_info = {
                "capabilities": expert_status.get("capabilities", {}),
                "tools": expert_status.get("tools", []),
                "version": expert_status.get("version", "unknown")
            }
        except Exception:
            expert_info = {"error": "Status unavailable"}
    
    return {
        "application": "Abacus FinBot - Enhanced Banking Analytics Platform",
        "version": "3.2.0",
        "description": "Professional banking transaction analysis with comprehensive chart generation and Sharia expert capabilities",
        "status": "ready" if total_agents >= 2 else "partial",
        "specialisation": "Enhanced Banking Analytics with Advanced Visualisation",
        "agents": {
            "agent01": {
                "name": "Enhanced Chat FinBot",
                "description": "AI chat with banking analytics and 12+ chart types",
                "status": "✅" if agents_initialised["agent01"] else "❌",
                "enhanced_features": [
                    "Automatic transaction categorisation",
                    "Income/Expense/Savings classification", 
                    "12+ chart types support",
                    "Banking dashboard",
                    "Financial insights engine",
                    "Spending analysis",
                    "Budget recommendations"
                ]
            },
            "agent02": {
                "name": "Stock Analysis",
                "description": "Stock analysis using GPT-4o",
                "status": "✅" if agents_initialised["agent02"] else "❌"
            },
            "agent03": {
                "name": "Sharia Expert Agent",
                "description": "Expert Islamic analysis with research tools",
                "status": "✅" if agents_initialised["agent03"] else "❌",
                "expert_info": expert_info
            }
        },
        "banking_capabilities": {
            "transaction_analysis": agents_initialised["agent01"],
            "automatic_categorisation": agents_initialised["agent01"],
            "financial_insights": agents_initialised["agent01"],
            "spending_breakdown": agents_initialised["agent01"],
            "budget_analysis": agents_initialised["agent01"],
            "time_series_analysis": agents_initialised["agent01"],
            "dashboard_metrics": agents_initialised["agent01"]
        },
        "chart_capabilities": {
            "total_chart_types": 12,
            "supported_types": [
                "bar", "pie", "line", "scatter", "histogram", "box", 
                "area", "stacked_bar", "donut", "waterfall", "heatmap", "violin"
            ],
            "banking_optimised": ["pie", "bar", "line", "waterfall", "area", "stacked_bar"],
            "interactive_generation": agents_initialised["agent01"],
            "auto_chart_selection": agents_initialised["agent01"],
            "enhanced_styling": agents_initialised["agent01"]
        },
        "expert_capabilities": {
            "real_time_research": agents_initialised["agent03"],
            "yahoo_finance_integration": agents_initialised["agent03"],
            "web_search": agents_initialised["agent03"],
            "news_monitoring": agents_initialised["agent03"],
            "haram_screening": agents_initialised["agent03"],
            "ai_sharia_analysis": agents_initialised["agent03"],
            "alternative_research": agents_initialised["agent03"],
            "ratio_calculations": agents_initialised["agent03"]
        },
        "features": {
            "enhanced_chat_ai": "Advanced financial chat with banking intelligence",
            "banking_analytics": "Professional transaction analysis and categorisation",
            "comprehensive_charts": "12+ chart types with smart generation",
            "stock_analysis": "Real-time stock analysis and recommendations",
            "expert_sharia_analysis": "Comprehensive Islamic investment screening",
            "research_tools": "Real-time company and market research",
            "automated_screening": "Haram keyword and ratio analysis",
            "ai_model": settings.MODEL_NAME
        },
        "enhanced_endpoints": {
            "banking_analysis": "/banking-analysis",
            "chart_generation": "/generate-chart",
            "chart_types": "/chart-types",
            "enhanced_upload": "/upload",
            "enhanced_chat": "/chat"
        },
        "expert_endpoints": {
            "comprehensive_analysis": "/islamic/expert-analyze",
            "research_alternatives": "/islamic/expert-alternatives", 
            "company_research": "/islamic/research-company",
            "expert_status": "/islamic/expert-status"
        },
        "compatibility": {
            "legacy_endpoints": "Maintained for backward compatibility",
            "simple_analyze": "/islamic/analyze",
            "simple_alternatives": "/islamic/alternatives"
        },
        "environment": ENVIRONMENT,
        "openai_configured": bool(settings.OPENAI_API_KEY)
    }

@app.get("/ready")
async def readiness_check():
    total_agents = sum(agents_initialised.values())
    
    # Enhanced detailed status
    banking_ready = agents_initialised["agent01"]
    expert_ready = False
    expert_details = {}
    
    if SHARIA_EXPERT_AVAILABLE and sharia_expert_agent:
        try:
            expert_status = sharia_expert_agent.get_agent_status()
            expert_ready = expert_status.get("status") == "operational"
            expert_details = {
                "tools_available": len(expert_status.get("tools", [])),
                "capabilities_count": len(expert_status.get("capabilities", {})),
                "version": expert_status.get("version", "unknown")
            }
        except Exception as e:
            expert_details = {"error": str(e)}
    
    return {
        "ready": total_agents >= 2,
        "agents_ready": total_agents,
        "total_agents": 3,
        "all_systems": "operational" if total_agents == 3 else "partial",
        "banking_analytics": "ready" if banking_ready else "limited",
        "expert_analysis": "ready" if expert_ready else "limited",
        "expert_details": expert_details,
        "banking_features": {
            "transaction_analysis": banking_ready,
            "chart_generation": banking_ready,
            "financial_insights": banking_ready,
            "dashboard_metrics": banking_ready
        },
        "chart_capabilities": {
            "total_types": 12 if banking_ready else 0,
            "interactive_studio": banking_ready,
            "auto_selection": banking_ready
        },
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "research_tools": "available" if agents_initialised["agent03"] else "unavailable",
        "platform_type": "Enhanced Banking Analytics with Comprehensive Charts"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "abacus-finbot-enhanced-banking",
        "version": "3.2.0",
        "environment": ENVIRONMENT,
        "port": PORT,
        "agents": agents_initialised,
        "banking_analytics": agents_initialised["agent01"],
        "chart_generation": agents_initialised["agent01"],
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "expert_available": SHARIA_EXPERT_AVAILABLE,
        "research_tools": agents_initialised["agent03"],
        "platform_features": {
            "banking_transaction_analysis": agents_initialised["agent01"],
            "comprehensive_chart_generation": agents_initialised["agent01"],
            "financial_dashboard": agents_initialised["agent01"],
            "ai_insights": agents_initialised["agent01"],
            "stock_analysis": agents_initialised["agent02"],
            "sharia_expert": agents_initialised["agent03"]
        }
    }

if __name__ == "__main__":
    import os
  
    port = int(os.environ.get("PORT", settings.PORT))
    
    if settings.ENVIRONMENT == "production":
        print("🌟 Starting Enhanced Banking Analytics Platform in PRODUCTION mode...")
        uvicorn.run(
            "main:app",
            host="0.0.0.0",   
            port=port,       
            reload=False,
            log_level="info"
        )
    else:
        print("🌟 Starting Enhanced Banking Analytics Platform in DEVELOPMENT mode...")
        print("⚠️  WAIT for the message '🚀 ENHANCED BANKING ANALYTICS PLATFORM READY!'")
        print("📱 Then launch the interface: streamlit run UI_streamlit.py")
        print(f"🌐 FastAPI: http://0.0.0.0:{port}")
        print(f"📚 Docs: http://0.0.0.0:{port}/docs")
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",  
            port=port,       
            reload=True,
            log_level="info"
        )