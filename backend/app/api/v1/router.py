from fastapi import APIRouter

from app.api.v1 import auth, dashboard, deliveries, documents, hostels, invoices, payments

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(hostels.router)
api_router.include_router(deliveries.router)
api_router.include_router(invoices.router)
api_router.include_router(payments.router)
api_router.include_router(dashboard.router)
api_router.include_router(documents.router)
