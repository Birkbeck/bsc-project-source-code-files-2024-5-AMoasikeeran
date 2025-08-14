import json
import re
import uuid
from Agent01.functions import *
from fastapi import APIRouter, HTTPException, UploadFile, Form, File, Depends, BackgroundTasks
from enum import Enum
from typing import Dict, Any, Optional, List    
from pydantic import BaseModel
import os
import random
import numpy as np
import time
import logging
import openai
from datetime import datetime, timedelta
from openai import OpenAI, OpenAIError
import io, base64
import matplotlib.pyplot as plt
import pandas as pd
import asyncio
import sys
from pathlib import Path
from pandas.api.types import (
    is_numeric_dtype,
    is_datetime64_any_dtype,
)
from sqlalchemy.orm import Session
from Database.database import get_db, User
from Database.auth import authenticate_user, validate_email, validate_name, get_current_user
from config import settings
from Agent02.direct_analysis import run_stock_analysis_direct, get_analysis_results_direct
from Agent02.tools import *

# ==================== SHARIA EXPERT AGENT IMPORT ====================
try:
    from Agent03.sharia_expert_agent import initialise_sharia_expert
    sharia_expert_agent = initialise_sharia_expert(settings.OPENAI_API_KEY, settings.MODEL_NAME)
    SHARIA_EXPERT_AVAILABLE = True
    print("✅ Routes: Sharia Expert Agent imported with research tools")
except ImportError as e:
    print(f"⚠️ Routes: Sharia Expert Agent unavailable - {e}")
    SHARIA_EXPERT_AVAILABLE = False
    sharia_expert_agent = None
except Exception as e:
    print(f"⚠️ Routes: Error initialising Sharia Expert Agent - {e}")
    SHARIA_EXPERT_AVAILABLE = False
    sharia_expert_agent = None

# ==================== STOCK ANALYSIS IMPORT ====================
try:
    STOCK_ANALYSIS_AVAILABLE = True
    print("✅ Routes: Stock analysis functions imported from Agent02")
except ImportError as e:
    print(f"⚠️ Routes: Stock functions unavailable - {e}")
    STOCK_ANALYSIS_AVAILABLE = False

# ==================== PYDANTIC MODELS ====================

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    user_name: Optional[str] = None
    user_email: Optional[str] = None

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class ContextMode(str, Enum):
    summary = "summary"
    sample  = "sample"
    full    = "full"

class SessionResponse(BaseModel):
    session_id: str

class UploadResponse(BaseModel):
    session_id: str
    summary: Dict[str, Any]

class ChatRequest(BaseModel):
    session_id: Optional[str] = None        
    message: str
    context_mode: ContextMode = ContextMode.sample

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    chart_base64: Optional[str] = None

# Models for stocks
class StockSymbolRequest(BaseModel):
    symbol: str

class StockAnalysisResponse(BaseModel):
    symbol: str
    analysis: Optional[str] = None
    recommendation: Optional[str] = None
    status: str
    message: str
    task_id: Optional[str] = None
    model_used: Optional[str] = None

class StockPriceResponse(BaseModel):
    symbol: str
    price: str
    status: str
    message: Optional[str] = None

class StockInfoResponse(BaseModel):
    symbol: str
    info: str
    status: str
    message: Optional[str] = None

# Models for Sharia Expert Analysis
class ShariaAnalysisRequest(BaseModel):
    investment_query: str

class ShariaAnalysisResponse(BaseModel):
    status: str
    investment_query: str
    islamic_status: Optional[str] = None
    expert_analysis: Optional[str] = None
    research_data: Optional[Dict[str, Any]] = None
    haram_screening: Optional[Dict[str, Any]] = None
    confidence_level: Optional[str] = None
    sources_used: Optional[list] = None
    agent_type: Optional[str] = None
    timestamp: Optional[str] = None
    message: Optional[str] = None

class ShariaAlternativesRequest(BaseModel):
    haram_investment: str

class ShariaAlternativesResponse(BaseModel):
    status: str
    haram_investment: str
    expert_alternatives: Optional[str] = None
    sector_research: Optional[Dict[str, Any]] = None
    research_based: Optional[bool] = None
    agent_type: Optional[str] = None
    timestamp: Optional[str] = None
    message: Optional[str] = None

class CompanyResearchRequest(BaseModel):
    company_name: str

class CompanyResearchResponse(BaseModel):
    status: str
    company_name: str
    research_data: Optional[Dict[str, Any]] = None
    haram_screening: Optional[Dict[str, Any]] = None
    agent_type: Optional[str] = None
    timestamp: Optional[str] = None
    message: Optional[str] = None

