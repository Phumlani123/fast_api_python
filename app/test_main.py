import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app  # Import your FastAPI app instance
from database import Base
import models
from datetime import datetime
import logging

@pytest.fixture(scope='function')
def test_db():
    engine = create_engine("sqlite:///:memory:")  
    Base.metadata.create_all(bind=engine) 

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # Clean up after tests

@pytest.fixture(scope="function")
def client(test_db):
    app.dependency_overrides[test_db] = lambda: test_db
    yield TestClient(app)
    app.dependency_overrides = {}

def test_create_customer_success(client: TestClient, test_db):
    customer_data = {
        "name": "John Doe",
        "email": "john.doe2@example.com",
        "age": 30,
        "signup_date": "2024-08-18"
    }
    
    response = client.post("/customers/", json=customer_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == customer_data["name"]
    assert data["email"] == customer_data["email"]
    assert data["age"] == customer_data["age"]
    assert data["signup_date"] == customer_data["signup_date"]

def test_create_customer_missing_field(client: TestClient):
    customer_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        # Missing 'age'
        "signup_date": "2024-08-18"
    }
    
    response = client.post("/customers/", json=customer_data)
    assert response.status_code == 422  
    assert response.json() 

def test_create_customer_invalid_data(client: TestClient):
    customer_data = {
        "name": "John Doe",
        "email": "not-an-email",  
        "age": "not-an-integer",   
        "signup_date": "2024-08-18"
    }
    
    response = client.post("/customers/", json=customer_data)
    assert response.status_code == 422  
    assert response.json()  


def test_read_customer_success(client: TestClient, test_db):
    customer_data = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "age": 28,
        "signup_date": "2024-08-18"
    }
    res = client.post("/customers/", json=customer_data)
    
    response = res.json()
    getResponse = client.get(f"/customers/{response["id"]}")

    assert getResponse.status_code == 200
    data = getResponse.json()
    assert data["name"] == "Jane Doe"
    assert data["email"] == "jane.doe@example.com"
    assert data["age"] == 28
    assert data["signup_date"] == "2024-08-18"

def test_read_customer_not_found(client: TestClient):
    response = client.get("/customers/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Customer not found"}