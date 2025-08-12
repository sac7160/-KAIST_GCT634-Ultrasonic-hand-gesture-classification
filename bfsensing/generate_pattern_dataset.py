import numpy as np
import csv
from emit_controller.coordinates import transducers, num_transducers

SPEED_OF_SOUND = 346.0
PORT_MAPPING = [
    51, 52, 53, 54, 28, 29, 30, 31, 47, 46, 45, 44, 43, 42, 41, 40,
    56, 57, 58, 59, 48, 49, 72, 69, 39, 38, 37, 36, 35, 34, 33, 32,
    21, 23, 65, 63, 9, 11, 13, 15, 20, 22, 64, 66, 8, 10, 12, 14,
    24, 25, 26, 27, 16, 17, 18, 19, 7, 6, 5, 4, 3, 2, 1, 0
]

def left_shift_array(arr, shift):
    shift %= len(arr)
    return arr[shift:] + arr[:shift]

def compute_signal_bytes(focal_point):
    bits = np.zeros((80, 10), dtype=int)

    for i in range(num_transducers):
        t_pos = np.array(transducers[i])
        distance = np.linalg.norm(t_pos - focal_point)

        wavelength = SPEED_OF_SOUND / 40000.0
        phase = (1.0 - ((distance / wavelength) % 1.0)) * 2.0
        shift = int(round((phase * 10.0 / 2.0) % 10.0))  # 0~9

        default_phase = [0,0,0,0,0,1,1,1,1,1]
        shifted_phase = left_shift_array(default_phase, shift)

        for j in range(10):
            bits[79 - PORT_MAPPING[i], j] = shifted_phase[j]

    signal_bytes = [0] * 200
    bytenum = 0
    for i in range(10):  # div
        for j in range(0, 80, 8):  # ports
            A = bits[j:j+4, i]
            B = bits[j+4:j+8, i]

            byteA = int(''.join(map(str, A)) + '0001', 2)
            byteB = int(''.join(map(str, B)) + '0001', 2)

            signal_bytes[bytenum] = byteB
            signal_bytes[bytenum + 1] = byteA
            bytenum += 2

    signal_bytes.reverse()
    return signal_bytes

# 3x3x3 = 27 focal points
focal_points = []
# for z in [0.1, 0.2, 0.3]:
for z in [0.2]:
    for y in [-0.1, 0.0, 0.1]:
        for x in [-0.1, 0.0, 0.1]:
            focal_points.append((x, y, z))

# CSV 저장
csv_path = "phase_patterns.csv"
with open(csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    header = ['x', 'y', 'z'] + [f'byte{i}' for i in range(200)]
    writer.writerow(header)

    for fp in focal_points:
        signal = compute_signal_bytes(np.array(fp))
        writer.writerow(list(fp) + signal)

print(f"✅ Phase delay patterns saved to {csv_path}")
