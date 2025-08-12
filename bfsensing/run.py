from data_collector.bf_data_collector import data_controller as bf_data_controller
from data_collector.bf_data_collector2 import data_controller as bf_data_controller2
from plot_manager import visualizer_ultrasonic 
from emit_controller.emit_ultrasonic import emit_controller

import torch.multiprocessing as multiprocessing

import tkinter as tk
from tkinter import ttk, font
from PIL import Image, ImageTk
import os

from data_collector.bf_data_collector import GESTURE_NAME

def run(process, start_queues, end_queues, duration):
    global root

    root = tk.Tk()
    root.resizable(True,True)
    root.title("Ultrasonic Beamforming Measurement")
    root.geometry("1600x900+0+0")
    root.focus_force()

    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(size=20)
    root.option_add("*Font", default_font)

    # Set the font style and size for line3_text and line4_text
    line2_label_font = font.Font(size=50, weight="bold")    #remaining time
    line3_label_font = font.Font(size=20)                   #condition
    line4_label_font = font.Font(size=20, weight="bold")    #phase
    line5_label_font = font.Font(size=30, weight="bold")    #target

    frame = ttk.Frame(root, padding="10", width=1600, height=900)
    frame.grid(column=0, row=0, sticky="nsew")  #그리드 레이아웃
    frame.grid_propagate(False)

     # GESTURE_NAME에 해당하는 이미지 불러오기
    gesture = GESTURE_NAME
    image_path = os.path.join("assets", f"{gesture}.png")

    if os.path.exists(image_path):
        gesture_image_pil = Image.open(image_path).resize((300, 300))
        gesture_image = ImageTk.PhotoImage(gesture_image_pil)
        media_label = ttk.Label(frame, image=gesture_image)
        media_label.image = gesture_image
    else:
        media_label = ttk.Label(frame, text=f"[Image not found: {gesture}]")

    media_label.grid(column=1, row=6, pady=(20, 10), sticky="nsew")
    
    #media_label = ttk.Label(frame)

    line1_text = f"Test line1"
    line1_label = ttk.Label(frame, text=line1_text)

    line3_text = f"Test line3"
    line3_label = ttk.Label(frame, text=line3_text, font=line3_label_font)

    line4_text = f"Test line4"
    line4_label = ttk.Label(frame, text=line4_text, font=line4_label_font)
    
    line5_text = f"Test line5"
    line5_label = ttk.Label(frame, text=line5_text, font=line5_label_font)

    #remaining_time_var = tk.StringVar()
    #line2_label = tk.Label(frame, textvariable=remaining_time_var, fg="blue", font=line2_label_font)

    #remaining_time_thread = threading.Thread(target=update_remaining_time_thread, args=(duration,))     #타이머 스레드
    #remaining_time_thread.start()
    line2_text = f"Test line2"
    line2_label = ttk.Label(frame, text=line2_text, font=line2_label_font)

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_rowconfigure(7, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(2, weight=1)

    line1_label.grid(column=1, row=1, sticky="nsew")
    line3_label.grid(column=1, row=2, pady=(0, 10), sticky="nsew")
    line4_label.grid(column=1, row=3, pady=(0, 10), sticky="nsew")
    line5_label.grid(column=1, row=4, pady=(0, 10), sticky="nsew")
    line2_label.grid(column=1, row=5, pady=(0, 10), sticky="nsew")

    root.mainloop() #root 창 생성됨



if __name__ == "__main__":
    


    data_queues = [multiprocessing.Queue()]
    data_queues2 = [multiprocessing.Queue()]
    start_queues = [multiprocessing.Queue()]
    end_queues = [multiprocessing.Queue()]
    ultrasonic_data_queue = multiprocessing.Queue() #visualizing용 queue
    flag_queue = multiprocessing.Queue()

    processes = [
        multiprocessing.Process(target=bf_data_controller, args=(data_queues[0],start_queues[0], end_queues[0], ultrasonic_data_queue, flag_queue), name='Ultrasonic Collector'),
        multiprocessing.Process(target=bf_data_controller2, args=(data_queues2[0],start_queues[0], end_queues[0], ultrasonic_data_queue, flag_queue), name='Ultrasonic Collector2'),
        #multiprocessing.Process(target=visualizer_ultrasonic, args=(ultrasonic_data_queue, 2, 'Ultrasonic Signal'), name='Ultrasonic Visualizer'),  #개수 임시로 1
        multiprocessing.Process(target=emit_controller,args=(flag_queue,), name='Ultrasonic Emitter')
    ]

    for process in processes:
        process.start()

    run(processes, start_queues, end_queues, 10)
    





