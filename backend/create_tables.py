from app.database.connection import engine
from app.database.base import Base

# Import all models to register them
from app.models import Transporter, Vehicle, VehiclePlate, Driver

print("Creating tables...")

Base.metadata.create_all(bind=engine)

print("[OK] Tables created successfully!")