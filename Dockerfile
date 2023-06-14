# Docker image for E4GL BFACPCloudflareSync
# Creator:  H3dius/Hedius github.com/hedius
FROM python:3

# User and Group ID of the account used for execution
ARG UID=4000
ARG GID=4000

LABEL maintainer="Hedius @ github.com/hedius" \
      description="BFACPCloudflare Access Group Sync" \
      version="1.0.0"

# account for execution of script
RUN groupadd -r -g $GID  pythonRun && \
    useradd -r -g pythonRun -u $UID pythonRun

COPY --chown=pythonRun:pythonRun src /usr/src/app
WORKDIR /usr/src/app

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt
RUN chown pythonRun:pythonRun -R /usr/src/app

USER pythonRun:pythonRun

CMD ["python3", "sync.py", "-c", "/usr/src/app/config.ini"]
