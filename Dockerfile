#
# HOWTO:
#
# 1.  build the container:  docker build -t phone-mgr .
#
# 2.  run the container:  docker run -it -v phone_data:/data phone-mgr


FROM python:3.12-slim

# prevent Python from buffering stdout (important for CLI UX)
ENV PYTHONUNBUFFERED=1

# create app directory inside the container
WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
# it is called phone.py and not app.py
COPY phone.py .

# create a directory for the SQLite DB
RUN mkdir -p /data

# tell SQLite where to live
ENV SQLITE_DB_PATH=/data/phones.db

# default command (interactive CLI)
# again, the main file is called phone.py and not app.py
CMD ["python", "phone.py"]
