FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY ./app.py  .
COPY ./requirements.txt  .

RUN pip install -r requirements.txt

EXPOSE 5050

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=5050", "--server.address=0.0.0.0"]