FROM python:3.12-alpine as base

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

FROM base as python-deps

ENV PYTHONUNBUFFERED 1
RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .
ENV PIPENV_VENV_IN_PROJECT=1
RUN pipenv install --deploy

FROM base AS runtime

COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

WORKDIR app
COPY . .
RUN touch logs

EXPOSE 8888

LABEL authors="chojo"

ENTRYPOINT ["python", "src/main.py", "-c", "/app/config/config.json", "-l", "/app/config/logging.json"]
