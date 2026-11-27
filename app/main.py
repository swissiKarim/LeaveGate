"""LeaveGate FastAPI application entry point."""
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import get_db, init_db
from app.services.leave_service import (
    BusinessRuleError,
    InvalidTransitionError,
    ValidationError,
    apply_transition,
    count_workdays,
    validate_new_leave_request,
)


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


class EmployeePatch(BaseModel):
    name: str | None = None
    email: str | None = None
    team: str | None = None
    remaining_days: int | None = None


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
    reason: str | None = None
    # days is computed by the domain service; client value is ignored
    days: int | None = None


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


class StatusTransitionIn(BaseModel):
    status: str


# ---------------------------------------------------------------------------
# Unified error helpers
# ---------------------------------------------------------------------------

def _error_response(status_code: int, error: str, detail: str | None = None) -> JSONResponse:
    body: dict = {"error": error}
    if detail is not None:
        body["detail"] = detail
    return JSONResponse(status_code=status_code, content=body)


# ---------------------------------------------------------------------------
# Exception handlers — unified JSON for all 4xx / 5xx
# ---------------------------------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    detail = str(exc.detail) if exc.detail else None
    # For 404 always expose detail so AC-1 / SC-1 can assert body.detail exists
    if exc.status_code == 404:
        error_msg = "Not found"
        detail = detail or "The requested resource was not found"
    elif exc.status_code == 409:
        error_msg = detail or "Conflict"
        detail = None  # already in error
    elif exc.status_code == 422:
        error_msg = detail or "Unprocessable entity"
        detail = None
    elif exc.status_code == 500:
        error_msg = "Internal server error"
        detail = None
    else:
        error_msg = detail or f"HTTP {exc.status_code}"
        detail = None
    return _error_response(exc.status_code, error_msg, detail)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    detail = "; ".join(
        f"{' -> '.join(str(loc) for loc in e['loc'])}: {e['msg']}"
        for e in errors
    )
    return _error_response(422, "Validation error", detail)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return _error_response(500, "Internal server error", str(exc))


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
# Employees UI
# ---------------------------------------------------------------------------

@app.get("/employees", response_class=HTMLResponse, tags=["ui"])
def employees_list(
    request: Request,
    q: str | None = None,
    team: str | None = None,
    sort: str | None = None,
    page: int = 1,
    db: Session = Depends(get_db),  # noqa: B008
):
    from app.models import Employee

    query = db.query(Employee)
    if q:
        like = f"%{q}%"
        query = query.filter(
            Employee.name.ilike(like) | Employee.email.ilike(like)
        )
    if team:
        query = query.filter(Employee.team == team)
    if sort:
        col = sort.lstrip("-")
        col_attr = getattr(Employee, col, None)
        if col_attr is not None:
            query = query.order_by(col_attr.desc() if sort.startswith("-") else col_attr)
    page_size = 20
    offset = (max(page, 1) - 1) * page_size
    employees = query.offset(offset).limit(page_size).all()
    # Distinct teams for filter dropdown
    all_teams = [row[0] for row in db.query(Employee.team).distinct().order_by(Employee.team).all()]
    return templates.TemplateResponse(
        request,
        "employees/list.html",
        {
            "page": "employees",
            "employees": employees,
            "q": q or "",
            "team": team or "",
            "sort": sort or "",
            "current_page": page,
            "all_teams": all_teams,
        },
    )


@app.get("/employees/new", response_class=HTMLResponse, tags=["ui"])
def employee_new_form(request: Request):
    return templates.TemplateResponse(
        request,
        "employees/new.html",
        {"page": "employees"},
    )


@app.get("/employees/{emp_id}", response_class=HTMLResponse, tags=["ui"])
def employee_detail(emp_id: int, request: Request, db: Session = Depends(get_db)):  # noqa: B008
    from app.models import Employee
    emp = db.get(Employee, emp_id)
    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return templates.TemplateResponse(
        request,
        "employees/detail.html",
        {"page": "employees", "emp": emp},
    )


