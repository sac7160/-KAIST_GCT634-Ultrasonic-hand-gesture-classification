import serial
import time
import keyboard
import numpy as np
import os
import csv

from emit_controller.coordinates import num_transducers,focal_points,transducers

#이렇게 시리얼 포트 열었는데 이게 맞는건가..?되는듯 안되는듯...250430
# try:
#     ser = serial.Serial(
#         port='COM11',
#         baudrate=115200,
#         timeout=None
#     )
# except serial.SerialException as e:
#     print(f"Error opening serial port: {e}")
#     ser = None

def init():
    ser = serial.Serial(
        port='COM11',
        #baudrate=1000000,
        baudrate=115200,
        timeout=None
    )
    print("ultrasonic emit _ serial port open")
    return ser

def handle_keyboard(ser):
    if keyboard.is_pressed('f'):
        print("f is pressed!")
        generate_feedback(ser, freq=200, dur=100)   #example values
        time.sleep(0.01)
    elif keyboard.is_pressed('p'):
        generate_am_feedback(ser, freq=200, dur=100)
    elif keyboard.is_pressed('q'):
        print("Exit entire program...")
        ser.close()
        os.system("taskkill /F /IM python.exe")
    # elif keyboard.is_pressed('t'):  #ultrasound emmision test for beamforming sensing
    #     print("t is pressed!")
    #     generate_signal(ser)
    #     #time.sleep(0.01)
    # elif keyboard.is_pressed('s'):  #buffer switch
    #     send_switch_buffer_signal(ser)






SPEED_OF_SOUND = 346.0  #m/s
PORT_MAPPING = [
    51, 52, 53, 54, 28, 29, 30, 31, 47, 46, 45, 44, 43, 42, 41, 40,
    56, 57, 58, 59, 48, 49, 72, 69, 39, 38, 37, 36, 35, 34, 33, 32,
    21, 23, 65, 63, 9, 11, 13, 15, 20, 22, 64, 66, 8, 10, 12, 14,
    24, 25, 26, 27, 16, 17, 18, 19, 7, 6, 5, 4, 3, 2, 1, 0
]
modulation_frequency = {}
modulation_frequency[0] = bytearray([0xF0, 0x30, 0xB0, 0x30, 0xF0, 0x30, 0xB0, 0x30, 0xF0, 0x30, 0xB0, 0x30, 0xF0, 0x30, 0xB0, 0x30, 0x10, 0x0])    #50Hz
modulation_frequency[1] = bytearray([0xF0, 0x30, 0xB0, 0x30, 0xF0, 0x30, 0xB0, 0x30, 0x10, 0x0])    #100Hz default focal point, lm focalpoint : 2 patterns
modulation_frequency[2] = bytearray([0x70, 0xB0, 0x70, 0x30, 0x70, 0xB0, 0x70, 0x30, 0x10, 0x0])    #200Hz

#32개 1cycle씩 출력
testduration_am = bytearray([0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x10, 0x0])

duration ={}
duration[0] = bytearray([0x30, 0x70, 0x70, 0x30, 0x10, 0x0]) #0.5ms
duration[1] = bytearray([0x30, 0xF0, 0xF0, 0x30, 0x10, 0x0]) #1.5ms
testduration = bytearray([0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x10, 0x0])

testduration_2patterns = bytearray([0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x10, 0x0])
testduration_3patterns = bytearray([0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x10, 0x0])
testduration_9patterns = bytearray([0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x10, 0x0])
testduration_9patterns_V2 = bytearray([0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0,0xF0, 0xF0, 0xF0, 0xF0,0xF0, 0xF0, 0xF0, 0xF0,0xF0, 0xF0, 0xF0, 0xF0,0xF0, 0xF0, 0xF0, 0xF0,0xF0, 0xF0, 0xF0, 0xF0,0xF0, 0xF0, 0xF0, 0xF0, 0x10, 0x0])
testduration_15patterns = bytearray([0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x30, 0x70, 0x70, 0x30, 0x30, 0xF0, 0xF0, 0x30, 0x10, 0x0]) #0.5ms+1.5ms 마지막이 switch임

switch_buffer = bytearray([0x00])

stop_pattern = bytearray([0x01] * 200)
stop_durs = bytearray([0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x70, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x10, 0x00])

zeros = bytearray([0x01] * 200)

precomputed_patterns = []
precomputed_am_patterns = []