# ==================== SESSION MANAGEMENT ====================

SESSIONS: Dict[str, Dict[str, Any]] = {}

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    return SESSIONS.get(session_id)

def save_session(session_id: str, session_data: Dict[str, Any]) -> None:
    SESSIONS[session_id] = session_data

# ==================== STOCK ANALYSIS BACKGROUND TASKS ====================

active_stock_tasks = {}

def run_stock_analysis_background(symbol: str, task_id: str, user_id: int = None):
    """Execute stock analysis in background"""
    if not STOCK_ANALYSIS_AVAILABLE:
        active_stock_tasks[task_id] = {
            "status": "error",
            "error": "Stock analysis service unavailable"
        }
        return

    try:
        print(f"🚀 Background analysis of {symbol} (task: {task_id})")
        
        active_stock_tasks[task_id] = {
            "status": "running",
            "symbol": symbol,
            "user_id": user_id,
            "progress": "GPT-4o analysis in progress..."
        }
        
        result = run_stock_analysis_direct(symbol)
        
        if result.get("status") == "success":
            analysis_data = get_analysis_results_direct(symbol)
            
            active_stock_tasks[task_id] = {
                "status": "completed",
                "symbol": symbol,
                "user_id": user_id,
                "analysis": analysis_data.get("analysis", ""),
                "recommendation": analysis_data.get("recommendation", ""),
                "model_used": "GPT-4o",
                "completed_at": result.get("timestamp"),
                "message": f"Analysis of {symbol} completed"
            }
        else:
            active_stock_tasks[task_id] = {
                "status": "error",
                "symbol": symbol,
                "user_id": user_id,
                "error": result.get("error", "Unknown error")
            }
            
    except Exception as e:
        active_stock_tasks[task_id] = {
            "status": "error",
            "symbol": symbol,
            "user_id": user_id,
            "error": str(e)
        }

# ==================== ROUTER INITIALISATION ====================

router = APIRouter()

# ==================== CHAT AND UPLOAD ROUTES ====================