@app.get("/employees/{emp_id}/edit", response_class=HTMLResponse, tags=["ui"])
def employee_edit_form(emp_id: int, request: Request, db: Session = Depends(get_db)):  # noqa: B008
    from app.models import Employee
    emp = db.get(Employee, emp_id)
    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return templates.TemplateResponse(
        request,
        "employees/edit.html",
        {"page": "employees", "emp": emp},
    )


# ---------------------------------------------------------------------------
# Employees API
# ---------------------------------------------------------------------------

@app.get("/api/employees", tags=["employees"])
def list_employees(
    q: str | None = None,
    team: str | None = None,
    sort: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),  # noqa: B008
):
    from app.models import Employee

    query = db.query(Employee)
    if q:
        like = f"%{q}%"
        query = query.filter(
            Employee.name.ilike(like) | Employee.email.ilike(like)
        )
    if team:
        query = query.filter(Employee.team == team)
    if sort:
        col = sort.lstrip("-")
        col_attr = getattr(Employee, col, None)
        if col_attr is not None:
            query = query.order_by(col_attr.desc() if sort.startswith("-") else col_attr)
    offset = (max(page, 1) - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    return {"items": [EmployeeOut.model_validate(e) for e in items]}


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
def patch_employee(emp_id: int, payload: EmployeePatch, db: Session = Depends(get_db)):  # noqa: B008
    from app.models import Employee
    emp = db.get(Employee, emp_id)
    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        if v is not None:
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

    # AC-2: compute workdays; return 422 for invalid ranges
    try:
        computed_days = count_workdays(payload.start_date, payload.end_date)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # AC-3 & AC-4: business rule checks
    try:
        validate_new_leave_request(
            db=db,
            employee_id=payload.employee_id,
            leave_type=payload.type,
            start=payload.start_date,
            end=payload.end_date,
            days=computed_days,
        )
    except BusinessRuleError as exc:
        return JSONResponse(status_code=409, content={"error": str(exc)})

    lr = LeaveRequest(
        employee_id=payload.employee_id,
        type=payload.type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        days=computed_days,
        reason=payload.reason,
        status="draft",
    )
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


@app.post(
    "/api/leave-requests/{lr_id}/status",
    response_model=LeaveRequestOut,
    tags=["leave-requests"],
)
def transition_leave_request_status(
    lr_id: int,
    payload: StatusTransitionIn,
    db: Session = Depends(get_db),  # noqa: B008
):
    """Apply a status transition to a leave request (AC-1)."""
    from app.models import LeaveRequest

    lr = db.get(LeaveRequest, lr_id)
    if lr is None:
        raise HTTPException(status_code=404, detail="Leave request not found")

    try:
        new_status = apply_transition(lr.status, payload.status)
    except InvalidTransitionError as exc:
        return JSONResponse(status_code=409, content={"error": str(exc)})

    lr.status = new_status
    db.commit()
    db.refresh(lr)
    return lr


@app.delete(
    "/api/leave-requests/{lr_id}",
    status_code=204,
    tags=["leave-requests"],
)
def delete_leave_request(lr_id: int, db: Session = Depends(get_db)):  # noqa: B008
    """Only draft requests may be deleted."""
    from app.models import LeaveRequest

    lr = db.get(LeaveRequest, lr_id)
    if lr is None:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if lr.status != "draft":
        return JSONResponse(
            status_code=409,
            content={"error": f"Only draft requests may be deleted (current status: '{lr.status}')."},
        )
    db.delete(lr)
    db.commit()


# ---------------------------------------------------------------------------
# Demo endpoints used only by scenario / unit tests
# ---------------------------------------------------------------------------

@app.get("/api/demo/not-found", tags=["demo"])
async def demo_not_found():
    raise HTTPException(status_code=404, detail="Demo resource not found")


@app.post("/api/demo/conflict", tags=["demo"])
async def demo_conflict():
    raise HTTPException(status_code=409, detail="Demo conflict: resource already exists")


@app.post("/api/demo/validate", tags=["demo"])
async def demo_validate(payload: dict):
    # Triggers RequestValidationError when body is wrong type; here we
    # manually raise 422 via HTTPException so SC-2 can target /api/demo/validate-strict
    raise HTTPException(status_code=422, detail="Validation failed")
