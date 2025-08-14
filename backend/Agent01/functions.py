import re
import pandas as pd
import os
import io
import random
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import numpy as np
from pandas.api.types import (
    is_numeric_dtype,
    is_datetime64_any_dtype,
)
from config import settings
import logging
import time
import json
from datetime import datetime
from openai import OpenAI, OpenAIError
import openai

# --- Globals & Configuration ---
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("finbot")
from config import settings

# Configure OpenAI client with timeout and retry settings
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    timeout=60.0,  # 60 second timeout
    max_retries=3  # Built-in retry mechanism
)


plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

SYSTEM_PROMPT = (
    # System prompt for OpenAI agent
    "You are Abacus, an AI financial adviser and data visualisation expert."
    "If a user ever asks for any advice or suggestions, make sure to assist and guide them properly."
    "Always express monetary values in UK pounds sterling (symbol '£', code 'GBP')."
    "If the source data uses another currency, first convert amounts approximately to GBP and mention the assumed rate in parentheses."
    "Never display any currency symbol other than £."
    "◆ **Transaction cleansing & categorisation**\n"
    "  1. Trim whitespace, drop emojis, fix double-spaces, make merchant/payee lower-case for matching.\n"
    "     • Groceries  • Utilities  • Housing  • Transport  • Health\n"
    "     • Dining & Entertainment  • Subscriptions  • Education  • Income\n"
    "     • Transfers  • Other\n"
    "  3. If a transaction is truly ambiguous, label it 'Uncategorised' and flag it.\n\n"
    "◆ **Visualisation capabilities**\n"
    "  • Support for all chart types: bar, line, pie, scatter, histogram, box, violin, heatmap, area, donut\n"
    "  • Interactive charts using Plotly for web display\n"
    "  • Static charts using Matplotlib/Seaborn for reports\n"
    "  • Automatic chart type selection based on data characteristics\n"
    "  • Multi-series and comparison visualisations\n\n"
    "◆ **Aggregation guidance**\n"
    "  • Whenever the user asks for a *summary*, *spending*, or *break-down*, "
    "aggregate totals by category **and** by any date range mentioned (inclusive).\n"
    "  • Respond with a Markdown table: | Category | Total £ | % of total |, sorted by highest spend.\n"
    "  • Provide short insights: which 3 categories dominate, any unusual spikes, etc.\n\n"
    "◆ **Data cleansing for charts**\n"
    "  • Before plotting, drop rows where either column is null, non-numeric, or negative.\n"
    "  • Clamp any value outside the 1st–99th percentile to the nearest boundary and flag it.\n"
    "  • Round all numeric values to two decimal places.\n"
    "  • If fewer than 3 valid data points remain, output:\n"
    "      { \"action\": \"error\", \"message\": \"Not enough valid data to plot.\" }\n\n"
    "◆ Column-picking rule\n"
    "  • If the user asks for a chart of *spending*, *expenses*, *income*, or similar "
    "and supplies only categorical columns, automatically choose the most suitable "
    "numeric column:\n"
    "      1. Prefer any column whose name contains 'amount', 'total', 'cost', "
    "         'value', 'balance', or 'price' (case-insensitive).\n"
    "      2. Otherwise pick the numeric column with the largest absolute sum.\n"
    "  • Include that numeric column in the JSON you return so the backend can "
    "    aggregate the data correctly.\n\n"
    "---\n"
    "When the user explicitly asks for a chart, respond **only** with this JSON (no extra words, no Markdown):\n"
    "{\n"
    "  \"action\":  \"plot\",\n"
    "  \"kind\":    \"bar | pie | line | scatter | histogram | box | violin | heatmap | area | donut\",\n"
    "  \"columns\": [\"ColA\", \"ColB\"],\n"
    "  \"title\":   \"Optional title\",\n"
    "  \"interactive\": true/false,\n"
    "  \"data\":    [ {\"ColA\": value1, \"ColB\": value2}, … ]\n"
    "}\n"
    "Do **not** wrap the JSON in back-ticks.\n\n"
    f"Reply in clear, friendly language. current date and time {now}"
)

_CURRENCY_RE = re.compile(r"[^\d.,\-]")
_MONEY_RE = re.compile(r"(amount|cost|price|total|value|balance|paid|spend|debit|credit)", re.I)

