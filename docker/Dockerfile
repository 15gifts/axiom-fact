# -- Pull the python 3.12 slim image
FROM python:3.12-slim

# -- Fetch CodeArtifact details from the parent environment
ARG CODEARTIFACT_AUTH_TOKEN

# -- Ensure python logs are sent straight to the terminal in real time
ENV PYTHONUNBUFFERED=1 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  # POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=1.8.0 \
  POETRY_REQUESTS_TIMEOUT=1000

# -- Install curl
RUN apt-get update \
    && apt-get install -y curl

RUN curl -sSL https://install.python-poetry.org | python3.12

# Set working directory
WORKDIR /code
# - Copy the poetry.lock and pyproject.toml
COPY poetry.lock pyproject.toml /code/

# install our dependencies
RUN poetry config http-basic.aws aws $CODEARTIFACT_AUTH_TOKEN
RUN poetry install
#RUN --mount=type=cache,target=/root/.cache poetry install

# Download the Spacy en_core_web_sm model
RUN python -m spacy download en_core_web_sm

# -- Copy the application code
COPY ./app /code/app

# Download the AlignScore base checkpoint
RUN mkdir /code/models
RUN cd /code/models && curl -OL https://huggingface.co/yzha/AlignScore/resolve/main/AlignScore-base.ckpt
RUN ls
RUN python -m pytorch_lightning.utilities.upgrade_checkpoint /code/models/AlignScore-base.ckpt
RUN cd /code

# Uncomment the line below to also download the large model
# RUN mkdir /code/models
# RUN cd /code/models && curl -OL https://huggingface.co/yzha/AlignScore/resolve/main/AlignScore-large.ckpt
# RUN python -m pytorch_lightning.utilities.upgrade_checkpoint AlignScore-large.ckpt
# RUN cd /code

# Download the punkt model to speed up start time
RUN python -c "import nltk; nltk.download('punkt')"
