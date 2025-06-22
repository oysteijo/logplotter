from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time
import threading
import logging
import sys

debug = True if "--debug" in sys.argv else False
if debug: 
    print("Adding logging features")
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.getLogger('flask_socketio').setLevel(logging.DEBUG)
    logging.getLogger('engineio').setLevel(logging.DEBUG)
    logging.getLogger('socketio').setLevel(logging.DEBUG)

app = Flask(__name__)

# IMPORTANT: Replace 'your_secret_key_here' with a strong, random key in production
#app.config['SECRET_KEY'] = 'a_random_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*") # Allow all origins for development, restrict in production

DATA_FILE = sys.argv[1] 
#DATA_FILE = './classic-td.log' # Path to your data file on the server
print("DATA_FILE: ", DATA_FILE)

# A simple list to hold already sent data, useful for initial plot
# This will be populated by the event handler on startup.
initial_data_points = []
# Create an instance of the event handler early to manage read position and initial data
# We'll pass this instance to the observer
file_event_handler = None # Will be initialized before app.run

# --- Watchdog Event Handler ---
class DataFileEventHandler(FileSystemEventHandler):
    def __init__(self, socketio_instance):
        super().__init__()
        self.socketio = socketio_instance
        self.last_read_position = 0 # Stores byte offset

        # Initialize last_read_position and initial_data_points
        self._initialize_read_position_and_data()

    def _initialize_read_position_and_data(self):
        #global initial_data_points
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                content = f.read() # Read entire content for initial load
                self.last_read_position = f.tell() # Get current file pointer (end of file)

                # Parse initial data for clients connecting later
                initial_data_points.clear() # Clear any previous data if re-initializing
                for line in content.splitlines():
                    line = line.strip()
                    if line:
                        try:
                            initial_data_points.append(float(line.split()[4]))
                        except ValueError:
                            pass # Skip malformed lines
            print(f"Initialized read position to {self.last_read_position} bytes.")
            print(f"Loaded {len(initial_data_points)} initial data points.")
        else:
            print(f"Warning: Data file '{DATA_FILE}' not found. Creating it.")
            open(DATA_FILE, 'a').close() # Create the file if it doesn't exist
            self.last_read_position = 0 # File is empty

    def on_modified(self, event):
        print("I got an MODIFIED event!")
        if not event.is_directory and event.src_path == DATA_FILE:
            # We add a small delay to ensure the file write operation is complete
            # This is a common workaround for inotify events sometimes firing prematurely
            print(f"[{time.time():.2f}] Watchdog fired for: {event.src_path}")
            time.sleep(0.1)

            print(f"File modified: {event.src_path}")
            new_lines = self._read_new_data()
            if new_lines:
                print(f"New data to emit: {new_lines}")
                # Emit new data to all connected clients
                # emit('new_data', {'data': new_lines}, broadcast=True)
                self.socketio.emit('new_data', {'data': new_lines})

    def _read_new_data(self):
        new_data_points = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                # Get current size of the file
                f.seek(0, os.SEEK_END)
                current_file_end = f.tell()

                # If the file has shrunk (e.g., truncated), reset position
                if current_file_end < self.last_read_position:
                    print("File truncated. Resetting read position.")
                    self.last_read_position = 0
                    # For a truncated file, you might want to re-send all data
                    # For now, we'll just read from the start if truncated
                    f.seek(0)
                    # And also clear initial_data_points and re-populate
                    # This could lead to a momentary empty plot, but ensures consistency
                    initial_data_points.clear()
                    print("Initial data points cleared due to truncation.")

                # Seek to the last known read position
                f.seek(self.last_read_position)

                new_content = f.read() # Read only the new content

                # Update the last read position to the new end of the file
                self.last_read_position = f.tell()

                for line in new_content.splitlines():
                    line = line.strip()
                    if line:
                        try:
                            val = float(line.split()[4])
                            print("value read: ", val)
                            new_data_points.append(val)
                            # Also append to initial_data_points for new clients
                            initial_data_points.append(val)
                        except ValueError:
                            print(f"Skipping malformed line: '{line}'")
                            pass
        return new_data_points

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

# Socket.IO event handlers
@socketio.on('connect')
def test_connect():
    print('Client connected')
    # When a new client connects, send them the current historical data
    # This ensures they don't start with an empty plot
    emit('initial_data', {'data': initial_data_points})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

# --- Watchdog Thread Setup ---
def start_file_monitoring(socketio_instance, event_handler_instance):
    observer = Observer()
    # Schedule the handler for the DATA_FILE within the current directory
    # Watchdog monitors the directory, but the event handler filters for DATA_FILE
    observer.schedule(event_handler_instance, path=os.path.dirname(os.path.abspath(DATA_FILE)), recursive=False)
    observer.start()
    print("Watchdog observer started in background thread.")
    try:
        while True:
            time.sleep(0.1) # Keep the thread alive
    except KeyboardInterrupt:
        observer.stop()
        print("Watchdog observer stopped.")
    observer.join()


if __name__ == '__main__':
    # Initialize the event handler which also populates initial_data_points
    # This must happen before the Flask app starts running and serving requests
    file_event_handler = DataFileEventHandler(socketio)


    # Start the watchdog observer in a separate thread
    # Pass the socketio instance and the event handler instance
    thread = threading.Thread(target=start_file_monitoring, args=(socketio, file_event_handler))
    thread.daemon = True # Allow the thread to exit when the main program exits
    thread.start()

    # Run the Flask-SocketIO application
    print(f"[{time.time():.2f}] Starting Flask-SocketIO app with use_reloader=False", end="")
    print("{}".format(" and DEBUG logging..." if debug else " ..."))
    socketio.run(app, debug=debug, use_reloader=False)