bits = np.zeros((80, 10), dtype=int)
def find_phase():
    focal_point = np.array(focal_points[0])
    distances = []  
    phases = []
    phase_delay = []

    for i in range(num_transducers):
        t_pos = np.array(transducers[i])
        distance = np.linalg.norm(t_pos - focal_point)
        distances.append(distance) # 굳이 안필요할지도

        wavelength = SPEED_OF_SOUND / 40000.0
        phase = (1.0 - ((distance / wavelength) % 1.0)) * 2.0
        phases.append(phase) # 굳이 안필요할지도

        shift = int(round((phase * 10.0 / 2.0) % 10.0)) #0~2 phase delay -> 0~9
        phase_delay.append(shift) # 굳이 안필요할지도

        default_phase = [0,0,0,0,0,1,1,1,1,1]
        left_shift_array(default_phase, shift)

        for j in range(10):
            bits[79-PORT_MAPPING[i], j] = default_phase[j]

lm_bits = np.zeros((80, 10), dtype=int)
def find_lm_phase():
    focal_point = np.array(focal_points[0]) + np.array([0.01, 0.0, 0.0])
    distances = []  
    phases = []
    phase_delay = []

    for i in range(num_transducers):
        t_pos = np.array(transducers[i])
        distance = np.linalg.norm(t_pos - focal_point)
        distances.append(distance) # 굳이 안필요할지도

        wavelength = SPEED_OF_SOUND / 40000.0
        phase = (1.0 - ((distance / wavelength) % 1.0)) * 2.0
        phases.append(phase) # 굳이 안필요할지도

        shift = int(round((phase * 10.0 / 2.0) % 10.0)) #0~2 phase delay -> 0~9
        phase_delay.append(shift) # 굳이 안필요할지도

        default_phase = [0,0,0,0,0,1,1,1,1,1]
        left_shift_array(default_phase, shift)

        for j in range(10):
            lm_bits[79-PORT_MAPPING[i], j] = default_phase[j]


def left_shift_array(arr, shift):
    shift %= len(arr)
    buffer = arr[:shift]
    for i in range(len(arr)-shift):
        arr[i] = arr[i+shift]
    for i in range(shift):
        arr[len(arr)-shift+i] = buffer[i]

lm_signal_bytes = [0] * 200
signal_bytes = [0] * 200
def get_phase_bytes(signal_type):
    if(signal_type == "lm"):
        find_lm_phase()      
        bytenum =0

        for i in range(10): #div
            for j in range(0,80,8): #ports
                bytestrA = f"{lm_bits[j, i]}{lm_bits[j+1, i]}{lm_bits[j+2, i]}{lm_bits[j+3, i]}0001"
                bytestrB = f"{lm_bits[j+4, i]}{lm_bits[j+5, i]}{lm_bits[j+6, i]}{lm_bits[j+7, i]}0001"

                lm_signal_bytes[bytenum] = int(bytestrB, 2)
                lm_signal_bytes[bytenum+1] = int(bytestrA, 2)
                bytenum += 2
        lm_signal_bytes.reverse()
    else:
        find_phase()
        bytenum = 0

        for i in range(10): #div
            for j in range(0,80,8): #ports
                bytestrA = f"{bits[j, i]}{bits[j+1, i]}{bits[j+2, i]}{bits[j+3, i]}0001"
                bytestrB = f"{bits[j+4, i]}{bits[j+5, i]}{bits[j+6, i]}{bits[j+7, i]}0001"

                signal_bytes[bytenum] = int(bytestrB, 2)
                signal_bytes[bytenum+1] = int(bytestrA, 2)
                bytenum += 2
        signal_bytes.reverse()

#####for UMH#####
def send_signal(ser, hz):
    get_phase_bytes("")
    get_phase_bytes("lm")
    ser.write(bytearray(signal_bytes))
    ser.write(bytearray(lm_signal_bytes))
    if hz == 100:
        ser.write(modulation_frequency[1])
    else:
        ser.write(modulation_frequency[2])


def stop_signal(ser):
    ser.write(stop_pattern)
    ser.write(stop_durs)
    print("stop feedback")


def generate_feedback(ser, freq, dur):
    send_signal(ser, freq)
    while True:
        if not keyboard.is_pressed('f'):
            print("finish generate_feedback")
            break
        time.sleep(0.01)
    stop_signal(ser)
