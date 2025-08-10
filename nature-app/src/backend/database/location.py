from models import Locations
from sqlmodel import Session


class LocationAccess:
    async def create_location(self, session: Session, bbox: list) -> int:
        location = Locations(area=str(bbox))
        session.add(location)
        await session.commit()
        await session.refresh(location)
        return location.location_id

