# Makefile for Jobs Mail Sender

# Variables
PYTHON := python
PIP := pip
BACKEND_DIR := backend
FRONTEND_DIR := frontend
PROJECT_ROOT := .

# Default target
.PHONY: help
help:
	@echo "Jobs Mail Sender - Makefile Commands"
	@echo "=========================================="
	@echo "make setup              - Install all dependencies"
	@echo "make setup-backend      - Install backend dependencies"
	@echo "make setup-frontend     - Install frontend dependencies"
	@echo "make run-backend        - Start the backend server"
	@echo "make run-frontend       - Start the frontend development server"
	@echo "make run-jobs           - Run job processing (dry run by default)"
	@echo "make run-jobs-send      - Run job processing and send emails"
	@echo "make build-docker       - Build Docker image"
	@echo "make run-docker         - Run with Docker Compose"
	@echo "make run-docker-dev     - Run with Docker Compose in development mode"
	@echo "make run-docker-prod    - Run with Docker Compose in production mode"
	@echo "make clean              - Clean temporary files"
	@echo "make test               - Run tests"
	@echo "make help               - Show this help message"

# Setup commands
.PHONY: setup
setup: setup-backend setup-frontend
	@echo "✅ All dependencies installed"

.PHONY: setup-backend
setup-backend:
	@echo "📦 Installing backend dependencies..."
	$(PIP) install -r $(BACKEND_DIR)/requirements.txt
	@echo "✅ Backend dependencies installed"

.PHONY: setup-frontend
setup-frontend:
	@echo "📦 Installing frontend dependencies..."
	cd $(FRONTEND_DIR) && npm install
	@echo "✅ Frontend dependencies installed"

# Run commands
.PHONY: run-backend
run-backend:
	@echo "🚀 Starting backend server..."
	cd $(BACKEND_DIR) && $(PYTHON) server.py

.PHONY: run-frontend
run-frontend:
	@echo "🚀 Starting frontend development server..."
	cd $(FRONTEND_DIR) && npm run dev

.PHONY: run-jobs
run-jobs:
	@echo "📋 Running job processing (dry run)..."
	cd $(BACKEND_DIR) && $(PYTHON) main.py

.PHONY: run-jobs-send
run-jobs-send:
	@echo "📧 Running job processing and sending emails..."
	cd $(BACKEND_DIR) && $(PYTHON) main.py --send

# Docker commands
.PHONY: build-docker
build-docker:
	@echo "🐳 Building Docker image..."
	docker build -t jobs-mail-sender .

.PHONY: run-docker
run-docker: build-docker
	@echo "🐳 Running with Docker Compose..."
	docker build -t jobs-mail-sender .
	docker-compose up -d

.PHONY: run-docker-dev
run-docker-dev: build-docker
	@echo "🐳 Running with Docker Compose in development mode..."
	docker-compose -f docker-compose.yml up --build

.PHONY: run-docker-prod
run-docker-prod: build-docker
	@echo "🐳 Running with Docker Compose in production mode..."
	docker-compose -f docker-compose.yml up -d

.PHONY: stop-docker
stop-docker:
	@echo "🛑 Stopping Docker containers..."
	docker-compose down

# Clean commands
.PHONY: clean
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name ".pytest_cache" -type d -exec rm -rf {} +
	rm -f *.log
	@echo "✅ Clean completed"

# Test commands
.PHONY: test
test:
	@echo "🧪 Running tests..."
	cd $(BACKEND_DIR) && $(PYTHON) test_motivational_letter.py
	cd $(BACKEND_DIR) && $(PYTHON) ../test_docker_setup.py

.PHONY: test-motivational-letter
test-motivational-letter:
	@echo "🧪 Testing motivational letter generation..."
	cd $(BACKEND_DIR) && $(PYTHON) test_motivational_letter.py

.PHONY: test-docker
test-docker:
	@echo "🧪 Testing Docker setup..."
	cd $(BACKEND_DIR) && $(PYTHON) ../test_docker_setup.py

# Utility commands
.PHONY: env-example
env-example:
	@echo "📝 Creating .env file from example..."
	cp .env.example .env
	@echo "✅ .env file created. Please edit it with your configuration."

.PHONY: check-requirements
check-requirements:
	@echo "📋 Checking requirements..."
	$(PYTHON) -c "import sys; print('Python version:', sys.version)"
	$(PIP) list

.PHONY: logs
logs:
	@echo "📋 Displaying recent logs..."
	@if [ -f "email_log.xlsx" ]; then \
		echo "Email log file exists: email_log.xlsx"; \
	else \
		echo "No email log file found"; \
	fi

# Install make if not available (Windows-specific)
.PHONY: install-make-windows
install-make-windows:
	@echo "Installing Make for Windows..."
	@echo "Please install Make using one of these methods:"
	@echo "1. Install Git for Windows (includes make): https://git-scm.com/download/win"
	@echo "2. Install Chocolatey and run: choco install make"
	@echo "3. Install MSYS2 and run: pacman -S make"