# --- Data Cleansing Utilities ---
def coerce_numeric(col: pd.Series) -> pd.Series:
    """Try VERY HARD to turn a column into floats."""
    if pd.api.types.is_numeric_dtype(col):
        return col
    if pd.api.types.is_datetime64_any_dtype(col):
        return col
    if pd.api.types.is_bool_dtype(col):
        return col.astype("int64")
    if col.dtype == "object":
        cleansed = (
            col.astype(str)
               .str.replace(_CURRENCY_RE, "", regex=True)
               .str.replace(",", "")
        )
        nums = pd.to_numeric(cleansed, errors="coerce")
        if nums.notna().mean() >= 0.10:
            return nums
    return col

def read_excel_any(data: bytes, filename: str) -> pd.DataFrame:
    """Read any Excel or CSV file and coerce columns to numeric if possible."""
    ext = os.path.splitext(filename)[-1].lower()
    if ext == ".csv":
        try:
            return pd.read_csv(io.BytesIO(data))
        except UnicodeDecodeError:
            return pd.read_csv(io.BytesIO(data), encoding="latin-1")
    engine_hint = {
        ".xlsx": "openpyxl",
        ".xls":  "xlrd",
        ".xlsm": "openpyxl",
        ".ods":  "odf",
    }.get(ext)
    df = pd.read_excel(io.BytesIO(data), engine=engine_hint)
    df = df.apply(coerce_numeric)
    return df

# --- DataFrame Summary & Sampling ---
def summarise_dataframe(df: pd.DataFrame) -> dict:
    """Return summary statistics for a DataFrame."""
    summary = {
        "num_rows": int(df.shape[0]),
        "num_columns": int(df.shape[1]),
        "columns": [],
    }
    for col in df.columns:
        s = df[col]
        info = {
            "name": str(col),
            "dtype": str(s.dtype),
            "nulls": int(s.isna().sum()),
        }
        if pd.api.types.is_numeric_dtype(s):
            nums = pd.to_numeric(s, errors="coerce")
            info.update(
                minimum=float(nums.min()),
                maximum=float(nums.max()),
                mean=float(nums.mean()),
                sum=float(nums.sum()),
            )
        else:
            top = s.value_counts(dropna=True).head(5).to_dict()
            info["top_values"] = {str(k): int(v) for k, v in top.items()}
        summary["columns"].append(info)
    return summary

def sample_df(df: pd.DataFrame) -> pd.DataFrame:
    """Return a random sample of the DataFrame within configured row limits."""
    n = max(settings.SAMPLE_MIN_ROWS,
            min(settings.SAMPLE_MAX_ROWS, len(df)))
    if len(df) <= n:
        return df
    random.seed(42)
    return df.iloc[random.sample(range(len(df)), n)]

# --- OpenAI API Utilities ---
def _with_system_prompt(messages: list[dict]) -> list[dict]:
    """Ensure SYSTEM_PROMPT is the first message exactly once."""
    if not messages or SYSTEM_PROMPT not in messages[0].get("content", ""):
        return [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    return messages

def call_openai(messages: list[dict]) -> str:
    """Wrapper that injects the system prompt and returns the assistant's reply."""
    prepared = _with_system_prompt(messages)
    
    # Check if API key is available
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.strip() == "":
        logger.error("OpenAI API key not configured")
        raise RuntimeError("OpenAI API key not configured")
    
    for attempt in range(4):
        try:
            logger.info(f"OpenAI API call attempt {attempt + 1}/4")
            logger.info("Prompt sent to OpenAI:\n%s", json.dumps(prepared, indent=2, ensure_ascii=False))
            
            resp = client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=prepared,
                temperature=0.3,
                timeout=60  # Explicit timeout per request
            )
            logger.info("OpenAI API call successful")
            return resp.choices[0].message.content
            
        except Exception as e:
            error_msg = f"OpenAI error (attempt {attempt + 1}): {str(e)}"
            logger.error(error_msg)
            
            # Check specific error types
            if "api_key" in str(e).lower() or "authentication" in str(e).lower():
                logger.error("API key authentication failed")
                raise RuntimeError("OpenAI API key authentication failed")
            
            if attempt < 3:  # Don't sleep on the last attempt
                sleep_time = 2 ** attempt
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
    
    logger.error("All OpenAI API retry attempts failed")
    raise RuntimeError("OpenAI API failure after retries")

