"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}

# In-memory employee and department database
departments = {}
employees = {}
next_employee_id = 1


class DepartmentCreate(BaseModel):
    name: str


class EmployeeCreate(BaseModel):
    name: str
    department: str
    salary: float = Field(gt=0)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.post("/departments")
def create_department(department: DepartmentCreate):
    if department.name in departments:
        raise HTTPException(status_code=400, detail="Department already exists")

    departments[department.name] = {"employees": []}
    return {"name": department.name}


@app.post("/employees")
def create_employee(employee: EmployeeCreate):
    if employee.department not in departments:
        raise HTTPException(status_code=404, detail="Department not found")

    global next_employee_id
    employee_id = next_employee_id
    next_employee_id += 1

    employee_record = {
        "id": employee_id,
        "name": employee.name,
        "department": employee.department,
        "salary": employee.salary
    }
    employees[employee_id] = employee_record
    departments[employee.department]["employees"].append(employee_id)
    return employee_record


@app.get("/employees/{employee_id}/salary")
def get_employee_salary_details(employee_id: int):
    if employee_id not in employees:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee = employees[employee_id]
    return {
        "employee_id": employee["id"],
        "name": employee["name"],
        "department": employee["department"],
        "salary": employee["salary"]
    }


@app.get("/departments/{department_name}/salary")
def get_department_salary_details(department_name: str):
    if department_name not in departments:
        raise HTTPException(status_code=404, detail="Department not found")

    department_employee_ids = departments[department_name]["employees"]
    department_employees = [employees[employee_id] for employee_id in department_employee_ids]
    total_salary = sum(employee["salary"] for employee in department_employees)

    return {
        "department": department_name,
        "total_salary": total_salary,
        "employees": [
            {
                "employee_id": employee["id"],
                "name": employee["name"],
                "salary": employee["salary"]
            }
            for employee in department_employees
        ]
    }


@app.get("/departments/{department_name}/employees")
def get_department_wise_employees(department_name: str):
    if department_name not in departments:
        raise HTTPException(status_code=404, detail="Department not found")

    department_employee_ids = departments[department_name]["employees"]
    return {
        "department": department_name,
        "employees": [employees[employee_id] for employee_id in department_employee_ids]
    }
