# Use a stable Python 3.11 image to avoid compilation freezes
FROM python:3.11

WORKDIR /code

# Install dependencies first to cache them
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Hugging Face requires running as a non-root user
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy your application files into the container
COPY --chown=user . $HOME/app

# Expose the mandatory Hugging Face port
EXPOSE 7860

# Pull ChromaDB from Dagshub, then launch Flask via Gunicorn on port 7860
CMD dvc pull && gunicorn app:app -b 0.0.0.0:7860