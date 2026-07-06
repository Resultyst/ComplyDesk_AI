from fastapi import APIRouter, HTTPException

from app.schemas.customer import Customer, CustomerDetail
from app.services import customer_service

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/", response_model=list[Customer])
async def list_customers():
    """Return all customers."""
    return customer_service.list_customers()


@router.get("/{customer_id}", response_model=CustomerDetail)
async def get_customer_detail(customer_id: str):
    """Return full customer detail including memory and recent tickets."""
    detail = customer_service.get_customer_detail(customer_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return detail
