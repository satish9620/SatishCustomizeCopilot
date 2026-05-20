import sys
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

sys.path.append(str(Path(__file__).resolve().parent))
import app as app_module


@pytest.fixture(autouse=True)
def reset_employee_department_state():
    app_module.departments.clear()
    app_module.employees.clear()
    app_module.next_employee_id = 1


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_create_department_and_employee(client):
    create_department_response = client.post("/departments", json={"name": "Engineering"})
    assert create_department_response.status_code == 200
    assert create_department_response.json() == {"name": "Engineering"}

    create_employee_response = client.post(
        "/employees",
        json={"name": "Satish", "department": "Engineering", "salary": 50000}
    )
    assert create_employee_response.status_code == 200
    assert create_employee_response.json() == {
        "id": 1,
        "name": "Satish",
        "department": "Engineering",
        "salary": 50000.0
    }


def test_get_employee_and_department_salary_details(client):
    client.post("/departments", json={"name": "Engineering"})
    client.post(
        "/employees",
        json={"name": "Satish", "department": "Engineering", "salary": 50000}
    )
    client.post(
        "/employees",
        json={"name": "Kumar", "department": "Engineering", "salary": 70000}
    )

    employee_salary_response = client.get("/employees/1/salary")
    assert employee_salary_response.status_code == 200
    assert employee_salary_response.json() == {
        "employee_id": 1,
        "name": "Satish",
        "department": "Engineering",
        "salary": 50000.0
    }

    department_salary_response = client.get("/departments/Engineering/salary")
    assert department_salary_response.status_code == 200
    assert department_salary_response.json() == {
        "department": "Engineering",
        "total_salary": 120000.0,
        "employees": [
            {"employee_id": 1, "name": "Satish", "salary": 50000.0},
            {"employee_id": 2, "name": "Kumar", "salary": 70000.0},
        ],
    }


def test_get_department_wise_employees(client):
    client.post("/departments", json={"name": "HR"})
    client.post("/employees", json={"name": "Anu", "department": "HR", "salary": 40000})
    client.post("/employees", json={"name": "Ravi", "department": "HR", "salary": 45000})

    department_employees_response = client.get("/departments/HR/employees")
    assert department_employees_response.status_code == 200
    assert department_employees_response.json() == {
        "department": "HR",
        "employees": [
            {"id": 1, "name": "Anu", "department": "HR", "salary": 40000.0},
            {"id": 2, "name": "Ravi", "department": "HR", "salary": 45000.0},
        ],
    }
