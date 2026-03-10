import serial
import time

# open serial port
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
    timeout=1
)

time.sleep(2)

# example command
command = b'/1ZR\r'   # reset syringe drive
ser.write(command)

response = ser.readline()
print(response)

def move_pump(steps):
    cmd = f'/1MD{steps}\r'.encode()
    ser.write(cmd)
    response = ser.readline().decode().strip()
    print("Pump response:", response)

# Example: move 500 steps
move_pump(500)

status_command = b'/1TS\r'  # 'TS' = Trigger Status
ser.write(status_command)
status = ser.readline().decode().strip()
print("Pump status:", status)


ser.close()
