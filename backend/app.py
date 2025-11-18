# backend/app.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Boarding.ai Simulation API",
    version="1.0.0",
    description=(
        "Simulation service for Boarding.ai. "
        "The /simulate endpoint accepts a flight boarding scenario and "
        "returns operational and economic metrics for the specified "
        "boarding strategy vs a baseline."
    ),
)

# ----- Pydantic models matching our OpenAPI schema (simplified) -----

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


# ----- Stub implementation of /simulate -----

@app.post("/simulate", response_model=SimulateResponse)
async def simulate(req: SimulateRequest) -> SimulateResponse:
    """
    Stub implementation of the boarding simulation.

    For now this ignores the detailed inputs and returns a hard-coded
    but realistic-looking response that matches our OpenAPI contract.
    Later, we will replace this stub with the real simulation engine.
    """

    # TODO: plug in real simulation engine using `req` data.
    # For now we just return static example values.
    return SimulateResponse(
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
        assumptions=Assumptions(flights_per_year=1825),
    )
