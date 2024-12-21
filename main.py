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
#fcntl.flock(lock.fileno(), fcntl.F_GETLK)
fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB) # exclusive lock
lock.write(str(os.getpid()))
lock.flush()
import RPi.GPIO as GPIO
import traceback
import keyboard
print("Starting robot")
GPIO.setmode(GPIO.BOARD)

try:
    motorLeft = MotorController(32, 38, 40)
    motorRight = MotorController(12, 18, 16)
    #motorLeft.forward(25)
    #motorRight.forward(25)
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
