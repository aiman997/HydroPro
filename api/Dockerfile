FROM python:3.12

# Install curl for healthchecks
RUN apt install curl gcc

# Setup a nonroot user for security
RUN adduser nonroot
USER nonroot

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir --upgrade -r requirements.txt

# Expose the app's port
EXPOSE 8000

WORKDIR /app
# Run the FastAPI server
ENTRYPOINT ["python", "-m"] 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "trace"]
