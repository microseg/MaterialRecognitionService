FROM public.ecr.aws/docker/library/python:3.11-slim

# Install system dependencies including git
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install PyTorch first (CPU version for simplicity)
RUN pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1

# Install MultiScaleDeformableAttention (CPU version)
RUN pip install --extra-index-url https://miropsota.github.io/torch_packages_builder MultiScaleDeformableAttention==1.0+9b0651cpt2.5.1cpu

# Install Detectron2 (CPU version)
RUN pip install --extra-index-url https://miropsota.github.io/torch_packages_builder detectron2==0.6+2a420edpt2.5.1cpu

# Install other required packages
RUN pip install git+https://github.com/cocodataset/panopticapi.git@7bb4655548f98f3fedc07bf37e9040a992b054b0 \
    && pip install git+https://github.com/mcordts/cityscapesScripts.git@067792b80e446e809dd5516ee80d39fa92e18269

# Clone MaskTerial repository
RUN git clone https://github.com/Jaluus/MaskTerial.git /opt/maskterial

# Install MaskTerial
RUN pip install -e /opt/maskterial/

# Install Flask and other web dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir gunicorn==21.2.0

# Copy application code
COPY . /app

ENV PORT=5000
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "300", "app:app"]


