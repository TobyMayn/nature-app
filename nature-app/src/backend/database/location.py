from models import Location
from shapely import Polygon
from sqlmodel import Session


class LocationAccess:
    async def create_location(session: Session, polygon: Polygon) -> int:
        location = Location(polygon=polygon)
        session.add(location)
        await session.commit()
        await session.refresh(location)
        return location.location_id

