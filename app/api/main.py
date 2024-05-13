from fastapi import FastAPI, Request

from typing import List

import os
import sys
sys.path.append('..')
from alignscore import AlignScore

app = FastAPI()

@app.on_event('startup')
async def startup():
    print('Starting up...')
    app.scorer = AlignScore(
        model='roberta-base',
        batch_size=32,
        device='cpu',
        ckpt_path=os.path.join('app/models/AlignScore-base.ckpt'),
        evaluation_mode='nli_sp',
        verbose=False
    )

@app.post('/score_claim/')
def score_claim(
    request: Request,
    contexts: List[str],
    claims: List[str]
):
    return {
        'score': request.app.scorer.score(
            contexts=contexts,
            claims=claims
        )
        }