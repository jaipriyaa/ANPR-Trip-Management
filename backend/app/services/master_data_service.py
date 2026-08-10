from typing import Optional, List, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_transporter import crud_transporter
from app.crud.crud_vehicle import crud_vehicle
from app.crud.crud_vehicle_plate import crud_vehicle_plate
from app.crud.crud_driver import crud_driver
from app.models.transporter import Transporter
from app.models.vehicle import Vehicle
from app.models.vehicle_plate import VehiclePlate
from app.models.driver import Driver
from app.schemas.transporter import TransporterCreate, TransporterUpdate
from app.schemas.vehicle import VehicleCreate, VehicleUpdate
from app.schemas.vehicle_plate import VehiclePlateCreate, VehiclePlateUpdate
from app.schemas.driver import DriverCreate, DriverUpdate


class MasterDataService:
    # --- Transporters ---
    def create_transporter(self, db: Session, obj_in: TransporterCreate) -> Transporter:
        existing = crud_transporter.get_by_code(db, code=obj_in.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transporter code '{obj_in.code}' already exists."
            )
        return crud_transporter.create(db, obj_in=obj_in)

    def get_transporters(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Transporter], int]:
        return crud_transporter.get_multi(db, skip=skip, limit=limit, search=search, is_active=is_active)

    def get_transporter(self, db: Session, transporter_id: UUID) -> Transporter:
        obj = crud_transporter.get(db, transporter_id=transporter_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transporter not found.")
        return obj

    def update_transporter(self, db: Session, transporter_id: UUID, obj_in: TransporterUpdate) -> Transporter:
        db_obj = self.get_transporter(db, transporter_id=transporter_id)
        if obj_in.code and obj_in.code != db_obj.code:
            existing = crud_transporter.get_by_code(db, code=obj_in.code)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Transporter code '{obj_in.code}' is taken."
                )
        return crud_transporter.update(db, db_obj=db_obj, obj_in=obj_in)

    def delete_transporter(self, db: Session, transporter_id: UUID) -> bool:
        self.get_transporter(db, transporter_id=transporter_id)
        return crud_transporter.delete(db, transporter_id=transporter_id)

    # --- Vehicles ---
    def create_vehicle(self, db: Session, obj_in: VehicleCreate) -> Vehicle:
        existing = crud_vehicle.get_by_number(db, vehicle_number=obj_in.vehicle_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Vehicle number '{obj_in.vehicle_number}' is already registered."
            )
        if obj_in.transporter_id:
            self.get_transporter(db, transporter_id=obj_in.transporter_id)
        
        vehicle = crud_vehicle.create(db, obj_in=obj_in)

        # Auto-create primary plate entry
        plate_in = VehiclePlateCreate(
            vehicle_id=vehicle.id,
            plate_number=vehicle.vehicle_number,
            plate_type="Standard",
            is_primary=True,
            is_active=True
        )
        crud_vehicle_plate.create(db, obj_in=plate_in)
        db.refresh(vehicle)
        return vehicle

    def get_vehicles(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        transporter_id: Optional[UUID] = None,
        vehicle_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_blacklisted: Optional[bool] = None
    ) -> Tuple[List[Vehicle], int]:
        return crud_vehicle.get_multi(
            db, skip=skip, limit=limit, search=search,
            transporter_id=transporter_id, vehicle_type=vehicle_type,
            is_active=is_active, is_blacklisted=is_blacklisted
        )

    def get_vehicle(self, db: Session, vehicle_id: UUID) -> Vehicle:
        obj = crud_vehicle.get(db, vehicle_id=vehicle_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
        return obj

    def update_vehicle(self, db: Session, vehicle_id: UUID, obj_in: VehicleUpdate) -> Vehicle:
        db_obj = self.get_vehicle(db, vehicle_id=vehicle_id)
        if obj_in.vehicle_number and obj_in.vehicle_number != db_obj.vehicle_number:
            existing = crud_vehicle.get_by_number(db, vehicle_number=obj_in.vehicle_number)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Vehicle number '{obj_in.vehicle_number}' is taken."
                )
        if obj_in.transporter_id:
            self.get_transporter(db, transporter_id=obj_in.transporter_id)
        return crud_vehicle.update(db, db_obj=db_obj, obj_in=obj_in)

    def delete_vehicle(self, db: Session, vehicle_id: UUID) -> bool:
        self.get_vehicle(db, vehicle_id=vehicle_id)
        return crud_vehicle.delete(db, vehicle_id=vehicle_id)

    # --- Vehicle Plates ---
    def create_plate(self, db: Session, obj_in: VehiclePlateCreate) -> VehiclePlate:
        self.get_vehicle(db, vehicle_id=obj_in.vehicle_id)
        return crud_vehicle_plate.create(db, obj_in=obj_in)

    def get_plates(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        vehicle_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[VehiclePlate], int]:
        return crud_vehicle_plate.get_multi(
            db, skip=skip, limit=limit, search=search, vehicle_id=vehicle_id, is_active=is_active
        )

    def delete_plate(self, db: Session, plate_id: UUID) -> bool:
        plate = crud_vehicle_plate.get(db, plate_id=plate_id)
        if not plate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle plate record not found.")
        return crud_vehicle_plate.delete(db, plate_id=plate_id)

    # --- Drivers ---
    def create_driver(self, db: Session, obj_in: DriverCreate) -> Driver:
        existing = crud_driver.get_by_license(db, license_number=obj_in.license_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Driver license '{obj_in.license_number}' already registered."
            )
        if obj_in.transporter_id:
            self.get_transporter(db, transporter_id=obj_in.transporter_id)
        return crud_driver.create(db, obj_in=obj_in)

    def get_drivers(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        transporter_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Driver], int]:
        return crud_driver.get_multi(
            db, skip=skip, limit=limit, search=search, transporter_id=transporter_id, is_active=is_active
        )

    def get_driver(self, db: Session, driver_id: UUID) -> Driver:
        obj = crud_driver.get(db, driver_id=driver_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")
        return obj

    def update_driver(self, db: Session, driver_id: UUID, obj_in: DriverUpdate) -> Driver:
        db_obj = self.get_driver(db, driver_id=driver_id)
        if obj_in.license_number and obj_in.license_number != db_obj.license_number:
            existing = crud_driver.get_by_license(db, license_number=obj_in.license_number)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Driver license '{obj_in.license_number}' is taken."
                )
        if obj_in.transporter_id:
            self.get_transporter(db, transporter_id=obj_in.transporter_id)
        return crud_driver.update(db, db_obj=db_obj, obj_in=obj_in)

    def delete_driver(self, db: Session, driver_id: UUID) -> bool:
        self.get_driver(db, driver_id=driver_id)
        return crud_driver.delete(db, driver_id=driver_id)


master_data_service = MasterDataService()
