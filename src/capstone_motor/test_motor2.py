import RPi.GPIO as GPIO
import time
from motors import Robot

# 定义第二个电机的引脚
pins1 = [17,18,27,22]
pins2 = [23,24,25,16]
robot = Robot(pins1, pins2)
delay = 0.002

# 步进序列（与你的代码一致）
# seq = [
#     [1,0,0,1],
#     [1,0,0,0],
#     [1,1,0,0],
#     [0,1,0,0],
#     [0,1,1,0],
#     [0,0,1,0],
#     [0,0,1,1],
#     [0,0,0,1]
# ]

# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)

# for pin in pins:
#     GPIO.setup(pin, GPIO.OUT)
#     GPIO.output(pin, GPIO.LOW)

# def step_once(direction=1):
#     steps = seq if direction == 1 else reversed(seq)
#     for step in steps:
#         for i, pin in enumerate(pins):
#             GPIO.output(pin, step[i])
#         time.sleep(delay)

# def rotate(steps, direction=1):
#     for _ in range(steps):
#         step_once(direction)

try:
    print("Testing motor1: forward 90 degrees...")
    # rotate(1024, direction=1)
    robot.step_motor2.rotate_degress(60, 1)
    print("Done.")
except KeyboardInterrupt:
    print("Interrupted")
finally:
    # for pin in pins:
    #     GPIO.output(pin, GPIO.LOW)
    # GPIO.cleanup()
    robot.cleanup_all()