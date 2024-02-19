

# Use a base image (e.g., a lightweight Linux distribution)
FROM alpine:latest

Copy . /build
# Metadata indicating the maintainer of the image
LABEL maintainer="Your Name <your.email@example.com>"

# Set the working directory inside the container
WORKDIR /app

# Copy application code into the container
COPY . .

# Define environment variables (if needed)
# ENV KEY=value

# Expose the port(s) the application listens on
# EXPOSE 80

# Define the command to run your application
CMD ["echo", "Hello, Docker!"]