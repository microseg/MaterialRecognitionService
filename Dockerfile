FROM public.ecr.aws/docker/library/python:3.11-slim

# Install system dependencies including git
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir gunicorn==21.2.0

COPY . /app

ENV PORT=5000
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "300", "app:app"]


