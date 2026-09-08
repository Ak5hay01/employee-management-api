from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    File,
    UploadFile
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import Base, engine, get_db
from pathlib import Path
from uuid import uuid4

from app.s3 import (
    upload_image,
    delete_image,
    generate_presigned_url
)


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="Employee Management API",
    description="REST API for managing employees",
    version="1.0.0",
)


@app.get("/")
def root():

    return {
        "message": "Employee Management API is running"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


@app.get("/ui")
def serve_ui():

    return FileResponse(
        "static/index.html"
    )


@app.post(
    "/employees",
    response_model=schemas.EmployeeResponse
)
def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db)
):

    existing_employee = db.query(
        models.Employee
    ).filter(
        models.Employee.email == employee.email
    ).first()

    if existing_employee:

        raise HTTPException(
            status_code=400,
            detail="Employee with this email already exists"
        )

    return crud.create_employee(
        db,
        employee
    )


# @app.get(
#     "/employees",
#     response_model=list[schemas.EmployeeResponse]
# )
# def get_employees(
#     db: Session = Depends(get_db)
# ):

#     return crud.get_employees(db)

@app.get(
    "/employees",
    response_model=list[schemas.EmployeeResponse]
)
def get_employees(
    db: Session = Depends(get_db)
):

    employees = crud.get_employees(db)

    result = []

    for employee in employees:

        result.append({
            "id": employee.id,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "email": employee.email,
            "department": employee.department,
            "designation": employee.designation,
            "profile_image_url": (
                generate_presigned_url(
                    employee.profile_image_key
                )
                if employee.profile_image_key
                else None
            ),
            "created_at": employee.created_at,
            "updated_at": employee.updated_at
        })

    return result


@app.get(
    "/employees/{employee_id}",
    response_model=schemas.EmployeeResponse
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):

    employee = crud.get_employee(
        db,
        employee_id
    )

    if employee is None:

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return {
        "id": employee.id,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "email": employee.email,
        "department": employee.department,
        "designation": employee.designation,
        "profile_image_url": (
            generate_presigned_url(
                employee.profile_image_key
            )
            if employee.profile_image_key
            else None
        ),
        "created_at": employee.created_at,
        "updated_at": employee.updated_at
    }


@app.put(
    "/employees/{employee_id}",
    response_model=schemas.EmployeeResponse
)
def update_employee(
    employee_id: int,
    employee: schemas.EmployeeUpdate,
    db: Session = Depends(get_db)
):

    existing_employee = crud.get_employee(
        db,
        employee_id
    )

    if existing_employee is None:

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return crud.update_employee(
        db,
        employee_id,
        employee
    )


@app.delete(
    "/employees/{employee_id}"
)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):

    employee = crud.get_employee(
        db,
        employee_id
    )

    if employee is None:

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    image_key = employee.profile_image_key

    crud.delete_employee(
        db,
        employee_id
    )

    if image_key:
        delete_image(image_key)

    return {
        "message": "Employee deleted successfully"
    }


@app.post(
    "/employees/{employee_id}/profile-image",
    response_model=schemas.EmployeeResponse
)
async def upload_profile_image(
    employee_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    employee = crud.get_employee(
        db,
        employee_id
    )

    if employee is None:

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    allowed_types = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp"
    }

    if file.content_type not in allowed_types:

        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG and WEBP images are allowed"
        )

    file_content = await file.read()

    max_size = 5 * 1024 * 1024

    if len(file_content) > max_size:

        raise HTTPException(
            status_code=400,
            detail="Image size must be 5 MB or less"
        )

    extension = allowed_types[file.content_type]

    object_key = (
        f"employees/{employee_id}/"
        f"{uuid4().hex}{extension}"
    )

    old_image_key = employee.profile_image_key

    upload_image(
        file_content,
        object_key,
        file.content_type
    )

    employee.profile_image_key = object_key

    db.commit()
    db.refresh(employee)

    if old_image_key:
        delete_image(old_image_key)

    return {
        "id": employee.id,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "email": employee.email,
        "department": employee.department,
        "designation": employee.designation,
        "profile_image_url": generate_presigned_url(
            employee.profile_image_key
        ),
        "created_at": employee.created_at,
        "updated_at": employee.updated_at
    }