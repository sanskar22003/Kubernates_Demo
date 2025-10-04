# Import necessary modules: Flask for web app, datetime for time, random for latency simulation, logging for logs.
from flask import Flask, jsonify
import datetime
import random
import time
import logging

# Set up logging: This helps debug by printing info to console.
logging.basicConfig(level=logging.INFO)

# Create the app instance.
app = Flask(__name__)

# Global counter for requests: Simple metric to track total requests.
request_count = 0

# Function to simulate latency: Adds a random delay (0-2 seconds) to mimic real-world slowdowns.
def simulate_latency():
    delay = random.uniform(0, 2)  # Random delay in seconds.
    time.sleep(delay)
    logging.info(f"Simulated latency: {delay} seconds")

# Root endpoint: Serves a simple message.
@app.route('/')
def hello_world():
    global request_count
    request_count += 1
    simulate_latency()  # Add delay for realism.
    logging.info("Handled / request")
    return 'Hello World from our enhanced workshop!'

# /time endpoint: Returns current server time in JSON.
@app.route('/time')
def get_time():
    global request_count
    request_count += 1
    simulate_latency()
    logging.info("Handled /time request")
    current_time = datetime.datetime.now().isoformat()
    return jsonify({'time': current_time})

# /metrics endpoint: Exposes basic stats like request count.
@app.route('/metrics')
def metrics():
    global request_count
    logging.info("Handled /metrics request")
    return jsonify({'request_count': request_count})

# Run the app: Starts the server.
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)