# Logplotter - a realtime data stream plotter

[![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/flask-2.x-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Flask-SocketIO Version](https://img.shields.io/badge/flask--socketio-5.x-orange.svg)](https://flask-socketio.readthedocs.io/)
[![Plotly.js Version](https://img.shields.io/badge/plotly.js-2.x-brightgreen.svg)](https://plotly.com/javascript/)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

## 📊 Overview

This project provides a simple yet powerful web-based application for visualizing real-time streaming numerical data. It leverages Flask as a backend server to watch a local log file for changes and Flask-SocketIO for WebSocket communication to push new data to the frontend. The client-side, built with HTML, JavaScript, and Plotly.js, displays the data as an interactive scatter plot, offering zoom, pan, and reset functionalities.

This system is ideal for monitoring sensor readings, log file metrics, or any application where continuous, live data visualization is beneficial.

## ✨ Features

* **Real-time Data Streaming:** Utilizes WebSockets (via Flask-SocketIO) for efficient, low-latency data transfer from server to client.
* **File Monitoring:** The Flask backend uses `watchdog` to detect changes in a specified log file, simulating a live data source.
* **Interactive Plotting:** Plotly.js on the frontend provides a dynamic scatter plot with built-in:
    * Zoom (mouse wheel, drag-box)
    * Pan (drag)
    * Reset view
    * Hover tooltips for data points.
* **Cross-platform Compatibility:** Designed to run on various operating systems where Python and modern web browsers are supported.
* **Clear Data Format:** Explicit handling of numerical data points for sequential plotting.

## 🚀 Getting Started

Follow these steps to get the project up and running on your local machine.

### Prerequisites

* Python 3.x (recommended 3.8+)
* `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:oysteijo/logplotter.git
    cd logplotter
    ```

2.  **Create and activate a Python virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```

3.  **Install the required Python packages:**
    Install the packages listed in the `requirements.txt` file in your project's root directory. It should have the following content:
    ```
    Flask
    Flask-SocketIO
    watchdog
    ```
    Then, install them:
    ```bash
    pip install -r requirements.txt
    ```
    **Warning:** I tried this on several systems Ubuntu, Arch Linux, RedHat EL, but it seems to me that
    there are some problems if you install Flask and Flask-SocketIO from system packages (`.rpm`, `.deb`, pacman). It is
    therefore strongly recommended that you use a virtual environment.

## 🛠️ Usage

1.  **Prepare your data source:**
    The `app.py` is configured to monitor a file named `test_data.log` (you can change this filename in `app.py`).
    You can create this file:
    ```bash
    touch test_data.log
    ```
    To simulate live data, you can append numerical values to this file. For example, open it in a text editor and add numbers, or use `echo`:
    ```bash
    echo "12.34" >> test_data.log
    echo "15.67" >> test_data.log
    # ... and so on
    ```
    Each new line added to `test_data.log` should contain a single numerical value.

2.  **Run the Flask server:**
    ```bash
    python app.py test_data.log --debug
    ```
    The server will start, typically on `http://127.0.0.1:5000`. You will see logging messages indicating the server's activity and when data points are sent.

3.  **Open the client in your web browser:**
    Navigate to `http://127.0.0.1:5000` in your preferred web browser.
    The plot will load. Any data already in `test_data.log` will be displayed as "initial data."

4.  **Observe real-time updates:**
    As you append new numerical values to `test_data.log` (e.g., using `echo "20.1" >> test_data.log`), you will see the plot update in real-time in your browser.
    Use your mouse to zoom, pan, and interact with the Plotly.js chart. Click "Reset View" to revert to the initial zoom level.

## ⚙️ Data Format (Server to Client)

The system expects numerical data points for plotting.

* **`initial_data` event:** Sends an array of historical numerical values (e.g., `[10.5, 12.3, 11.8, 15.0]`). The client plots these sequentially, using the array index as the X-axis value.
* **`new_data` event:** Sends a single numerical value (e.g., `20.1`). The client appends this value to the existing data, incrementing the X-axis index.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/[Your-GitHub-Username]/[your-repo-name]/issues).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

* [Flask](https://flask.palletsprojects.com/)
* [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
* [watchdog](https://python-watchdog.readthedocs.io/)
* [Plotly.js](https://plotly.com/javascript/)
* [Socket.IO](https://socket.io/)
