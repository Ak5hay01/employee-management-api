from sqlalchemy.orm import Session

from app import models, schemas


def get_employees(
    db: Session
):
    return db.query(
        models.Employee
    ).all()


def get_employee(
    db: Session,
    employee_id: int
):
    return db.query(
        models.Employee
    ).filter(
        models.Employee.id == employee_id
    ).first()


def create_employee(
    db: Session,
    employee: schemas.EmployeeCreate
):

    db_employee = models.Employee(
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        department=employee.department,
        designation=employee.designation
    )

    db.add(db_employee)

    db.commit()

    db.refresh(db_employee)

    return db_employee


def update_employee(
    db: Session,
    employee_id: int,
    employee: schemas.EmployeeUpdate
):

    db_employee = get_employee(
        db,
        employee_id
    )

    if db_employee is None:
        return None

    db_employee.first_name = employee.first_name
    db_employee.last_name = employee.last_name
    db_employee.email = employee.email
    db_employee.department = employee.department
    db_employee.designation = employee.designation

    db.commit()

    db.refresh(db_employee)

    return db_employee


def delete_employee(
    db: Session,
    employee_id: int
):

    db_employee = get_employee(
        db,
        employee_id
    )

    if db_employee is None:
        return None

    db.delete(db_employee)

    db.commit()

    return db_employee