import RPi.GPIO as GPIO
class MotorController:
    def __init__(self, pwmPin, forwardPinLow, forwardPinHigh):
        GPIO.setup(forwardPinHigh, GPIO.OUT)
        GPIO.setup(forwardPinLow, GPIO.OUT)
        GPIO.setup(pwmPin, GPIO.OUT)
        self.forwardPinHigh = forwardPinHigh
        self.forwardPinLow = forwardPinLow
        self.pwm = GPIO.PWM(pwmPin, 300)
    def forward(self, speed):
        GPIO.output(self.forwardPinHigh, GPIO.HIGH)
        GPIO.output(self.forwardPinLow, GPIO.LOW)
        self.pwm.start(speed)
    def backward(self, speed):
        GPIO.output(self.forwardPinHigh, GPIO.LOW)
        GPIO.output(self.forwardPinLow, GPIO.HIGH)
        self.pwm.start(speed)
    def stop(self):
        self.pwm.start(0)