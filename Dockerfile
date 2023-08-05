FROM keymetrics/pm2:18-alpine
WORKDIR /app

# Install Python and other utilities
RUN apk add --no-cache --update alpine-sdk git wget python3 python3-dev ca-certificates musl-dev libc-dev gcc bash nano linux-headers && \
    python3 -m ensurepip && \
    pip3 install --no-cache-dir --upgrade pip setuptools

# Copy requirements.txt from build machine to WORKDIR (/app) folder (important we do this BEFORE copying the rest of the files to avoid re-running pip install on every code change)
COPY requirements.txt requirements.txt

# Install Python requirements
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy source code from build machine to WORKDIR (/app) folder
COPY . .

# Delete unnecessary files in WORKDIR (/app) folder (not caught by .dockerignore)
RUN echo "**** removing unneeded files ****"
RUN rm -rf /app/requirements.txt

# Run the app
CMD [ "pm2-runtime", "start", "ecosystem.config.json" ]
