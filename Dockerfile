FROM python:3.13-slim

# send Python output straight to the container logs
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# copy requirements first, so Docker reuses the installed packages
# when only the source code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# build the SQLite database and load the sample catalog into the image
RUN python manage.py migrate && python manage.py loaddata sample_data

EXPOSE 8000

# 0.0.0.0 makes the server reachable from outside the container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