####################
def generate_am_feedback(ser, freq=200, dur=100):
    #우선 패턴 32개 보냄
    for j in range (1000):  #너무 짧은 시간이라 1000번 -> 5초 반복
        tmp = bytearray()
        for i in range(32):
            tmp += bytearray(precomputed_am_patterns[i]+testduration_am)
            #ser.write(bytearray(precomputed_am_patterns[i]))
            #ser.write(testduration_am)
        print(j)
        ser.write(tmp)
        tmp = bytearray()
        for i in range(32):
            tmp += bytearray(precomputed_am_patterns[i+32]+testduration_am)
            #ser.write(bytearray(precomputed_am_patterns[i+32]))
            #ser.write(testduration_am)
        ser.write(tmp)
        tmp = bytearray()
        print(f"{j}-2")
        for i in range(32):
            tmp += bytearray(precomputed_am_patterns[i+64]+testduration_am)
            #ser.write(bytearray(precomputed_am_patterns[i+64]))
            #ser.write(testduration_am)
        ser.write(tmp)
        tmp = bytearray()
        print(f"{j}-3")
        for i in range(32):
            tmp += bytearray(precomputed_am_patterns[i+96]+testduration_am)
            # ser.write(bytearray(precomputed_am_patterns[i+96]))
            # ser.write(testduration_am)
        print(f"{j}-4")

        ser.write(tmp)
        tmp = bytearray()
        for i in range(32):
            tmp += bytearray(precomputed_am_patterns[i+128]+testduration_am)
            # ser.write(bytearray(precomputed_am_patterns[i+128]))
            # ser.write(testduration_am)
        print(f"{j}-5")
        ser.write(tmp)
        tmp = bytearray()
        for i in range(32):
            tmp += bytearray(precomputed_am_patterns[i+160]+testduration_am)
            # ser.write(bytearray(precomputed_am_patterns[i+160]))
            # ser.write(testduration_am)
        print(f"{j}-6")
        ser.write(tmp)
        print(j)
    print("signal 전송 완료")
    stop_signal(ser)
    #일단 192개 패턴을 보내보자
    # for i in range(32):
    #     ser.write(bytearray(precomputed_am_patterns[i+192]))
    #     ser.write(testduration_am)

def generate_signal(ser):
    send_beamforming_signal(ser)

def send_beamforming_signal(ser):
    get_phase_bytes("") #일단 focalpoint center 하나로 테스트
    
    # ser.write(bytearray(signal_bytes))
    # ser.write(duration[0])  #emit for 0.5ms
    # ser.write(switch_buffer)
    # ser.write(stop_pattern)
    # ser.write(duration[1])

    #first test ~25.05.11
    # ser.write(bytearray(signal_bytes))
    # print(signal_bytes)
    # ser.write(stop_pattern)
    # ser.write(testduration) # 전부 전송이 된 후에 버퍼를 switch 시켜 패턴을 출력하는것
    
    # ser.write(precomputed_patterns[0])
    # ser.write(stop_pattern)
    # ser.write(testduration)
    # time.sleep(0.01)
    # ser.write(switch_buffer)
    
    #phase precompute and test 25.05.12 
    #transmit pattern
    # for i in range(0,2):
    #     ser.write(bytearray(precomputed_patterns[i]))
    #     ser.write(stop_pattern)
    #transmit duration + transmit commit duration + switch pattern
    #ser.write(testduration_15patterns)

    #2개 패턴!!
    # ser.write(bytearray(precomputed_patterns[0]))
    # ser.write(stop_pattern)
    # ser.write(bytearray(precomputed_patterns[1]))
    # ser.write(stop_pattern)
    
    # ser.write(testduration_2patterns) #dration 끝의 switch command가 수신되고 나서야 출력하는건데 왜 2개 출력할때는 안되지?
    ser.write(bytearray(precomputed_patterns[0]))
    ser.write(stop_pattern)
    ser.write(bytearray(precomputed_patterns[1]))
    ser.write(stop_pattern)
    ser.write(bytearray(precomputed_patterns[2]))
    ser.write(stop_pattern)
    ser.write(bytearray(precomputed_patterns[3]))
    ser.write(stop_pattern)
    ser.write(bytearray(precomputed_patterns[4]))
    ser.write(stop_pattern)
    ser.write(bytearray(precomputed_patterns[5]))
    ser.write(stop_pattern)
    ser.write(bytearray(precomputed_patterns[6]))
    ser.write(stop_pattern)
    ser.write(bytearray(precomputed_patterns[7]))
    ser.write(stop_pattern)
    ser.write(bytearray(precomputed_patterns[8]))
    ser.write(stop_pattern)

    ser.write(stop_pattern)
    ser.write(stop_pattern)
    ser.write(stop_pattern)
    ser.write(stop_pattern)
    ser.write(stop_pattern)
    ser.write(stop_pattern)
    ser.write(stop_pattern)
    ser.write(stop_pattern)
    ser.write(stop_pattern)
    ser.write(stop_pattern)
    ser.write(stop_pattern)
    ser.write(stop_pattern)
    ser.write(stop_pattern)
    ser.write(stop_pattern)
 
    ser.write(testduration_9patterns_V2)

    ser.write(stop_pattern)
    ser.write(duration[1])
    
  

    # buf = bytearray()
    # buf += bytearray(precomputed_patterns[0])
    # buf += stop_pattern
    # buf += bytearray(precomputed_patterns[1])
    # buf += stop_pattern
    # buf += testduration_2patterns
    # ser.write(buf)

    #3개패턴 보내보자
    # ser.write(bytearray(precomputed_patterns[0]))
    # ser.write(stop_pattern)
    # ser.write(bytearray(precomputed_patterns[1]))
    # ser.write(stop_pattern)
    # ser.write(bytearray(precomputed_patterns[2]))
    # ser.write(stop_pattern)
    # ser.write(testduration_3patterns)

    #25.05.14. 다시 하나부터 차근차근
    # ser.write(bytearray(signal_bytes))
    # # ser.flush()
    # ser.write(stop_pattern)
    # # ser.flush()
    # ser.write(testduration)
     


