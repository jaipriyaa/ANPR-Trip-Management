from app.crud.crud_transporter import crud_transporter
from app.crud.crud_vehicle import crud_vehicle
from app.crud.crud_vehicle_plate import crud_vehicle_plate
from app.crud.crud_driver import crud_driver
from app.crud.crud_vehicle_detection import crud_vehicle_detection
from app.crud.crud_gate import crud_gate
from app.crud.crud_camera import crud_camera
from app.crud.crud_gate_rule import crud_gate_rule
from app.crud.crud_vehicle_movement import crud_vehicle_movement
from app.crud.crud_scheduled_trip import crud_scheduled_trip

__all__ = [
    "crud_transporter",
    "crud_vehicle",
    "crud_vehicle_plate",
    "crud_driver",
    "crud_vehicle_detection",
    "crud_gate",
    "crud_camera",
    "crud_gate_rule",
    "crud_vehicle_movement",
    "crud_scheduled_trip",
]
