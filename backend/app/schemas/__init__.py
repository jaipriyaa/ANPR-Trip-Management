from app.schemas.transporter import (
    TransporterCreate, TransporterUpdate, TransporterResponse, TransporterPaginatedResponse
)
from app.schemas.vehicle import (
    VehicleCreate, VehicleUpdate, VehicleResponse, VehiclePaginatedResponse
)
from app.schemas.vehicle_plate import (
    VehiclePlateCreate, VehiclePlateUpdate, VehiclePlateResponse, VehiclePlatePaginatedResponse
)
from app.schemas.driver import (
    DriverCreate, DriverUpdate, DriverResponse, DriverPaginatedResponse
)
from app.schemas.gate import (
    GateCreate, GateUpdate, GateResponse, GatePaginatedResponse
)
from app.schemas.camera import (
    CameraCreate, CameraUpdate, CameraResponse, CameraPaginatedResponse
)
from app.schemas.gate_rule import (
    GateRuleCreate, GateRuleUpdate, GateRuleResponse
)
from app.schemas.vehicle_movement import (
    VehicleMovementCreate, VehicleMovementUpdate, VehicleMovementResponse,
    VehicleMovementPaginatedResponse, LiveMovementsSummaryResponse
)
from app.schemas.scheduled_trip import (
    ScheduledTripCreate, ScheduledTripUpdate, TripStatusUpdate, TripApprovalUpdate,
    TripStatusHistoryResponse, ScheduledTripResponse, ScheduledTripPaginatedResponse,
    TripDashboardSummaryResponse
)

__all__ = [
    "TransporterCreate", "TransporterUpdate", "TransporterResponse", "TransporterPaginatedResponse",
    "VehicleCreate", "VehicleUpdate", "VehicleResponse", "VehiclePaginatedResponse",
    "VehiclePlateCreate", "VehiclePlateUpdate", "VehiclePlateResponse", "VehiclePlatePaginatedResponse",
    "DriverCreate", "DriverUpdate", "DriverResponse", "DriverPaginatedResponse",
    "GateCreate", "GateUpdate", "GateResponse", "GatePaginatedResponse",
    "CameraCreate", "CameraUpdate", "CameraResponse", "CameraPaginatedResponse",
    "GateRuleCreate", "GateRuleUpdate", "GateRuleResponse",
    "VehicleMovementCreate", "VehicleMovementUpdate", "VehicleMovementResponse",
    "VehicleMovementPaginatedResponse", "LiveMovementsSummaryResponse",
    "ScheduledTripCreate", "ScheduledTripUpdate", "TripStatusUpdate", "TripApprovalUpdate",
    "TripStatusHistoryResponse", "ScheduledTripResponse", "ScheduledTripPaginatedResponse",
    "TripDashboardSummaryResponse",
]