# --- DataFrame Column Utilities ---
def _split_cols(df: pd.DataFrame, cols: list[str]) -> tuple[list[str], list[str]]:
    """Return (categoricals, numerics) preserving user order."""
    cats, nums = [], []
    for c in cols:
        if c not in df.columns:
            continue
        (nums if is_numeric_dtype(df[c]) else cats).append(c)
    return cats, nums

def _all_numeric(df: pd.DataFrame) -> list[str]:
    """Return all numeric columns in the DataFrame."""
    return [c for c in df.columns if is_numeric_dtype(df[c])]

def _best_numeric(df: pd.DataFrame) -> str | None:
    """Pick the most likely 'money' column or the numeric with largest movement."""
    nums = _all_numeric(df)
    if not nums:
        return None
    for c in nums:
        if _MONEY_RE.search(c):
            return c
    return max(nums, key=lambda c: df[c].abs().sum())

# --- Chart Data Cleansing ---
def _cleanse_chart_data(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Cleanse chart data: drop nulls, clamp outliers, round, remove negatives."""
    df = df.dropna(subset=cols)
    for c in cols:
        if c not in df.columns or not is_numeric_dtype(df[c]):
            continue
        lower = df[c].quantile(0.01)
        upper = df[c].quantile(0.99)
        df[c] = df[c].clip(lower, upper).round(2)
        if c.lower() in ['amount', 'balance', 'profit', 'loss']:
            continue  
    return df

# --- Enhanced Chart Creation ---
def create_interactive_chart(df: pd.DataFrame, kind: str, columns: list[str], title: str = "") -> str:
    """Create interactive charts using Plotly and return as JSON."""
    cols = [c for c in columns if c in df.columns]
    if not cols:
        raise ValueError(f"No valid columns amongst {columns}")

    df = _cleanse_chart_data(df, cols)
    if len(df) < 3:
        return json.dumps({"action": "error", "message": "Not enough valid data to plot."})

    cats, nums = _split_cols(df, cols)
    
    try:
        fig = None
        
        if kind == "bar":
            if cats and nums:
                gb = df.groupby(cats[0])[nums[0]].sum().reset_index()
                fig = px.bar(gb, x=cats[0], y=nums[0], title=title or f"Bar Chart: {nums[0]} by {cats[0]}")
            elif nums:
                fig = px.bar(df, y=nums[0], title=title or f"Bar Chart: {nums[0]}")
                
        elif kind == "line":
            if cats and nums:
                if is_datetime64_any_dtype(df[cats[0]]):
                    fig = px.line(df, x=cats[0], y=nums[0], title=title or f"Line Chart: {nums[0]} over time")
                else:
                    gb = df.groupby(cats[0])[nums[0]].sum().reset_index()
                    fig = px.line(gb, x=cats[0], y=nums[0], title=title or f"Line Chart: {nums[0]} by {cats[0]}")
            elif nums:
                fig = px.line(df, y=nums[0], title=title or f"Line Chart: {nums[0]}")
                
        elif kind == "pie":
            if cats and nums:
                gb = df.groupby(cats[0])[nums[0]].sum().reset_index()
                gb = gb[gb[nums[0]] > 0] 
                fig = px.pie(gb, values=nums[0], names=cats[0], title=title or f"Pie Chart: {nums[0]} by {cats[0]}")
            elif cats:
                vc = df[cats[0]].value_counts().reset_index()
                fig = px.pie(vc, values='count', names=cats[0], title=title or f"Distribution: {cats[0]}")
                
        elif kind == "scatter":
            if len(nums) >= 2:
                colour_col = cats[0] if cats else None
                fig = px.scatter(df, x=nums[0], y=nums[1], color=colour_col, 
                               title=title or f"Scatter: {nums[1]} vs {nums[0]}")
            elif cats and nums:
                fig = px.scatter(df, x=cats[0], y=nums[0], title=title or f"Scatter: {nums[0]} by {cats[0]}")
                
        elif kind == "histogram":
            if nums:
                fig = px.histogram(df, x=nums[0], title=title or f"Histogram: {nums[0]}")
                
        elif kind == "box":
            if cats and nums:
                fig = px.box(df, x=cats[0], y=nums[0], title=title or f"Box Plot: {nums[0]} by {cats[0]}")
            elif nums:
                fig = px.box(df, y=nums[0], title=title or f"Box Plot: {nums[0]}")
                
        elif kind == "violin":
            if cats and nums:
                fig = px.violin(df, x=cats[0], y=nums[0], title=title or f"Violin Plot: {nums[0]} by {cats[0]}")
            elif nums:
                fig = px.violin(df, y=nums[0], title=title or f"Violin Plot: {nums[0]}")
                
        elif kind == "heatmap":
            if len(nums) >= 2:
                correlation_data = df[nums].corr()
                fig = px.imshow(correlation_data, text_auto=True, title=title or "Correlation Heatmap")
                
        elif kind == "area":
            if cats and nums:
                if is_datetime64_any_dtype(df[cats[0]]):
                    fig = px.area(df, x=cats[0], y=nums[0], title=title or f"Area Chart: {nums[0]} over time")
                else:
                    gb = df.groupby(cats[0])[nums[0]].sum().reset_index()
                    fig = px.area(gb, x=cats[0], y=nums[0], title=title or f"Area Chart: {nums[0]} by {cats[0]}")
                    
        elif kind == "donut":
            if cats and nums:
                gb = df.groupby(cats[0])[nums[0]].sum().reset_index()
                gb = gb[gb[nums[0]] > 0]
                fig = px.pie(gb, values=nums[0], names=cats[0], title=title or f"Donut Chart: {nums[0]} by {cats[0]}")
                fig.update_traces(hole=.3)
            elif cats:
                vc = df[cats[0]].value_counts().reset_index()
                fig = px.pie(vc, values='count', names=cats[0], title=title or f"Donut Distribution: {cats[0]}")
                fig.update_traces(hole=.3)
        
        if fig is None:
            return json.dumps({"action": "error", "message": f"Cannot create {kind} chart with provided data."})
            
        # Configure layout
        fig.update_layout(
            showlegend=True,
            template="plotly_white",
            font=dict(size=12),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
        
    except Exception as e:
        logger.error(f"Error creating interactive chart: {e}")
        return json.dumps({"action": "error", "message": f"Chart creation failed: {str(e)}"})

def make_chart(df: pd.DataFrame, kind: str, columns: list[str], prompt: str = "", interactive: bool = False) -> str:
    """
    Create a chart and return it base-64 encoded (static) or as JSON (interactive).
    Cleanses data before plotting. Returns error JSON if not enough valid data.
    """
    if interactive:
        return create_interactive_chart(df, kind, columns, prompt)
    
    cols = [c for c in columns if c in df.columns]
    if not cols:
        raise ValueError(f"No valid columns amongst {columns}")

    df = _cleanse_chart_data(df, cols)
    if len(df) < 3:
        return json.dumps({"action": "error", "message": "Not enough valid data to plot."})

    fig, ax = plt.subplots(figsize=(12, 8))
    cats, nums = _split_cols(df, cols)

    try:
        # --- Bar Chart ---
        if kind == "bar":
            if cats and len(cats) > 0 and is_datetime64_any_dtype(df[cats[0]]):
                plot_df = df.set_index(cats[0])[nums or _all_numeric(df)]
                plot_df.plot(kind=kind, ax=ax)
            elif cats and nums:
                gb = df.groupby(cats[0])[nums].sum()
                gb.plot(kind=kind, ax=ax)
            elif not nums and cats:
                maybe = _best_numeric(df)
                if maybe:
                    series = df.groupby(cats[0])[maybe].sum()
                    series.plot(kind=kind, ax=ax)
                    nums = [maybe]
                else:
                    df[cats[0]].value_counts().plot(kind="bar", ax=ax)
            elif nums:
                df[nums].plot(kind=kind, ax=ax)

        # --- Line Chart ---
        elif kind == "line":
            if cats and len(cats) > 0 and is_datetime64_any_dtype(df[cats[0]]):
                plot_df = df.set_index(cats[0])[nums or _all_numeric(df)]
                plot_df.plot(kind=kind, ax=ax, marker='o')
            elif cats and nums:
                gb = df.groupby(cats[0])[nums].sum()
                gb.plot(kind=kind, ax=ax, marker='o')
            elif nums:
                df[nums].plot(kind=kind, ax=ax, marker='o')

        # --- Pie Chart ---
        elif kind == "pie":
            if cats and not nums:
                best_num = _best_numeric(df)
                nums = [best_num] if best_num else []
            if cats and nums:
                series = df.groupby(cats[0])[nums[0]].sum()
            elif cats:
                series = df[cats[0]].value_counts()
            elif nums:
                series = df[nums[0]].value_counts()
            else:
                return json.dumps({"action": "error", "message": "Not enough valid data to plot."})

            # Handle negatives for spending/expense/outflow
            if any(w in prompt.lower() for w in ("spend", "expense", "outflow")):
                series = series[series < 0]
            if (series < 0).all():
                series = -series
            elif (series < 0).any():
                series = series.abs()
            series = series[series != 0]
            if len(series) < 3:
                return json.dumps({"action": "error", "message": "Not enough valid data to plot."})
            series.plot(kind="pie", autopct="%1.1f%%", ax=ax)

        # --- Scatter Plot ---
        elif kind == "scatter":
            if len(nums) >= 2:
                ax.scatter(df[nums[0]], df[nums[1]], alpha=0.6)
                ax.set_xlabel(nums[0])
                ax.set_ylabel(nums[1])
            else:
                return json.dumps({"action": "error", "message": "Scatter plot requires at least 2 numeric columns."})

        # --- Histogram ---
        elif kind == "histogram":
            if nums:
                df[nums[0]].plot(kind="hist", ax=ax, bins=20, alpha=0.7)
            else:
                return json.dumps({"action": "error", "message": "Histogram requires numeric data."})

        # --- Box Plot ---
        elif kind == "box":
            if cats and nums:
                df.boxplot(column=nums[0], by=cats[0], ax=ax)
            elif nums:
                df[nums].plot(kind="box", ax=ax)
            else:
                return json.dumps({"action": "error", "message": "Box plot requires numeric data."})

        # --- Area Chart ---
        elif kind == "area":
            if cats and len(cats) > 0 and is_datetime64_any_dtype(df[cats[0]]):
                plot_df = df.set_index(cats[0])[nums or _all_numeric(df)]
                plot_df.plot(kind="area", ax=ax, alpha=0.7)
            elif cats and nums:
                gb = df.groupby(cats[0])[nums].sum()
                gb.plot(kind="area", ax=ax, alpha=0.7)
            elif nums:
                df[nums].plot(kind="area", ax=ax, alpha=0.7)

        else:
            return json.dumps({"action": "error", "message": f"Unsupported chart type: {kind}"})

        # Styling
        ax.set_title(f"{kind.title()} Chart – {', '.join(cols or nums)}", fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save to base64
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        return base64.b64encode(buf.getvalue()).decode()

    except Exception as e:
        plt.close(fig)
        logger.error(f"Error creating chart: {e}")
        return json.dumps({"action": "error", "message": f"Chart creation failed: {str(e)}"})

# --- Advanced Visualisation Functions ---
def suggest_chart_type(df: pd.DataFrame, columns: list[str]) -> str:
    """Suggest the best chart type based on data characteristics."""
    cats, nums = _split_cols(df, columns)
    
    # Time series data
    if cats and is_datetime64_any_dtype(df[cats[0]]):
        return "line"
    
    # Categorical with numeric - distribution
    if len(cats) == 1 and len(nums) == 1:
        unique_cats = df[cats[0]].nunique()
        if unique_cats <= 10:
            return "pie" if unique_cats <= 6 else "bar"
        else:
            return "bar"
    
    # Two numeric columns - correlation
    if len(nums) >= 2:
        return "scatter"
    
    # Single numeric - distribution
    if len(nums) == 1 and not cats:
        return "histogram"
    
    # Default
    return "bar"

def create_dashboard_data(df: pd.DataFrame) -> dict:
    """Create comprehensive dashboard data for the frontend."""
    summary = summarise_dataframe(df)
    
    dashboard = {
        "summary": summary,
        "suggested_charts": [],
        "available_chart_types": [
            "bar", "line", "pie", "scatter", "histogram", 
            "box", "violin", "heatmap", "area", "donut"
        ]
    }
    
    # Suggest charts based on data
    cats = [col for col in df.columns if not is_numeric_dtype(df[col])]
    nums = [col for col in df.columns if is_numeric_dtype(df[col])]
    
    if cats and nums:
        for cat in cats[:3]:  # Top 3 categorical columns
            for num in nums[:2]:  # Top 2 numeric columns
                suggested_type = suggest_chart_type(df, [cat, num])
                dashboard["suggested_charts"].append({
                    "type": suggested_type,
                    "columns": [cat, num],
                    "title": f"{num} by {cat}",
                    "description": f"Shows {num} distributed across {cat}"
                })
    
    return dashboard