def send_switch_buffer_signal(ser):
    ser.write(switch_buffer)

def load_phase_patterns_from_csv(csv_path='phase_patterns.csv'):
    global precomputed_patterns
    precomputed_patterns =[]

    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        for row in reader:
            signal = list(map(int,row[3:]))
            precomputed_patterns.append(signal)

def load_am_phase_patterns_from_csv(csv_path='phase_patterns_am.csv'):
    global precomputed_am_patterns
    precomputed_am_patterns =[]

    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        for row in reader:
            signal = list(map(int,row[3:]))
            precomputed_am_patterns.append(signal)



def emit_controller(flag_queue):
    ser = init()
    load_phase_patterns_from_csv()  #generate 27 patterns
    load_am_phase_patterns_from_csv()

    #start signal emitting and recording
    def keyboard_press_r():
        print('r is pressed!(emit_signal)')

        flag_queue.put(True)
        
        print("[Emitter] ▶ Start saving!")
        
        generate_signal(ser)
    
        # while True:
        #     print("[Emitter] Waiting saving signal")
        #     if ser.in_waiting:
        #         byte = ser.read()
                # if byte == b'\xA5':
                #     print("[Emitter] Received 0xA5 flag from Mega! ▶ Start saving!")
                #     flag_queue.put(True)  
                #     break

                #multibyte로
                # if byte == b'\xAA':  # 시작 바이트
                #     next1 = ser.read()
                #     next2 = ser.read()
                #     if next1 == b'\x55' and next2 == b'\xA5':
                #         print("[Emitter] Multi-byte flag received")
                #         flag_queue.put(True)
                #         break
                
            #time.sleep(0.001)
        
        # 총 전송 바이트: 11016 bytes
        # 총 전송 비트 수: 11016 × 10 = 110160 bits

        # 전송 시간 (초) = 110160 / 115200 ≈ 0.95625 초 ≈ 956.25 ms
        # time.sleep(0.55)
        # flag_queue.put(True)
        # print("[Emitter] ▶ Start saving!")

    def keyboard_press_s():
        print('s is pressed!')
        send_switch_buffer_signal(ser)

    def keyboard_press_z():
        print('z is pressed! Initialize!!!!')
        ser.write(bytearray([0xA9]))  # COMMAND_RESET
        ser.flush()
        time.sleep(0.01)
    
    def keyboard_press_m():
        print('m is pressed! Start 10 iterations...')
        for i in range(10):
            print(f"\n[M Sequence] Iteration {i+1}/10")

            # 1. 데이터 수집 시작
            flag_queue.put(True)
            print("[Emitter] ▶ Start saving!")
            generate_signal(ser)

            # 2. 수집 대기 (2.5초 + 여유 시간)
            time.sleep(3.0)

            # 3. 초기화
            print("[Emitter] ▶ Send reset signal (z equivalent)")
            ser.write(bytearray([0xA9]))  # COMMAND_RESET
            ser.flush()
            time.sleep(0.01)

        print("[M Sequence] All 10 iterations complete.")


    keyboard.on_press_key('r', lambda _: keyboard_press_r())
    keyboard.on_press_key('s', lambda _: keyboard_press_s())
    keyboard.on_press_key('z', lambda _: keyboard_press_z())
    keyboard.on_press_key('m', lambda _: keyboard_press_m())

    while True:
        #print("working...")
        handle_keyboard(ser)
