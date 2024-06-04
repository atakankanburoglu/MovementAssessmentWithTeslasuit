import os
import signal
import sys
import time
from joblib import load
from core.DataGateway import DataGateway
from server.Server import Server
os.environ['FOR_DISABLE_CONSOLE_CTRL_HANDLER'] = '1'

dataGateway = DataGateway()
server = Server(dataGateway)

def run_program():
    server.start()

def on_exit(signum, frame):
    print("Stopping...")
    server.stop()
    print("All stopped. Exiting.")
    sys.exit(1)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, on_exit)
    run_program()
    print("Startup complete")
    while True:
        time.sleep(10)
