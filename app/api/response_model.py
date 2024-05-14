from pydantic import BaseModel, Field

from app.api.request_model import FactCheckingRequest

class FactCheckingResponse(BaseModel):
    request: FactCheckingRequest = Field(
        ...,
        title='FactCheckingRequest',
        description='The request object received.'
    )
    fact_checking_score: float