@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    session_id: str = Form(None),
):
    """Attach an Excel/CSV to an existing session (if provided) or create new."""
    if session_id and (session := get_session(session_id)):
        pass
    else:
        session_id = str(uuid.uuid4())
        session = {
            "df": None,
            "summary": {},
            "chat": [
                {"role": "system", "content": "You are FinBot, an AI financial adviser."}
            ],
        }
        save_session(session_id, session)

    try:
        raw = await file.read()
        df = read_excel_any(raw, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read file: {e}")

    summary = summarise_dataframe(df)
    session["df"] = df
    session["summary"] = summary
    save_session(session_id, session)

    return UploadResponse(session_id=session_id, summary=summary)

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Chat with FinBot + chart generation"""
    session_id = req.session_id
    session = get_session(session_id) if session_id else None

    if session is None:
        session_id = str(uuid.uuid4())
        session = {
            "df": None,
            "summary": {},
            "chat": [
                {"role": "system", "content": "You are FinBot, an AI financial adviser."}
            ],
        }
        save_session(session_id, session)

    chat_history = session["chat"]
    chat_history.append({"role": "user", "content": req.message})

    messages = chat_history.copy()
    if session["summary"]:
        messages.append({
            "role": "system",
            "content": f"spreadsheet_summary={json.dumps(session['summary'])}",
        })

    rows_df = None
    if req.context_mode == ContextMode.sample and session["df"] is not None:
        rows_df = sample_df(session["df"])
    elif req.context_mode == ContextMode.full and session["df"] is not None:
        rows_df = session["df"]
    if rows_df is not None:
        messages.append({
            "role": "system",
            "content": f"spreadsheet_rows={rows_df.to_dict(orient='records')}",
        })

    assistant_text = call_openai(messages)

    # Chart handling
    chart_base64: str | None = None
    blob = assistant_text.strip()

    if blob.startswith("```"):
        blob = re.sub(r"^```.*?\n|```$", "", blob, flags=re.DOTALL)

    m = re.search(r"(\{.*\})", blob, flags=re.DOTALL)
    if m:
        try:
            spec = json.loads(m.group(1))
            if spec.get("action") == "plot":
                if session["df"] is None:
                    raise HTTPException(status_code=400, detail="Please upload your dataset first before requesting a chart.")

                chart_base64 = make_chart(
                    session["df"],
                    spec["kind"],
                    spec.get("columns", []),
                )
                assistant_text = spec.get("title", "Here's the chart you requested:")
        except (json.JSONDecodeError, ValueError):
            pass

    chat_history.append({"role": "assistant", "content": assistant_text})
    return ChatResponse(
        answer=assistant_text,
        session_id=session_id,
        chart_base64=chart_base64,
    )

@router.post("/session", response_model=SessionResponse)
async def create_session():
    """Create a brand-new session with no spreadsheet attached."""
    session_id = str(uuid.uuid4())
    save_session(
        session_id,
        {
            "df": None,
            "summary": {},
            "chat": [
                {
                    "role": "system",
                    "content": "You are FinBot, an AI financial adviser.",
                }
            ],
        },
    )
    return SessionResponse(session_id=session_id)

# ==================== AUTHENTICATION ROUTES ====================

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login route"""
    try:
        if not validate_email(request.email):
            return LoginResponse(success=False, message="Invalid email format")
        
        if not request.password or len(request.password.strip()) < 1:
            return LoginResponse(success=False, message="Password required")
        
        user = authenticate_user(db, request.email.lower().strip(), request.password)
        
        if not user:
            return LoginResponse(success=False, message="Incorrect email or password")
        
        return LoginResponse(
            success=True,
            message="Login successful",
            user_name=user.name,
            user_email=user.email
        )
        
    except Exception as e:
        return LoginResponse(success=False, message=f"Login error: {str(e)}")

@router.post("/register", response_model=LoginResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Registration route"""
    try:
        from Database.auth import create_user
        
        user = create_user(
            db=db,
            name=request.name,
            email=request.email,
            password=request.password
        )
        
        return LoginResponse(
            success=True,
            message="Account created successfully",
            user_name=user.name,
            user_email=user.email
        )
        
    except ValueError as e:
        return LoginResponse(success=False, message=str(e))
    except Exception as e:
        return LoginResponse(success=False, message=f"Error: {str(e)}")

@router.get("/users")
async def list_users(db: Session = Depends(get_db)):
    """List users (debug)"""
    users = db.query(User).all()
    return [{"name": u.name, "email": u.email, "created_at": u.created_at} for u in users]

# ==================== STOCK ANALYSIS ROUTES ====================

@router.post("/stock/analyze-sync", response_model=StockAnalysisResponse)
async def analyse_stock_sync(
    request: StockSymbolRequest,
    db: Session = Depends(get_db)
):
    """Synchronous stock analysis (immediate result)"""
    if not STOCK_ANALYSIS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Stock analysis service unavailable"
        )
    
    try:
        symbol = request.symbol.upper().strip()
        if not symbol:
            raise HTTPException(status_code=400, detail="Stock symbol required")
        
        print(f"🔍 Synchronous analysis of {symbol}")
        
        result = await asyncio.get_event_loop().run_in_executor(
            None, run_stock_analysis_direct, symbol
        )
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=f"Analysis error: {result.get('error')}"
            )
        
        analysis_data = get_analysis_results_direct(symbol)
        
        return StockAnalysisResponse(
            symbol=symbol,
            analysis=analysis_data.get("analysis", ""),
            recommendation=analysis_data.get("recommendation", ""),
            status="success",
            message=f"GPT-4o analysis of {symbol} completed successfully",
            model_used="GPT-4o"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/stock/price", response_model=StockPriceResponse)
async def get_stock_price(request: StockSymbolRequest):
    """Real-time stock price"""
    if not STOCK_ANALYSIS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    try:
        symbol = request.symbol.upper().strip()
        if not symbol:
            raise HTTPException(status_code=400, detail="Symbol required")
        
        price_result = get_current_stock_price(symbol)
        
        if "Error" in price_result or "unavailable" in price_result:
            return StockPriceResponse(
                symbol=symbol, price=price_result, status="error",
                message=f"Unable to retrieve price for {symbol}"
            )
        
        return StockPriceResponse(
            symbol=symbol, price=price_result, status="success",
            message=f"Price retrieved for {symbol}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/stock/info", response_model=StockInfoResponse)
async def get_stock_info(request: StockSymbolRequest):
    """Detailed company information"""
    if not STOCK_ANALYSIS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    try:
        symbol = request.symbol.upper().strip()
        if not symbol:
            raise HTTPException(status_code=400, detail="Symbol required")
        
        info_result = get_company_info(symbol)
        
        if "Error" in info_result or "unavailable" in info_result:
            return StockInfoResponse(
                symbol=symbol, info=info_result, status="error",
                message=f"Unable to retrieve info for {symbol}"
            )
        
        return StockInfoResponse(
            symbol=symbol, info=info_result, status="success",
            message=f"Information retrieved for {symbol}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/stock/health")
async def stock_service_health():
    """Stock analysis service health"""
    return {
        "service": "stock_analysis",
        "status": "operational" if STOCK_ANALYSIS_AVAILABLE else "unavailable",
        "features": {
            "real_time_analysis": STOCK_ANALYSIS_AVAILABLE,
            "background_tasks": STOCK_ANALYSIS_AVAILABLE,
            "real_time_prices": STOCK_ANALYSIS_AVAILABLE,
            "company_info": STOCK_ANALYSIS_AVAILABLE,
            "model": "GPT-4o" if STOCK_ANALYSIS_AVAILABLE else "N/A"
        },
        "endpoints": {
            "/stock/analyze-sync": "Synchronous analysis",
            "/stock/price": "Real-time price",
            "/stock/info": "Company information"
        }
    }

# ==================== SHARIA EXPERT ROUTES ====================

@router.post("/islamic/expert-analyze", response_model=ShariaAnalysisResponse)
async def expert_sharia_analysis(request: ShariaAnalysisRequest):
    """
    Expert Sharia analysis with real-time research
    """
    try:
        if not SHARIA_EXPERT_AVAILABLE or not sharia_expert_agent:
            raise HTTPException(status_code=503, detail="Sharia Expert Agent not available")
        
        investment_query = request.investment_query.strip()
        if not investment_query:
            raise HTTPException(status_code=400, detail="Investment query required")
        
        print(f"🕌 Expert Sharia analysis with research tools: {investment_query}")
        
        result = await sharia_expert_agent.analyse_investment_comprehensive(investment_query)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message"))
        
        sharia_analysis = result.get("sharia_analysis", {})
        verdict = sharia_analysis.get("verdict", "QUESTIONABLE ⚠️")
        analysis_text = sharia_analysis.get("analysis_text", "Analysis not available")
        
        return ShariaAnalysisResponse(
            status="success",
            investment_query=investment_query,
            islamic_status=verdict,
            expert_analysis=analysis_text,
            research_data=result.get("research_data", {}),
            haram_screening=result.get("haram_screening", {}),
            confidence_level=sharia_analysis.get("confidence_level", "MEDIUM"),
            sources_used=sharia_analysis.get("sources_used", []),
            agent_type="Sharia Expert with Research Tools",
            timestamp=result.get("timestamp"),
            message="Analysis completed with research tools"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Expert analysis error: {str(e)}")

@router.post("/islamic/expert-alternatives", response_model=ShariaAlternativesResponse)
async def expert_halal_alternatives(request: ShariaAlternativesRequest):
    """
    Halal alternatives with expert research
    """
    try:
        if not SHARIA_EXPERT_AVAILABLE or not sharia_expert_agent:
            raise HTTPException(status_code=503, detail="Sharia Expert Agent not available")
        
        haram_investment = request.haram_investment.strip()
        if not haram_investment:
            raise HTTPException(status_code=400, detail="Investment description required")
        
        print(f"🔍 Expert search for halal alternatives: {haram_investment}")
        
        result = await sharia_expert_agent.get_halal_alternatives(haram_investment)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message"))
        
        ai_recs = result.get("ai_recommendations", {})
        recommendations = ai_recs.get("recommendations", "No alternatives found")
        
        return ShariaAlternativesResponse(
            status="success",
            haram_investment=haram_investment,
            expert_alternatives=recommendations,
            sector_research=result.get("sector_research", {}),
            research_based=True,
            agent_type="Sharia Expert with Research Tools",
            timestamp=result.get("timestamp"),
            message="Alternatives found with expert research"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Expert alternatives error: {str(e)}")

@router.post("/islamic/research-company", response_model=CompanyResearchResponse)
async def research_company_islamic(request: CompanyResearchRequest):
    """
    In-depth company research for Sharia analysis
    """
    try:
        if not SHARIA_EXPERT_AVAILABLE or not sharia_expert_agent:
            raise HTTPException(status_code=503, detail="Sharia Expert Agent not available")
        
        company_name = request.company_name.strip()
        if not company_name:
            raise HTTPException(status_code=400, detail="Company name required")
        
        print(f"🔍 Researching company for Sharia analysis: {company_name}")
        
        research_result = await sharia_expert_agent.search_company_info(company_name)
        
        haram_check = await sharia_expert_agent.check_haram_keywords(research_result)
        
        return CompanyResearchResponse(
            status="success",
            company_name=company_name,
            research_data=research_result,
            haram_screening=haram_check,
            agent_type="Sharia Expert Research Tools",
            timestamp=datetime.now().isoformat(),
            message="Research completed with expert tools"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Company research error: {str(e)}")

@router.get("/islamic/expert-status")
async def expert_agent_status():
    """
    Status of the Sharia expert agent
    """
    try:
        if not SHARIA_EXPERT_AVAILABLE or not sharia_expert_agent:
            return {
                "status": "unavailable",
                "message": "Sharia Expert Agent not initialised"
            }
        
        status = sharia_expert_agent.get_agent_status()
        return status
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Status error: {str(e)}"
        }

@router.get("/islamic/health")
async def islamic_health():
    """Islamic analysis service health check with expert capabilities"""
    try:
        if not SHARIA_EXPERT_AVAILABLE or not sharia_expert_agent:
            return {
                "service": "sharia_expert_analysis",
                "status": "unavailable",
                "error": "Sharia Expert Agent not initialised"
            }
        
        status_info = sharia_expert_agent.get_agent_status()
        
        return {
            "service": "sharia_expert_analysis",
            "status": status_info.get("status", "unknown"),
            "version": status_info.get("version", "unknown"),
            "agent_name": status_info.get("agent_name", "Sharia Expert"),
            "capabilities": status_info.get("capabilities", {}),
            "tools": status_info.get("tools", []),
            "features": {
                "real_time_research": True,
                "yahoo_finance_integration": True,
                "web_search": True,
                "news_monitoring": True,
                "haram_screening": True,
                "ai_sharia_analysis": True,
                "alternative_research": True,
                "model": status_info.get("model", "unknown")
            },
            "endpoints": {
                "/islamic/expert-analyze": "Comprehensive Sharia analysis with research",
                "/islamic/expert-alternatives": "Research-based halal alternatives",
                "/islamic/research-company": "Company research for Sharia analysis",
                "/islamic/expert-status": "Expert agent status"
            }
        }
        
    except Exception as e:
        return {
            "service": "sharia_expert_analysis", 
            "status": "error",
            "error": str(e)
        }


@router.post("/islamic/analyze", response_model=ShariaAnalysisResponse)
async def islamic_analyse_investment(request: ShariaAnalysisRequest):
    """
    Simplified Islamic analysis (redirects to expert)
    """
    return await expert_sharia_analysis(request)

@router.post("/islamic/alternatives", response_model=ShariaAlternativesResponse)
async def islamic_get_alternatives(request: ShariaAlternativesRequest):
    """
    Simplified Islamic alternatives (redirects to expert)
    """
    return await expert_halal_alternatives(request)

@router.get("/islamic/status")
async def islamic_status():
    """
    Islamic status (redirects to expert)
    """
    return await expert_agent_status()

# ==================== GLOBAL HEALTH ROUTE ====================

@router.get("/health/all")
async def health_all_services():
    """Health check for all services"""
    try:
        # Check each service
        stock_health = {"status": "operational" if STOCK_ANALYSIS_AVAILABLE else "unavailable", "service": "Agent02"}
        
        # Check Sharia Expert
        if SHARIA_EXPERT_AVAILABLE and sharia_expert_agent:
            try:
                expert_status = sharia_expert_agent.get_agent_status()
                expert_health = {"status": "operational", "service": "Agent03_Expert"}
            except Exception:
                expert_health = {"status": "error", "service": "Agent03_Expert"}
        else:
            expert_health = {"status": "unavailable", "service": "Agent03_Expert"}
        
        total_operational = sum([
            1,  # Agent01 always operational (chat)
            1 if STOCK_ANALYSIS_AVAILABLE else 0,
            1 if expert_health["status"] == "operational" else 0
        ])
        
        return {
            "global_status": "operational" if total_operational >= 2 else "partial",
            "services": {
                "chat_finbot": {"status": "operational", "service": "Agent01"},
                "stock_analysis": stock_health,
                "sharia_expert": expert_health
            },
            "total_agents": 3,
            "operational_agents": total_operational,
            "version": "3.0.0",
            "features": {
                "chat_ai": True,
                "file_upload": True,
                "stock_analysis": STOCK_ANALYSIS_AVAILABLE,
                "sharia_expert_analysis": SHARIA_EXPERT_AVAILABLE,
                "real_time_research": SHARIA_EXPERT_AVAILABLE,
                "authentication": True
            },
            "expert_capabilities": {
                "yahoo_finance": SHARIA_EXPERT_AVAILABLE,
                "web_search": SHARIA_EXPERT_AVAILABLE,
                "news_monitoring": SHARIA_EXPERT_AVAILABLE,
                "haram_screening": SHARIA_EXPERT_AVAILABLE,
                "ai_analysis": SHARIA_EXPERT_AVAILABLE
            } if SHARIA_EXPERT_AVAILABLE else {},
            "model": settings.MODEL_NAME,
            "openai_configured": bool(settings.OPENAI_API_KEY)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Global health error: {str(e)}")
    
class ChartRequest(BaseModel):
    chart_type: str  # bar, line, pie, scatter, histogram, box, violin, heatmap, area, donut
    columns: List[str]
    title: Optional[str] = ""
    interactive: bool = True
    data: Optional[List[Dict[str, Any]]] = None

class ChartSuggestionRequest(BaseModel):
    columns: List[str]

class DashboardRequest(BaseModel):
    file_id: Optional[str] = None

class VisualisationRequest(BaseModel):
    user_prompt: str
    file_id: Optional[str] = None
    chart_preferences: Optional[Dict[str, Any]] = None


@router.post("/finbot/create-chart")
async def create_chart_endpoint(request: ChartRequest):
    try:
        if request.data:
            df = pd.DataFrame(request.data)
        else:
            import numpy as np
            df = pd.DataFrame({
                'category': ['Groceries', 'Transport', 'Entertainment', 'Utilities', 'Healthcare'],
                'amount': [1200, 800, 600, 400, 300],
                'date': pd.date_range('2023-01-01', periods=5),
                'merchant': ['Store A', 'Gas Station', 'Cinema', 'Electric Co', 'Hospital']
            })
        if request.interactive:
            chart_result = create_interactive_chart(
                df, 
                request.chart_type, 
                request.columns, 
                request.title
            )
            result_data = json.loads(chart_result)
            if isinstance(result_data, dict) and result_data.get("action") == "error":
                raise HTTPException(status_code=400, detail=result_data.get("message"))
            return {
                "success": True,
                "chart_type": request.chart_type,
                "interactive": True,
                "chart_data": result_data
            }
        else:
            chart_base64 = make_chart(
                df, 
                request.chart_type, 
                request.columns, 
                request.title,
                interactive=False
            )
            try:
                error_data = json.loads(chart_base64)
                if error_data.get("action") == "error":
                    raise HTTPException(status_code=400, detail=error_data.get("message"))
            except json.JSONDecodeError:
                pass  
            
            return {
                "success": True,
                "chart_type": request.chart_type,
                "interactive": False,
                "chart_image": chart_base64
            }
            
    except Exception as e:
        logger.error(f"Error creating chart: {e}")
        raise HTTPException(status_code=500, detail=f"Chart creation failed: {str(e)}")

@router.post("/finbot/suggest-chart")
async def suggest_chart_endpoint(request: ChartSuggestionRequest):
    """
    Suggests the best chart type based on selected columns.
    """
    try:
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=100),
            'amount': range(100),
            'category': ['A', 'B', 'C'] * 33 + ['A'],
            'balance': [1000 + i*10 for i in range(100)]
        })
        
        suggested_type = suggest_chart_type(df, request.columns)
        
        return {
            "success": True,
            "suggested_chart_type": suggested_type,
            "columns": request.columns,
            "reasoning": f"Based on the data characteristics, {suggested_type} chart is most suitable"
        }
        
    except Exception as e:
        logger.error(f"Error suggesting chart: {e}")
        raise HTTPException(status_code=500, detail=f"Chart suggestion failed: {str(e)}")

@router.post("/finbot/dashboard-data")
async def get_dashboard_data(request: DashboardRequest):
    """
    Generates complete data for a dashboard with chart suggestions.
    """
    try:
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=100),
            'amount': range(100),
            'category': ['Groceries', 'Transport', 'Entertainment'] * 33 + ['Groceries'],
            'merchant': ['Store A', 'Store B', 'Store C'] * 33 + ['Store A'],
            'balance': [1000 + i*10 for i in range(100)]
        })
        
        dashboard_data = create_dashboard_data(df)
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "data_preview": df.head(10).to_dict('records')
        }
        
    except Exception as e:
        logger.error(f"Error creating dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard creation failed: {str(e)}")

@router.post("/finbot/smart-visualisation")
async def smart_visualisation(request: VisualisationRequest):
    """
    Uses AI to interpret user request and create appropriate visualisation.
    """
    try:
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=100),
            'amount': [1000 + i*10 + (i%10)*50 for i in range(100)],
            'category': ['Groceries', 'Transport', 'Entertainment', 'Utilities', 'Healthcare'] * 20,
            'merchant': ['Store A', 'Store B', 'Store C', 'Store D', 'Store E'] * 20,
            'balance': [5000 + i*25 for i in range(100)]
        })
        df_summary = df.describe().to_string()
        columns_info = f"Available columns: {list(df.columns)}"
        ai_prompt = f"""
        User request: {request.user_prompt}
        
        Data context:
        {columns_info}
        
        Data summary:
        {df_summary}
        
        Please analyse the user's request and return ONLY a JSON response with the following structure:
        {{
            "action": "plot",
            "kind": "bar|line|pie|scatter|histogram|box|violin|heatmap|area|donut",
            "columns": ["column1", "column2"],
            "title": "Chart title",
            "interactive": true,
            "data": []
        }}
        
        Choose the most appropriate chart type and columns based on the user's request.
        If the request is not about creating a chart, respond with explanatory text instead.
        """
        
        ai_response = call_openai([{"role": "user", "content": ai_prompt}])
        
        try:
            chart_config = json.loads(ai_response)
            
            if chart_config.get("action") == "plot":
                chart_result = create_interactive_chart(
                    df,
                    chart_config.get("kind", "bar"),
                    chart_config.get("columns", []),
                    chart_config.get("title", "")
                )
                try:
                    result_data = json.loads(chart_result)
                    if isinstance(result_data, dict) and result_data.get("action") == "error":
                        raise HTTPException(status_code=400, detail=result_data.get("message"))
                    
                    return {
                        "success": True,
                        "user_request": request.user_prompt,
                        "ai_interpretation": chart_config,
                        "chart_data": result_data
                    }
                except json.JSONDecodeError:
                    return {
                        "success": True,
                        "user_request": request.user_prompt,
                        "ai_interpretation": chart_config,
                        "chart_data": json.loads(chart_result)
                    }
            else:
                return {
                    "success": True,
                    "user_request": request.user_prompt,
                    "ai_response": ai_response,
                    "chart_data": None
                }
                
        except json.JSONDecodeError:
            return {
                "success": True,
                "user_request": request.user_prompt,
                "ai_response": ai_response,
                "chart_data": None
            }
            
    except Exception as e:
        logger.error(f"Error in smart visualisation: {e}")
        raise HTTPException(status_code=500, detail=f"Smart visualisation failed: {str(e)}")

@router.post("/finbot/upload-and-visualise")
async def upload_and_visualise(
    file: UploadFile = File(...),
    chart_type: str = Form("auto"),
    columns: str = Form(""),
    interactive: bool = Form(True)
):
    """
    Upload a file and immediately create a visualisation.
    """
    try:
        file_content = await file.read()
        df = read_excel_any(file_content, file.filename)
        selected_columns = [col.strip() for col in columns.split(",") if col.strip()] if columns else []
        
        if chart_type == "auto":
            if not selected_columns:
                cats = [col for col in df.columns if not df[col].dtype in ['float64', 'int64']]
                nums = [col for col in df.columns if df[col].dtype in ['float64', 'int64']]
                selected_columns = (cats[:1] + nums[:1]) if cats and nums else list(df.columns[:2])
            
            chart_type = suggest_chart_type(df, selected_columns)
        if len(df) > 1000:
            df = sample_df(df)
        if interactive:
            chart_result = create_interactive_chart(df, chart_type, selected_columns, f"Analysis of {file.filename}")
            
            try:
                result_data = json.loads(chart_result)
                if isinstance(result_data, dict) and result_data.get("action") == "error":
                    raise HTTPException(status_code=400, detail=result_data.get("message"))
                
                return {
                    "success": True,
                    "filename": file.filename,
                    "chart_type": chart_type,
                    "columns": selected_columns,
                    "interactive": True,
                    "chart_data": result_data,
                    "data_summary": {
                        "rows": len(df),
                        "columns": len(df.columns),
                        "column_names": list(df.columns)
                    }
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "filename": file.filename,
                    "chart_type": chart_type,
                    "columns": selected_columns,
                    "interactive": True,
                    "chart_data": json.loads(chart_result),
                    "data_summary": {
                        "rows": len(df),
                        "columns": len(df.columns),
                        "column_names": list(df.columns)
                    }
                }
        else:
            chart_base64 = make_chart(df, chart_type, selected_columns, f"Analysis of {file.filename}", interactive=False)
            
            try:
                error_data = json.loads(chart_base64)
                if error_data.get("action") == "error":
                    raise HTTPException(status_code=400, detail=error_data.get("message"))
            except json.JSONDecodeError:
                pass  
            
            return {
                "success": True,
                "filename": file.filename,
                "chart_type": chart_type,
                "columns": selected_columns,
                "interactive": False,
                "chart_image": chart_base64,
                "data_summary": {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": list(df.columns)
                }
            }
            
    except Exception as e:
        logger.error(f"Error in upload and visualise: {e}")
        raise HTTPException(status_code=500, detail=f"Upload and visualisation failed: {str(e)}")

@router.get("/finbot/chart-types")
async def get_available_chart_types():
    """
    Returns the list of all available chart types with their descriptions.
    """
    chart_types = {
        "bar": {
            "name": "Bar Chart",
            "description": "Perfect for comparing categories or showing distribution",
            "best_for": ["categorical data", "comparisons", "rankings"],
            "data_requirements": "1 categorical + 1 numeric column"
        },
        "line": {
            "name": "Line Chart", 
            "description": "Ideal for showing trends over time or continuous data",
            "best_for": ["time series", "trends", "continuous data"],
            "data_requirements": "1 date/numeric + 1 numeric column"
        },
        "pie": {
            "name": "Pie Chart",
            "description": "Shows proportions and percentages of a whole",
            "best_for": ["proportions", "percentages", "parts of whole"],
            "data_requirements": "1 categorical + 1 numeric column"
        },
        "donut": {
            "name": "Donut Chart",
            "description": "Like pie chart but with a hole in the centre",
            "best_for": ["proportions", "percentages", "modern styling"],
            "data_requirements": "1 categorical + 1 numeric column"
        },
        "scatter": {
            "name": "Scatter Plot",
            "description": "Shows correlation between two numeric variables",
            "best_for": ["correlations", "relationships", "outliers"],
            "data_requirements": "2 numeric columns"
        },
        "histogram": {
            "name": "Histogram",
            "description": "Shows distribution of a single numeric variable",
            "best_for": ["distributions", "frequency analysis"],
            "data_requirements": "1 numeric column"
        },
        "box": {
            "name": "Box Plot",
            "description": "Shows statistical summary and outliers",
            "best_for": ["statistical analysis", "outlier detection", "comparing distributions"],
            "data_requirements": "1 numeric column, optional categorical"
        },
        "violin": {
            "name": "Violin Plot",
            "description": "Shows distribution shape and density",
            "best_for": ["distribution analysis", "density visualisation"],
            "data_requirements": "1 numeric column, optional categorical"
        },
        "heatmap": {
            "name": "Heatmap",
            "description": "Shows correlation matrix or 2D data intensity",
            "best_for": ["correlations", "patterns in 2D data"],
            "data_requirements": "Multiple numeric columns"
        },
        "area": {
            "name": "Area Chart",
            "description": "Like line chart but with filled area underneath",
            "best_for": ["cumulative data", "volume over time"],
            "data_requirements": "1 date/numeric + 1 numeric column"
        }
    }
    
    return {
        "success": True,
        "chart_types": chart_types,
        "total_types": len(chart_types)
    }

@router.get("/finbot/test-visualisation")
async def test_visualisation():
    """
    Test route to verify that visualisations work.
    """
    try:
        import numpy as np
        df = pd.DataFrame({
            'category': ['Groceries', 'Transport', 'Entertainment', 'Utilities', 'Healthcare'],
            'amount': [1200, 800, 600, 400, 300],
            'date': pd.date_range('2023-01-01', periods=5),
            'percentage': [40, 27, 20, 13, 10]
        })
        test_results = {}
        bar_chart = create_interactive_chart(df, "bar", ["category", "amount"], "Test Bar Chart")
        test_results["bar_chart"] = {"status": "success" if not "error" in bar_chart else "error"}
        
        pie_chart = create_interactive_chart(df, "pie", ["category", "amount"], "Test Pie Chart")
        test_results["pie_chart"] = {"status": "success" if not "error" in pie_chart else "error"}
        
        line_chart = create_interactive_chart(df, "line", ["date", "amount"], "Test Line Chart")
        test_results["line_chart"] = {"status": "success" if not "error" in line_chart else "error"}
        
        return {
            "success": True,
            "message": "Visualisation test completed",
            "test_results": test_results,
            "data_used": df.to_dict('records')
        }
        
    except Exception as e:
        logger.error(f"Error in visualisation test: {e}")
        return {
            "success": False,
            "message": f"Visualisation test failed: {str(e)}"
        }