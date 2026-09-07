"""
APIx-India Backend API (main.py)
Principal Econometric & High-Frequency Airfare Index Service
Serving MoSPI, RBI, and DGCA retail inflation augmentation prototypes.

Zero Database Architecture: Directly reads/writes flat files (data/*.json).
"""

import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from econometrics import (
    DATA_DIR,
    FARES_FILE,
    INDEX_HISTORY_FILE,
    calculate_econometric_indicators,
    compute_lead_time_curve,
    ensure_data_directory,
    read_fares,
    read_index_history,
)
from scraper import run_scrape_batch, seed_initial_history_if_needed
from scrapy_runner import execute_scrapy_crawl, read_scrapy_status


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure data directory and files exist
    ensure_data_directory()
    # Seed historical depth if needed
    seed_initial_history_if_needed()
    # Compute initial index snapshot
    calculate_econometric_indicators()
    yield


app = FastAPI(
    title="APIx-India API",
    description="Real-Time Airfare Price Index for Retail Inflation Augmentation (MoSPI, RBI, DGCA)",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for open institutional access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
@app.head("/")
async def serve_dashboard(request: Request):
    """Serve the primary institutional financial analytics dashboard."""
    summary = calculate_econometric_indicators()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "APIx-India | High-Frequency Aviation CPI Augmentation",
            "initial_summary": summary,
        },
    )


@app.post("/api/scrape/trigger")
async def trigger_scrape(
    use_scrapy: bool = True,
    demo_mode: bool = False,
    routes: Optional[str] = None,
    lead_times: Optional[str] = None,
):
    """
    Executes real-time airfare data fetching from web travel portals using Scrapy.
    Appends new observations to data/fares.json, recalculates Jevons indices,
    and updates data/index_history.json and data/scrapy_status.json.
    """
    try:
        if use_scrapy:
            route_list = [r.strip() for r in routes.split(",")] if routes else None
            lt_list = [int(x.strip()) for x in lead_times.split(",")] if lead_times else None
            scrapy_res = await execute_scrapy_crawl(routes=route_list, lead_times=lt_list, demo_fallback=False)
            return {
                "status": "success",
                "engine": "Scrapy 2.18.0",
                "message": f"Scrapy harvested {scrapy_res['live_web_items']} verified live web fares from Google Flights in {scrapy_res['execution_duration_sec']}s.",
                "scrape_details": {
                    "records_added": scrapy_res["items_scraped"],
                    "live_web_records": scrapy_res["live_web_items"],
                    "fallback_records": 0,
                    "execution_duration_sec": scrapy_res["execution_duration_sec"],
                    "engine": "Scrapy 2.18.0 (Twisted/Epoll)",
                    "target_source": "Google Flights (Verified Actual)",
                },
                "index_snapshot": scrapy_res["index_snapshot"],
                "telemetry": scrapy_res["telemetry"],
            }
        else:
            # Fallback legacy runner
            scrape_result = await run_scrape_batch(demo_mode=demo_mode)
            index_snapshot = calculate_econometric_indicators()
            return {
                "status": "success",
                "engine": "Legacy HTTPX",
                "message": f"Scrape completed successfully. Added {scrape_result['records_added']} records.",
                "scrape_details": scrape_result,
                "index_snapshot": index_snapshot,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@app.get("/api/scrapy/status")
def get_scrapy_status():
    """Returns the current state and telemetry of the Scrapy web scraping engine."""
    try:
        return read_scrapy_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading Scrapy status: {str(e)}")


@app.post("/api/scrapy/trigger")
async def trigger_scrapy_explicit(
    routes: Optional[str] = "DEL-BOM,BLR-DEL,BOM-BLR",
    lead_times: Optional[str] = "1,7,15,30,45",
):
    """Explicit endpoint to run the Scrapy web scraper across selected routes and lead times."""
    try:
        route_list = [r.strip() for r in routes.split(",")] if routes else None
        lt_list = [int(x.strip()) for x in lead_times.split(",")] if lead_times else None
        return await execute_scrapy_crawl(routes=route_list, lead_times=lt_list, demo_fallback=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scrapy execution failed: {str(e)}")


@app.get("/api/index/summary")
def get_index_summary():
    """Returns the latest National Airfare Index, 24h delta, route weights, and sample size."""
    try:
        history = read_index_history()
        if history:
            latest = history[-1]
            return latest
        return calculate_econometric_indicators()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading index summary: {str(e)}")


@app.get("/api/index/trends")
def get_index_trends():
    """Returns historical daily index points directly from data/index_history.json."""
    try:
        history = read_index_history()
        if not history:
            # Generate snapshot
            snapshot = calculate_econometric_indicators()
            history = [snapshot]
        return {
            "count": len(history),
            "trends": history,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading index trends: {str(e)}")


@app.get("/api/lead-time-curve")
def get_lead_time_curve():
    """Returns average fare breakdown across the 5 lead time windows (T+1 to T+45)."""
    try:
        curve = compute_lead_time_curve()
        return curve
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing lead-time curve: {str(e)}")


@app.get("/api/raw-fares")
def get_raw_fares(limit: int = 150):
    """Returns the last N entries directly from data/fares.json without any database."""
    try:
        fares = read_fares()
        # Return most recent first
        recent = fares[-limit:][::-1] if fares else []
        return {
            "total_records": len(fares),
            "limit": limit,
            "fares": recent,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading raw fares: {str(e)}")


@app.get("/api/health")
def health_check():
    """System health check and flat-file storage verification."""
    fares_exist = os.path.exists(FARES_FILE)
    history_exist = os.path.exists(INDEX_HISTORY_FILE)
    fares_size = os.path.getsize(FARES_FILE) if fares_exist else 0
    history_size = os.path.getsize(INDEX_HISTORY_FILE) if history_exist else 0

    return {
        "status": "healthy",
        "architecture": "Zero-Database Local Flat Files",
        "storage": {
            "fares_json_exists": fares_exist,
            "fares_size_bytes": fares_size,
            "index_history_exists": history_exist,
            "index_history_size_bytes": history_size,
        },
    }
