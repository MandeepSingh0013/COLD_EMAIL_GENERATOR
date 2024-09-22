# ## THE OFFICIAL PYTHON 3.11
# FROM python:3.11-slim

# ## SET WORKING DIRECTORY TO /app
# WORKDIR /app

# # Copy the requirements file into the container
# COPY requirements.txt .

# # Install dependencies
# RUN pip install --upgrade pip && pip install -r requirements.txt

# # Copy the rest of the application code into the container
# COPY ./app /app

# # Expose the port Streamlit runs on
# EXPOSE 8501

# # Set environment variables to allow external access
# ENV STREAMLIT_SERVER_HEADLESS=true
# ENV STREAMLIT_SERVER_ENABLECORS=false
# ENV STREAMLIT_SERVER_ENABLEWEBBROWSER=false

# # Command to run the Streamlit app from the 'app' folder
# CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]

## Use the official Python 3.9 image
FROM python:3.11

# Set working directory to /code
WORKDIR /code

# Copy the requirements file to the working directory
COPY ./requirements.txt /code/

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application code into the container
COPY ./app /code/

# Set a new user named "user"
RUN useradd user

# Switch to the new user
USER user

# Set home to the user's home directory and add to PATH
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Copy the current directory into the container at $HOME/app, setting the owner to the user
COPY --chown=user . $HOME/app

# Expose port 8501 for Streamlit
EXPOSE 8501

# Start the Streamlit app on the port 8501
CMD ["streamlit", "run", "app/main.py", "--server.port=8080", "--server.address=0.0.0.0"]
