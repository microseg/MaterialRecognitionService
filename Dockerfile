FROM public.ecr.aws/docker/library/python:3.11-slim

# Install system dependencies including git, wget, unzip, and minimal OpenCV dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    make \
    wget \
    unzip \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgthread-2.0-0 \
    libgtk-3-0 \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libopenblas-dev \
    gfortran \
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

# Create model directory
RUN mkdir -p /opt/maskterial/models

# Download pre-trained models from Zenodo
# Using a few key models for different materials
RUN cd /opt/maskterial/models && \
    # Download segmentation models (SEG_M2F_*)
    wget -O SEG_M2F_GrapheneH.zip "https://zenodo.org/records/15765516/files/SEG_M2F_GrapheneH.zip?download=1" && \
    wget -O SEG_M2F_GrapheneL.zip "https://zenodo.org/records/15765516/files/SEG_M2F_GrapheneL.zip?download=1" && \
    wget -O SEG_M2F_hBN_Thin.zip "https://zenodo.org/records/15765516/files/SEG_M2F_hBN_Thin.zip?download=1" && \
    wget -O SEG_M2F_WS2.zip "https://zenodo.org/records/15765516/files/SEG_M2F_WS2.zip?download=1" && \
    # Download classification models (CLS_AMM_*)
    wget -O CLS_AMM_GrapheneH.zip "https://zenodo.org/records/15765516/files/CLS_AMM_GrapheneH.zip?download=1" && \
    wget -O CLS_AMM_GrapheneL.zip "https://zenodo.org/records/15765516/files/CLS_AMM_GrapheneL.zip?download=1" && \
    wget -O CLS_AMM_hBN_Thin.zip "https://zenodo.org/records/15765516/files/CLS_AMM_hBN_Thin.zip?download=1" && \
    wget -O CLS_AMM_WS2.zip "https://zenodo.org/records/15765516/files/CLS_AMM_WS2.zip?download=1" && \
    # Extract all models
    unzip -o SEG_M2F_GrapheneH.zip && \
    unzip -o SEG_M2F_GrapheneL.zip && \
    unzip -o SEG_M2F_hBN_Thin.zip && \
    unzip -o SEG_M2F_WS2.zip && \
    unzip -o CLS_AMM_GrapheneH.zip && \
    unzip -o CLS_AMM_GrapheneL.zip && \
    unzip -o CLS_AMM_hBN_Thin.zip && \
    unzip -o CLS_AMM_WS2.zip && \
    # Clean up zip files
    rm *.zip

# Install Flask and other web dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir gunicorn==21.2.0

# Copy application code
COPY . /app

# Set environment variables for MaskTerial
ENV MODEL_PATH=/opt/maskterial/models
ENV PORT=5000
EXPOSE 5000

# Verify models are properly set up
RUN python verify_models.py

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "300", "app:app"]


