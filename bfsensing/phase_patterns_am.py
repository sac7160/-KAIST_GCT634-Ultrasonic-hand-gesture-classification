import numpy as np
import csv
from emit_controller.coordinates import transducers, num_transducers

# Constants
SPEED_OF_SOUND = 346.0  # m/s
FREQ = 40000.0  # Hz (40 kHz)
WAVELENGTH = SPEED_OF_SOUND / FREQ
PORT_MAPPING = [
    51, 52, 53, 54, 28, 29, 30, 31, 47, 46, 45, 44, 43, 42, 41, 40,
    56, 57, 58, 59, 48, 49, 72, 69, 39, 38, 37, 36, 35, 34, 33, 32,
    21, 23, 65, 63, 9, 11, 13, 15, 20, 22, 64, 66, 8, 10, 12, 14,
    24, 25, 26, 27, 16, 17, 18, 19, 7, 6, 5, 4, 3, 2, 1, 0
]

# Load from previous context
duty_array = np.array(
    [50, 50, 50, 40, 50, 50, 50, 30, 50, 50, 50, 20, 50, 50, 50, 20, 50, 50, 50, 10, 50, 50, 50, 10,
    50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 10,
    50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 10,
    50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 20, 50, 50, 50, 20, 50, 50, 50, 30, 50, 50, 50, 30,
    50, 50, 50, 40, 50, 40, 50, 50, 50, 30, 50, 50, 50, 30, 50, 50, 50, 20, 50, 50, 50, 20, 50, 50,
    50, 10, 50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 10, 50, 50,
    50, 10, 50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 10, 50, 50,
    50, 10, 50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 20, 50, 50, 50, 20, 50, 50,
    50, 30, 50, 50, 50, 40, 50, 50]
)


# Default pattern pool by duty percentage (50% → [0,0,0,0,0,1,1,1,1,1])
pattern_pool = {
    10: [0,0,0,0,0,0,0,0,0,1],
    20: [0,0,0,0,0,0,0,0,1,1],
    30: [0,0,0,0,0,0,0,1,1,1],
    40: [0,0,0,0,0,0,1,1,1,1],
    50: [0,0,0,0,0,1,1,1,1,1]
}

# Placeholder for transducer and focal point coordinates
focal_point = np.array([0, 0, 0.12])  # example

# Prepare the full pattern list
def left_shift_array(arr, shift):
    shift %= len(arr)
    return arr[shift:] + arr[:shift]

def compute_signal_bytes(duty):
    phase_bits = np.zeros((80, 10), dtype=int)

    for i in range(len(transducers)):
        distance = np.linalg.norm(transducers[i] - focal_point)
        phase = (1.0 - ((distance / WAVELENGTH) % 1.0)) * 2.0
        shift = int(round((phase * 10.0 / 2.0) % 10.0))  # 0~9
        print(shift)

        n_high = duty // 10
        pattern = [0] * (10 - n_high) + [1] * n_high
        shifted = left_shift_array(pattern, shift)

        for j in range(10):
            phase_bits[79 - PORT_MAPPING[i], j] = shifted[j]

    signal_bytes = [0] * 200
    bytenum = 0
    for i in range(10):  # div
        for j in range(0, 80, 8):  # ports
            A = phase_bits[j:j+4, i]
            B = phase_bits[j+4:j+8, i]

            byteA = int(''.join(map(str, A)) + '0001', 2)
            byteB = int(''.join(map(str, B)) + '0001', 2)

            signal_bytes[bytenum] = byteB
            signal_bytes[bytenum + 1] = byteA
            bytenum += 2

    signal_bytes.reverse()
    return signal_bytes

# CSV 저장
csv_path = "phase_patterns_am.csv"
with open(csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    header = ['x', 'y', 'z', 'duty'] + [f'byte{i}' for i in range(200)]
    writer.writerow(header)

    for duty in duty_array:
        signal = compute_signal_bytes(duty)
        writer.writerow([focal_point[0], focal_point[1], focal_point[2]] + signal)


print(f"✅ Phase delay patterns saved to {csv_path}")