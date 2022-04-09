from fastapi import APIRouter, Depends

from api.deps import get_current_user, get_measurement
from models.measurement import Measurement
from models.ticket import Ticket
from models.user import User
from schemas.ticket import TicketInputSchema
from services.ws import WsTicketService

router = APIRouter()


@router.post("/ticket/", response_model=Ticket)
async def create_ticket(
    ticket: TicketInputSchema,
    user: User = Depends(get_current_user),
    measurement: Measurement = Depends(get_measurement),
):
    return await WsTicketService().create(user, measurement)
