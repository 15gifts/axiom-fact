import os

from fastapi import FastAPI, Request

from app import __version__ as app_version
from app.alignscore import AlignScore
from app.api.config import Settings
from app.api.logging.logger import configure_logger
from app.api.request_model import FactCheckingRequest
from app.api.response_model import FactCheckingResponse

app = FastAPI(title="FACT", version=app_version)


@app.on_event("startup")
async def startup():
    logger = configure_logger()
    app.logger = logger
    settings = Settings()
    logger.info("✨\tStarting up the application")
    logger.debug("🔧\tLoading the AlignScore model from 'models/AlignScore-base.ckpt'")
    app.scorer = AlignScore(
        model=settings.model_name,
        batch_size=32,
        device=settings.device,
        ckpt_path=os.path.join(settings.path_to_model_checkpoint),
        evaluation_mode="nli_sp",
        verbose=False,
    )
    logger.info("🎉\tFACT application is ready to receive requests.")


@app.post("/run_fact")
def score_claim(
    fact_checking_request: FactCheckingRequest,
    request: Request,
):
    logger = request.app.logger
    context = fact_checking_request.context
    claim = fact_checking_request.claim
    logger.info(
        f'🔎\tReceived a request to fact-check the claim "{claim}" against the context "{context}"'
    )
    scores = request.app.scorer.score(contexts=[context], claims=[claim])
    return FactCheckingResponse(
        request=fact_checking_request, fact_checking_score=scores[0]
    )


# TODO: Add a route to get the model's metadata, e.g. the model's name, version, and description.
