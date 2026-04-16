# Build the Docker image
docker build -t talkraus/techrent-pro:latest .

# Run the container (maps host port 5000 to container port 5000)
docker run -p 5000:5000 talkraus/techrent-pro:latest

# Options for overriden environment variables (e.g., for development):
# docker run -p 5000:5000 --env-file .env talkraus/techrent-pro:latest

# Open in browser
http://localhost:5000

# Pull directly from Docker Hub
docker pull talkraus/techrent-pro:latest
