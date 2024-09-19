## THE OFFICIAL PYTHON 3.11
FROM python:3.11-slim

## SET WORKING DIRECTORY TO /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY ./app /app

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the Streamlit app from the 'app' folder
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
