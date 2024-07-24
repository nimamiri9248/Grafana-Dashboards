#!/bin/bash

# Function to run a script in the background and log output
run_in_background() {
  local script_name=$1
  nohup setsid python "$script_name" > "logs/${script_name}.log" 2>&1 &
}

# Navigate to the scripts directory
cd scripts || exit
rm -rf venv

# Create a virtual environment
python3 -m venv venv
if [ $? -ne 0 ]; then
  echo "Failed to create virtual environment"
  exit 1
fi

# Activate the virtual environment
source venv/bin/activate
if [ $? -ne 0 ]; then
  echo "Failed to activate virtual environment"
  exit 1
fi

# Install dependencies
pip install -r requirements.txt
if [ $? -ne 0 ]; then
  echo "Failed to install dependencies"
  exit 1
fi

# Ensure logs directory exists
mkdir -p logs

# Run the three server scripts in the background
run_in_background "user_exporter.py"
run_in_background "network_exporter.py"
run_in_background "hardware_exporter.py"
run_in_background "process_exporter.py"
run_in_background "log_exporter.py"
run_in_background "load_monitor.py"
run_in_background "website_monitor.py"
# Navigate back to the project root
cd ..

# Run Docker Compose
docker compose up -d
if [ $? -ne 0 ]; then
  echo "Failed to start Docker Compose"
  exit 1
fi

echo "Scripts are running in the background. Logs can be found in the logs directory."

