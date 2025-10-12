.PHONY: help setup dev build deploy clean test

help:
	@echo "TerraGuard AI - Available Commands:"
	@echo "  make setup     - Initial project setup"
	@echo "  make dev       - Run development environment"
	@echo "  make build     - Build Docker images"
	@echo "  make deploy    - Deploy to production"
	@echo "  make test      - Run tests"
	@echo "  make clean     - Clean up containers"

setup:
	@echo "Setting up TerraGuard AI..."
	@./setup.sh

dev:
	@echo "Starting development environment..."
	docker-compose up --build

build:
	@echo "Building Docker images..."
	docker-compose build

deploy:
	@echo "Deploying to production..."
	docker-compose -f docker-compose.prod.yml up -d

test:
	@echo "Running tests..."
	cd backend && pytest tests/ -v
	cd frontend && npm test

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	docker system prune -f
