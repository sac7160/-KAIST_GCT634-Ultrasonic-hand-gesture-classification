# import sys
# import numpy as np
# from collections import deque
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtWidgets, QtCore
# from queue import Empty
# from datetime import datetime, timedelta

# def visualizer_ultrasonic(data_queue, num_sensors=1, title="Ultrasonic Signal"):
#     app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

#     QUEUE_SIZE = 40000
#     PLOT_WINDOW = 3000  # ← 더 많은 주기 보기 위해 증가
#     vbuf = deque(maxlen=QUEUE_SIZE)

#     teensy_t0 = None
#     wallclock_t0 = None

#     win = pg.GraphicsLayoutWidget(title=title)
#     win.resize(1000, 400)
#     win.show()

#     string_axis = pg.AxisItem(orientation='bottom')
#     plot = win.addPlot(title=title, axisItems={'bottom': string_axis})
#     plot.showGrid(x=True, y=True)
#     plot.setLabel('bottom', 'Time')
#     plot.setLabel('left', 'ADC Value')
#     curve = plot.plot(pen=pg.mkPen('r', width=1))

#     def update():
#         nonlocal teensy_t0, wallclock_t0
#         got = False
#         while True:
#             try:
#                 item = data_queue.get_nowait()
#             except Empty:
#                 break
#             got = True

#             ts_us, val = item
#             if teensy_t0 is None:
#                 teensy_t0 = ts_us
#                 wallclock_t0 = datetime.now()

#             vbuf.append((ts_us, val))

#         if not got or len(vbuf) < 2:
#             return

#         recent_data = list(vbuf)[-PLOT_WINDOW:]
#         ts_us_arr = np.array([x[0] for x in recent_data])
#         adc_values = np.array([x[1] for x in recent_data])

#         times = [wallclock_t0 + timedelta(microseconds=int(ts - teensy_t0)) for ts in ts_us_arr]
#         xs = np.array([t.timestamp() for t in times])
#         labels = [t.strftime("%H:%M:%S.%f")[:-3] for t in times]

#         curve.setData(xs, adc_values, downsample=False, autoDownsample=False)  # 고주파 신호라서 downsample 없음
#         plot.setXRange(xs[0], xs[-1])
#         string_axis.setTicks([[(x, label) for x, label in zip(xs[::300], labels[::300])]])

#     timer = QtCore.QTimer()
#     timer.timeout.connect(update)
#     timer.start(10)  # ← 10ms마다 update (100FPS)

#     if hasattr(app, 'exec_'):
#         app.exec_()
#     else:
#         app.exec()


#트랜스듀서 2개 변경 테스트
import sys
import numpy as np
from collections import deque
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
from queue import Empty
from datetime import datetime, timedelta

def visualizer_ultrasonic(data_queue, num_sensors=2, title="Ultrasonic Signals (2CH)"):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

    QUEUE_SIZE = 40000
    PLOT_WINDOW = 3000
    vbuf = deque(maxlen=QUEUE_SIZE)

    teensy_t0 = None
    wallclock_t0 = None

    win = pg.GraphicsLayoutWidget(title=title)
    win.resize(1000, 600)
    win.show()

    plots = []
    curves = []

    for ch in range(num_sensors):
        string_axis = pg.AxisItem(orientation='bottom')
        plot = win.addPlot(title=f"{title} - CH{ch}", axisItems={'bottom': string_axis})
        plot.showGrid(x=True, y=True)
        plot.setLabel('bottom', 'Time')
        plot.setLabel('left', f'ADC Value CH{ch}')
        curve = plot.plot(pen=pg.mkPen('r' if ch == 0 else 'b', width=1))

        plots.append((plot, string_axis))
        curves.append(curve)
        win.nextRow()

    def update():
        nonlocal teensy_t0, wallclock_t0
        got = False
        while True:
            try:
                item = data_queue.get_nowait()
            except Empty:
                break
            got = True

            ts_us, val0, val1 = item
            if teensy_t0 is None:
                teensy_t0 = ts_us
                wallclock_t0 = datetime.now()

            vbuf.append((ts_us, val0, val1))

        if not got or len(vbuf) < 2:
            return

        recent_data = list(vbuf)[-PLOT_WINDOW:]
        ts_us_arr = np.array([x[0] for x in recent_data])
        val0_arr = np.array([x[1] for x in recent_data])
        val1_arr = np.array([x[2] for x in recent_data])

        times = [wallclock_t0 + timedelta(microseconds=int(ts - teensy_t0)) for ts in ts_us_arr]
        xs = np.array([t.timestamp() for t in times])
        labels = [t.strftime("%H:%M:%S.%f")[:-3] for t in times]

        # Plot CH0
        curves[0].setData(xs, val0_arr, downsample=False, autoDownsample=False)
        plots[0][0].setXRange(xs[0], xs[-1])
        plots[0][1].setTicks([[(x, label) for x, label in zip(xs[::300], labels[::300])]])

        # Plot CH1
        curves[1].setData(xs, val1_arr, downsample=False, autoDownsample=False)
        plots[1][0].setXRange(xs[0], xs[-1])
        plots[1][1].setTicks([[(x, label) for x, label in zip(xs[::300], labels[::300])]])

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(10)  # 100 FPS

    if hasattr(app, 'exec_'):
        app.exec_()
    else:
        app.exec()
