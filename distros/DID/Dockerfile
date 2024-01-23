FROM tiangolo/uvicorn-gunicorn-fastapi
RUN apt update
#RUN apt-get -y install curl gnupg
#RUN curl -sL https://deb.nodesource.com/setup_18.x  | bash -
RUN apt-get -y install poppler-utils wget bash vim git jq ca-certificates curl gnupg 
RUN mkdir -p /etc/apt/keyrings
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
#RUN NODE_MAJOR=18;export NODE_MAJOR
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_21.x nodistro main" > /etc/apt/sources.list.d/nodesource.list
RUN apt-get update
RUN apt-get -y install --no-install-recommends nodejs --fix-missing
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
