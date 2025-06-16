# logplotter 

logplotter is a tool to plot logfiles. Typically is you are logging some value
in some other process or if you are training some neural network or other machine
learning model, it is nice to have plot of the development of the interesting value
ie. the loss function value metric or whatever you are measuring.

## How it works

This system sets up a inotify signal on the logfile you want to plot. It uses the watchdog
package to watch over changes in a file. This can be slow if it is a remote system.

It then sets up a Flask application server and sets up a WebSocket connection between the
server and the client. The client makes a plot using ~~chart.js~~ plotly.

## Install

This is ment as a starting point for your specific task, so the edges are a bit rough!
I tried this on several systems Ubuntu, Arch Linux, RedHat EL, but it seems to me that
there are some problems if you install Flask and Flask-SocketIO from packages. It is
therefore strongly recommended that you use a virtual environment.

```shell
python -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install Flask Flask-SocketIO watchdog

# Then start the app server
python app.py
```

So, since this is ment as a starting point, the logfile name and the way to parse the
file is hardcoded into the app.py file you hence have to modify it to suit your need.

