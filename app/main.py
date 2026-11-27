"""LeaveGate FastAPI application entry point."""
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Auto-create / migrate database tables on startup."""
    init_db()
    yield


app = FastAPI(
    title="LeaveGate",
    description="Abwesenheitsverwaltung für Mitarbeitende",
    version="0.1.0",
    lifespan=lifespan,
)

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class EmployeeCreate(BaseModel):
    name: str
    email: str
    team: str
    remaining_days: int = 20


class EmployeeOut(BaseModel):
    id: int
    name: str
    email: str
    team: str
    remaining_days: int

    model_config = {"from_attributes": True}


class LeaveRequestCreate(BaseModel):
    employee_id: int
    type: str
    start_date: date
    end_date: date
    days: int = 1
    reason: str | None = None
    status: str = "draft"


class LeaveRequestOut(BaseModel):
    id: int
    employee_id: int
    type: str
    start_date: date
    end_date: date
    days: int
    reason: str | None
    status: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health", tags=["ops"])
async def health() -> dict:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Dashboard UI
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, tags=["ui"])
@app.get("/dashboard", response_class=HTMLResponse, tags=["ui"])
async def dashboard(request: Request):
    return templates.TemplateResponse(
        request, "dashboard.html", {"page": "dashboard"}
    )


# ---------------------------------------------------------------------------
# Employees API
# ---------------------------------------------------------------------------

@app.get("/api/employees", tags=["employees"])
def list_employees(db: Session = Depends(get_db)):  # noqa: B008
    from app.models import Employee
    return db.query(Employee).all()


@app.post("/api/employees", status_code=201, response_model=EmployeeOut, tags=["employees"])
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):  # noqa: B008
    from app.models import Employee
    emp = Employee(**payload.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@app.get("/api/employees/{emp_id}", response_model=EmployeeOut, tags=["employees"])
def get_employee(emp_id: int, db: Session = Depends(get_db)):  # noqa: B008
    from app.models import Employee
    emp = db.get(Employee, emp_id)
    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@app.patch("/api/employees/{emp_id}", response_model=EmployeeOut, tags=["employees"])
def patch_employee(emp_id: int, payload: EmployeeCreate, db: Session = Depends(get_db)):  # noqa: B008
    from app.models import Employee
    emp = db.get(Employee, emp_id)
    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(emp, k, v)
    db.commit()
    db.refresh(emp)
    return emp


# ---------------------------------------------------------------------------
# Leave Requests API
# ---------------------------------------------------------------------------

@app.get("/api/leave-requests", tags=["leave-requests"])
def list_leave_requests(db: Session = Depends(get_db)):  # noqa: B008
    from app.models import LeaveRequest
    return db.query(LeaveRequest).all()


@app.post(
    "/api/leave-requests",
    status_code=201,
    response_model=LeaveRequestOut,
    tags=["leave-requests"],
)
def create_leave_request(payload: LeaveRequestCreate, db: Session = Depends(get_db)):  # noqa: B008
    from app.models import Employee, LeaveRequest
    emp = db.get(Employee, payload.employee_id)
    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    lr = LeaveRequest(**payload.model_dump())
    db.add(lr)
    db.commit()
    db.refresh(lr)
    return lr


@app.get(
    "/api/leave-requests/{lr_id}",
    response_model=LeaveRequestOut,
    tags=["leave-requests"],
)
def get_leave_request(lr_id: int, db: Session = Depends(get_db)):  # noqa: B008
    from app.models import LeaveRequest
    lr = db.get(LeaveRequest, lr_id)
    if lr is None:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return lr


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"error": "Not found"})


@app.exception_handler(500)
async def server_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"error": "Internal server error"})
