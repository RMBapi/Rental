.PHONY: build run clean start-local up down logs

# Docker image name
IMAGE_NAME = flask-app

# Build Docker image
build:
	docker build -t $(IMAGE_NAME) .

# Run Docker container
run:
	docker run -p 5000:5000 $(IMAGE_NAME)

# Clean Docker resources
clean:
	docker stop $$(docker ps -a -q --filter ancestor=$(IMAGE_NAME)) 2>/dev/null || true
	docker rm $$(docker ps -a -q --filter ancestor=$(IMAGE_NAME)) 2>/dev/null || true
	docker rmi $(IMAGE_NAME) 2>/dev/null || true

# Start Flask server locally
start-local:
	flask run --host=0.0.0.0

# Docker Compose commands
up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f 