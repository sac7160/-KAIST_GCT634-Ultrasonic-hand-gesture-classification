# import time
# import serial
# import pandas as pd
# import os
# import keyboard
# from datetime import datetime

# DATA_DIR = "data"
# os.makedirs(DATA_DIR, exist_ok=True)

# BYTES_PER_SAMPLE = 7  # 1 + 4 + 2
# SAMPLES_PER_BLOCK = 1000
# DURATION_US = 2500000#18000#3_000_000 us    9 sensing frame = 9 * 2ms 18ms

# GESTURE_NAME = "extension"

# def init():
#     ser = serial.Serial(port='COM12', baudrate=2000000, timeout=1)
#     print("[Collector] Serial port open")
#     ser.write(b'R') #Teensy buffer reset
#     return ser

# def save_csv(buf, filepath):
#     df = pd.DataFrame(buf, columns=["teensy_ts_us", "readable_time", "adc_value"])
#     df.to_csv(filepath, index=False)
#     print(f"[Collector] → Saved {len(buf)} samples to {filepath}")

# def parse_samples(data, t0, duration_us, buf, visualize_queue):
#     stop = False
#     for i in range(0, len(data) - BYTES_PER_SAMPLE + 1, BYTES_PER_SAMPLE):
#         if data[i] != 0xAA:
#             continue
#         ts_us = int.from_bytes(data[i+1:i+5], 'little')
#         val = (data[i+5] << 8) | data[i+6]

#         visualize_queue.put((ts_us, 4095-val))  # 반대로 나와 4095- 추가

#         if t0 is None:
#             t0 = ts_us

#         if ts_us - t0 <= duration_us:
#             readable_time = datetime.now().isoformat()
#             buf.append((ts_us, readable_time, 4095-val)) # 반대로 나와 4095- 추가
#         else:
#             stop = True
#             break
#     return t0, stop

# def wait(ser, data_queue, start_queue, visualize_queue, flag_queue):
#     file_counter = 0

#     while True:
#         # 평상시에도 시각화용 데이터 계속 전달
#         block = ser.read(BYTES_PER_SAMPLE * SAMPLES_PER_BLOCK)
#         parse_samples(block, None, float('inf'), [], visualize_queue)

#         # r 키 입력 시 3초 수집 시작
#         # if keyboard.is_pressed('r'):
#         #     while keyboard.is_pressed('r'):
#         #         ser.write(b'R') #Teensy buffer reset
#         #         print("reset teensy buffer")
#         #         time.sleep(0.01)
        
#         if not flag_queue.empty():
#             while not flag_queue.empty():
#                 flag_queue.get()
#             # ser.write(b'R') #Teensy buffer reset
#             # print("reset teensy buffer")
#             # time.sleep(0.01)
            
#             file_counter += 1
#             print(f"[Collector] ▶ Recording 3.0s → record_{file_counter:03d}.csv …")
#             buf, t0 = [], None

#             while True:
#                 data = ser.read(BYTES_PER_SAMPLE * SAMPLES_PER_BLOCK)
#                 t0, should_stop = parse_samples(data, t0, DURATION_US, buf, visualize_queue)
#                 if should_stop:
#                     break

#             now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#             fname = os.path.join(DATA_DIR, GESTURE_NAME, f"{now_str}.csv")
#             save_csv(buf, fname)
#             index_path = os.path.join("data_index", f"{GESTURE_NAME}.csv")
#             with open(index_path, "a") as f:
#                 f.write(f"{now_str}.csv\n")
#             print(f"[Collector] ■ Recording complete: 총 {len(buf)} samples\n")

#         if not start_queue.empty():
#             seconds, filepath, is_exit = start_queue.get()
#             return seconds, filepath, is_exit

# def data_controller(data_queue, start_queue, end_queue, visualize_queue, flag_queue):
#     ser = init()
#     try:
#         while True:
#             seconds, filepath, is_exit = wait(ser, data_queue, start_queue, visualize_queue, flag_queue)
#             if is_exit:
#                 break
#     finally:
#         ser.close()


#2개 트랜스듀서 테스트
import time
import serial
import pandas as pd
import os
import keyboard
from datetime import datetime

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

BYTES_PER_SAMPLE = 9  # 1 + 4 + 2 + 2 (HEADER + timestamp + A0 + A1)
SAMPLES_PER_BLOCK = 1000#500#200#1000
DURATION_US = 2500000  # 2.5초

