FROM python:3.9-alpine

LABEL "com.github.actions.name"="Annotate PR with pytest coverage report"
LABEL "com.github.actions.description"="GitHub Action to run pytest on your PR and add coverage report to your PR"
LABEL "com.github.actions.icon"="shield"
LABEL "com.github.actions.color"="yellow"
LABEL "com.github.actions.repository"="https://github.com/amitds1997/python-coverage"
LABEL "com.github.actions.homepage"="https://github.com/amitds1997/python-coverage"
LABEL "com.github.actions.maintainer"="Amit Singh"

RUN apk add --no-cache git bash jq curl
RUN pip install --upgrade pip
RUN pip install pytest coverage requests

COPY src /src
CMD ["/src/entrypoint.sh"]
