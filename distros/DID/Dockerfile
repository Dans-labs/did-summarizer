#FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7-2019-10-15
FROM tiangolo/uvicorn-gunicorn-fastapi
RUN apt update
RUN apt-get -y install curl gnupg
RUN curl -sL https://deb.nodesource.com/setup_14.x  | bash -
RUN apt-get -y install poppler-utils nodejs wget bash vim git nodejs jq
RUN pip install nltk
RUN pip install textacy

RUN npm install -g wikidata-taxonomy
RUN npm install -g wikibase-cli
COPY ./app /app
COPY ./app/app.py /app/main.py
RUN pip install -r /app/requirements.txt

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update && apt-get -y install yarn
RUN git clone https://github.com/CLARIAH/vocabulary-recommender
RUN cd vocabulary-recommender;yarn;yarn build
