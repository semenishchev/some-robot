import os
import sys
import subprocess
import fcntl
# check if we're in the first terminal and not ssh session
primary_tty = os.ttyname(sys.stdin.fileno())
if primary_tty != "/dev/tty1" and len(sys.argv) < 2:
    exit(0)
    raise Exception() # unreachable

# Check for file lock
lock = open("/root/robot.lock", "w")
fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB) # exclusive lock
lock.write(str(os.getpid()))
lock.flush()

print("Starting robot")

import RPi.GPIO as GPIO
import traceback
import keyboard
import threading
from server import webserver
from websockets.sync.server import serve
GPIO.setmode(GPIO.BOARD)
try:
    _motorLeft = MotorController(32, 38, 40)
    _motorRight = MotorController(12, 18, 16)
    #motorLeft.forward(25)
    #motorRight.forward(25)
    web = None
    def websocket_handler():
        pass
    websocket = serve(websocket_handler, host="0.0.0.0", port=3001)
    web = webserver(websocket)
    def start_websocket():
        websocket.serve_forever()
    websocket_thread = threading.Thread(target=start_websocket)
    websocket_thread.daemon = True
    websocket_thread.name = "Robot-Websocket-Thread"
    def start_webserver():
        web.run()
    server_thread = threading.Thread(target=start_webserver)
    server_thread.daemon = True
    server_thread.name = "Robot-Flask-Thread"
    server_thread.start()
    websocket_thread.start()
    print("Started robot")
    while True:
        speed = 35
        speed_turn = 25
        if keyboard.is_pressed("space"):
            speed = 100
            speed_turn = 90
        if keyboard.is_pressed("up"):
            motorRight.forward(speed)
            motorLeft.forward(speed)
        elif keyboard.is_pressed("down"):
            motorRight.backward(speed)
            motorLeft.backward(speed)
        elif keyboard.is_pressed("left"):
           motorRight.forward(speed)
           motorLeft.backward(speed_turn)
        elif keyboard.is_pressed("right"):
           motorRight.backward(speed_turn)
           motorLeft.forward(speed)
        else:
            motorRight.stop()
            motorLeft.stop()
except:
    print(traceback.format_exc())
try:
    GPIO.cleanup()
except: pass
fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
lock.close()
print("Starting internet and SSH")
subprocess.run(["/bin/bash", "/root/start_internet.sh"], stdout=sys.stdout, stderr=sys.stderr)
subprocess.run(["systemctl", "start", "ssh"], stderr=sys.stderr)
subprocess.run(["ifconfig"], stdout=sys.stdout, stderr=sys.stderr)
