# backend/app.py

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Optional, Dict
from fastapi.middleware.cors import CORSMiddleware
import uuid

app = FastAPI(
    title="Boarding.ai Simulation API",
    version="1.1.0",
    description="Simulation engine backend for Boarding.ai",
)

# ------------------------------------------------------
# CORS CONFIG — Allows Base44, ngrok, localhost
# ------------------------------------------------------

ALLOWED_ORIGINS = [
    "*",  # easiest for dev
    "https://app.base44.com",
    "https://*.base44.com",
    "https://*.modal.host",
    "https://hylophagous-candis-zealous.ngrok-free.dev",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],   # <-- CRITICAL (OPTIONS ALLOWED)
    allow_headers=["*"],
)

# ------------------------------------------------------
# MODELS
# ------------------------------------------------------

class Aircraft(BaseModel):
    type: str
    num_rows: int
    seats_per_row: int
    num_aisles: int

class Load(BaseModel):
    load_factor: float

class Boarding(BaseModel):
    method: str
    baseline_method: str

class Bags(BaseModel):
    carry_on_rate: float
    bin_capacity_per_row: int

class Behavior(BaseModel):
    walking_speed_mean: Optional[float] = 1.3
    stow_time_carry_on_mean: Optional[float] = 12.0
    seat_slide_time_mean: Optional[float] = 3.0
    late_pax_rate: Optional[float] = 0.02

class Controls(BaseModel):
    time_step: Optional[float] = 0.5
    num_runs: Optional[int] = 25
    cost_per_minute_delay: Optional[float] = 75.0

class SimulateRequest(BaseModel):
    aircraft: Aircraft
    load: Load
    boarding: Boarding
    bags: Bags
    behavior: Optional[Behavior] = None
    controls: Optional[Controls] = None

class Assumptions(BaseModel):
    flights_per_year: Optional[int] = 1825

class SimulateResponse(BaseModel):
    run_id: str
    total_boarding_time_sec: int
    time_to_50_percent_sec: Optional[int] = None
    time_to_90_percent_sec: Optional[int] = None
    num_aisle_conflicts: int
    max_aisle_queue_length: Optional[int] = None
    avg_wait_time_per_pax_sec: Optional[float] = None
    baseline_boarding_time_sec: int
    delta_vs_baseline_sec: int
    percent_faster_vs_baseline: float
    dollars_saved_per_flight: float
    dollars_saved_per_year: float
    assumptions: Optional[Assumptions] = None

# ------------------------------------------------------
# LOCAL STORAGE
# ------------------------------------------------------

RUN_STORAGE: Dict[str, SimulateResponse] = {}

# ------------------------------------------------------
# FIX: OPTIONS HANDLER
# ------------------------------------------------------

@app.options("/simulate")
async def simulate_options():
    return Response(status_code=200)

# ------------------------------------------------------
# SIMULATE ENDPOINT
# ------------------------------------------------------

@app.post("/simulate", response_model=SimulateResponse)
async def simulate(req: SimulateRequest):

    run_id = str(uuid.uuid4())

    response = SimulateResponse(
        run_id=run_id,
        total_boarding_time_sec=1830,
        time_to_50_percent_sec=740,
        time_to_90_percent_sec=1540,
        num_aisle_conflicts=142,
        max_aisle_queue_length=12,
        avg_wait_time_per_pax_sec=28.0,
        baseline_boarding_time_sec=2020,
        delta_vs_baseline_sec=-190,
        percent_faster_vs_baseline=9.4,
        dollars_saved_per_flight=225.0,
        dollars_saved_per_year=410000.0,
        assumptions=Assumptions(),
    )

    RUN_STORAGE[run_id] = response
    return response

# ------------------------------------------------------
# RESULT FETCH
# ------------------------------------------------------

@app.get("/simulation-result/{run_id}", response_model=SimulateResponse)
async def get_simulation_result(run_id: str):
    if run_id not in RUN_STORAGE:
        raise HTTPException(status_code=404, detail="Run ID not found")
    return RUN_STORAGE[run_id]

# ------------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Boarding.ai Simulation API is running",
    }
