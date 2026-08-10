from fastapi import APIRouter

from app.api.v1.endpoints import (
    transporters,
    vehicles,
    vehicle_plates,
    drivers,
    vehicle_recognition,
    gates,
    gate_cameras,
    gate_rules,
    movements,
    live_monitor,
    trips,
    admin,
    authorization,
    manual_review,
    pipeline,
    deepstream,
    system,
    benchmark,
    reports,
    alerts,
)

api_router = APIRouter()

api_router.include_router(transporters.router)
api_router.include_router(vehicles.router)
api_router.include_router(vehicle_plates.router)
api_router.include_router(drivers.router)
api_router.include_router(vehicle_recognition.router)
api_router.include_router(gates.router)
api_router.include_router(gate_cameras.router)
api_router.include_router(gate_rules.router)
api_router.include_router(movements.router)
api_router.include_router(live_monitor.router)
api_router.include_router(trips.router)
api_router.include_router(reports.router)
api_router.include_router(alerts.router)
api_router.include_router(admin.router)
api_router.include_router(authorization.router)
api_router.include_router(manual_review.router)
api_router.include_router(pipeline.router)
api_router.include_router(system.router)
api_router.include_router(benchmark.router)
api_router.include_router(deepstream.router, prefix="/deepstream", tags=["NVIDIA DeepStream 7.x"])

