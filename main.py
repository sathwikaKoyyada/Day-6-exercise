from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="TechStar Group - Supply Chain Status API",
    description="Internal utility API for shipment tracking",
    version="1.0.0",
)

MOCK_SHIPMENTS: dict[str, dict] = {
    "SH001": {
        "shipment_id": "SH001",
        "carrier": "DHL",
        "status": "in_transit",
        "origin": "Mumbai",
        "destination": "Delhi",
        "cost_usd": 250.0,
        "created_at": "2024-01-18T10:00:00",
    },
    "SH002": {
        "shipment_id": "SH002",
        "carrier": "FEDEX",
        "status": "delivered",
        "origin": "Chennai",
        "destination": "Bangalore",
        "cost_usd": 180.5,
        "created_at": "2024-01-17T09:30:00",
    },
    "SH003": {
        "shipment_id": "SH003",
        "carrier": "BLUEDART",
        "status": "delayed",
        "origin": "Pune",
        "destination": "Hyderabad",
        "cost_usd": 320.0,
        "created_at": "2024-01-16T14:15:00",
    },
}

MOCK_CARRIERS: dict[str, dict] = {
    "DHL": {
        "code": "DHL",
        "name": "DHL Express",
        "sla_days": 2,
    },
    "FEDEX": {
        "code": "FEDEX",
        "name": "FedEx India",
        "sla_days": 3,
    },
    "BLUEDART": {
        "code": "BLUEDART",
        "name": "BlueDart",
        "sla_days": 2,
    },
}


class ShipmentResponse(BaseModel):
    shipment_id: str
    carrier: str
    status: str
    origin: str
    destination: str
    cost_usd: float
    created_at: str


class CarrierResponse(BaseModel):
    code: str
    name: str
    sla_days: int


class ShipmentCreateRequest(BaseModel):
    shipment_id: str = Field(..., min_length=3, max_length=20)
    carrier: str = Field(..., min_length=2)
    origin: str = Field(..., min_length=2)
    destination: str = Field(..., min_length=2)
    cost_usd: float = Field(..., gt=0)


@app.get("/")
def home():
    return {"message": "Supply Chain API Running"}


@app.get(
    "/shipments/{shipment_id}",
    response_model=ShipmentResponse,
)
def get_shipment(shipment_id: str) -> dict:
    if shipment_id not in MOCK_SHIPMENTS:
        raise HTTPException(
            status_code=404,
            detail=f"Shipment {shipment_id} not found",
        )

    return MOCK_SHIPMENTS[shipment_id]


@app.get("/carriers/{carrier_code}", response_model=CarrierResponse)
def get_carrier(carrier_code: str):
    return MOCK_CARRIERS[carrier_code]


@app.get("/shipments", response_model=list[ShipmentResponse])
def list_shipments(
    status: Optional[str] = None,
    carrier: Optional[str] = None,
) -> list[dict]:
    """
    GET /shipments
    GET /shipments?status=delayed
    GET /shipments?carrier=DHL&status=in_transit
    """

    shipments = list(MOCK_SHIPMENTS.values())

    if status:
        shipments = [s for s in shipments if s["status"].lower() == status.lower()]

    if carrier:
        shipments = [s for s in shipments if s["carrier"].upper() == carrier.upper()]

    return shipments

@app.post(
    "/shipments",
    response_model=ShipmentResponse,
    status_code=201,
)
def create_shipment(
    payload: ShipmentCreateRequest,
) -> dict:

    if payload.shipment_id in MOCK_SHIPMENTS:
        raise HTTPException(
            status_code=409,
            detail=f"Shipment {payload.shipment_id} already exists",
        )

    record = {
        "shipment_id": payload.shipment_id,
        "carrier": payload.carrier.upper(),
        "status": "pending",
        "origin": payload.origin,
        "destination": payload.destination,
        "cost_usd": payload.cost_usd,
        "created_at": datetime.utcnow().isoformat(),
    }

    MOCK_SHIPMENTS[payload.shipment_id] = record

    return record


@app.get(
    "/carriers",
    response_model=list[CarrierResponse],
)
def list_carriers() -> list[dict]:
    """
    GET /carriers
    """

    return list(MOCK_CARRIERS.values())