gesture_set = ["extension", "flexion", "spiderman", "stretch", "thumbs_up", "wrist_extension", "wrist_flexion"]
GESTURE_NAME = gesture_set[6]


def init():
    ser = serial.Serial(port='COM12', baudrate=2000000, timeout=1)
    print("[Collector_teensy1] Serial port open")
    ser.write(b'R')  # Teensy 버퍼 초기화
    return ser

def save_csv(buf, filepath):
    df = pd.DataFrame(buf, columns=["teensy_ts_us", "readable_time", "adc_val0", "adc_val1"])
    df.to_csv(filepath, index=False)
    print(f"[Collector] → Saved {len(buf)} samples to {filepath}")

def parse_samples(data, t0, duration_us, buf, visualize_queue):
    stop = False
    for i in range(0, len(data) - BYTES_PER_SAMPLE + 1, BYTES_PER_SAMPLE):
        if data[i] != 0xAA:
            continue
        ts_us = int.from_bytes(data[i+1:i+5], 'little')
        val0 = (data[i+5] << 8) | data[i+6]
        val1 = (data[i+7] << 8) | data[i+8]

        #visualize_queue.put((ts_us, 4095 - val0, 4095 - val1))  # 반전 처리

        if t0 is None:
            t0 = ts_us

        if ts_us - t0 <= duration_us:
            readable_time = datetime.now().isoformat()
            buf.append((ts_us, readable_time, 4095 - val0, 4095 - val1))
        else:
            stop = True
            break
    return t0, stop

def wait(ser, data_queue, start_queue, visualize_queue, flag_queue):
    file_counter = 0

    while True:
        # 평상시 실시간 시각화
        block = ser.read(BYTES_PER_SAMPLE * SAMPLES_PER_BLOCK)
        ##이부분 추가해봄. 자꾸 됐다 안됐다 그럼
        if len(block) < BYTES_PER_SAMPLE:
            print("[WARNING] 수신 데이터 부족. 다시 read")
            continue

        # if keyboard.is_pressed('z'):
        #     print("[Keyboard] 'z' pressed → Teensy buffer reset")
        #     ser.write(b'R')
        #     time.sleep(0.05)
        ######################################
        #parse_samples(block, None, float('inf'), [], visualize_queue)



        if not flag_queue.empty():
            # while not flag_queue.empty():
            #     flag_queue.get()
            
            file_counter += 1
            #print(f"[Collector] ▶ Recording 3.0s → record_{file_counter:03d}.csv …")
            buf, t0 = [], None

            while True:
                #print("[bf_data_collector] in the while loop...parse_samples error")
                data = ser.read(BYTES_PER_SAMPLE * SAMPLES_PER_BLOCK)
                ##디버깅용
                if len(data) < BYTES_PER_SAMPLE:
                    print("[WARNING] 데이터 너무 짧음 (0xAA 탐지 불가)")
                    continue

                if b'\xAA' not in data:
                    print("[WARNING] 0xAA 헤더 없음 → 무시하고 다음 read 시도")
                    continue
                ###########

                t0, should_stop = parse_samples(data, t0, DURATION_US, buf, visualize_queue)
                if should_stop:
                    break

            now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            gesture_dir = os.path.join(DATA_DIR, GESTURE_NAME)
            os.makedirs(gesture_dir, exist_ok=True)
            fname = os.path.join(gesture_dir, f"{now_str}.csv")
            save_csv(buf, fname)
            index_path = os.path.join("data_index", f"{GESTURE_NAME}.csv")
            os.makedirs("data_index", exist_ok=True)
            with open(index_path, "a") as f:
                f.write(f"{now_str}.csv\n")
            print(f"[Collector] ■ Recording complete: 총 {len(buf)} samples\n")

        while not flag_queue.empty():
                flag_queue.get()

        # if not start_queue.empty():
        #     seconds, filepath, is_exit = start_queue.get()
        #     return seconds, filepath, is_exit
        
def data_controller(data_queue, start_queue, end_queue, visualize_queue, flag_queue):
    ser = init()
    try:
        while True:
            seconds, filepath, is_exit = wait(ser, data_queue, start_queue, visualize_queue, flag_queue)
            if is_exit:
                break
    finally:
        ser.close()
