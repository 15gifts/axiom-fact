from pydantic import BaseModel, Field


class FactCheckingRequest(BaseModel):
    context: str = Field(
        ...,
        title="Context",
        description="The context against which the claim is to be fact-checked.",
    )
    claim: str = Field(
        ...,
        title="Claim",
        description="The claim to be fact-checked against the context.",
    )
