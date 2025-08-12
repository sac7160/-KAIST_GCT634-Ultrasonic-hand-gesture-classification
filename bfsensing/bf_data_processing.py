import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import csv

def resample_and_plot(csv_path, target_interval_us=2, show_plot=True):
    df = pd.read_csv(csv_path)
    df = df.sort_values("teensy_ts_us").reset_index(drop=True)

    orig_ts = df["teensy_ts_us"].values
    orig_vals = df["adc_value"].values

    # 정규화된 timestamp 생성
    t0 = orig_ts[0]
    orig_ts_norm = orig_ts - t0

    # 타겟 간격에 맞춰 새로운 타임스탬프 배열 생성
    new_ts = np.arange(0, orig_ts_norm[-1], target_interval_us)
    interp_vals = np.interp(new_ts, orig_ts_norm, orig_vals)

    if show_plot:
        plt.figure(figsize=(12, 4))
        plt.plot(orig_ts_norm[:1000], orig_vals[:1000], label="Original", alpha=0.4)
        plt.plot(new_ts[:1000], interp_vals[:1000], label=f"Resampled ({target_interval_us}µs)", linewidth=1)
        plt.xlabel("Time (µs)")
        plt.ylabel("ADC Value")
        plt.title(f"ADC Signal Resampled to {target_interval_us}µs")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    return new_ts, interp_vals


def plot_resampled_range(csv_path, start_us=0, end_us=500, interval_us=2):
    """
    지정한 구간(start_us~end_us)에서 4us 간격으로 리샘플링 후 원본 데이터와 함께 plot

    Args:
        csv_path (str): CSV 파일 경로
        start_us (int): 시작 timestamp (μs)
        end_us (int): 끝 timestamp (μs)
        interval_us (int): 리샘플링 간격 (μs)
    """
    # CSV 로드 및 타입 변환
    df = pd.read_csv(csv_path)
    df["timestamp_us"] = pd.to_numeric(df["teensy_ts_us"], errors="coerce")
    df.dropna(inplace=True)
    df["timestamp_us"] = df["timestamp_us"].astype(int)

    # 해당 범위 필터링
    df_filtered = df[(df["timestamp_us"] >= start_us) & (df["timestamp_us"] <= end_us)].copy()
    if df_filtered.empty:
        print(f"[경고] 지정한 범위 {start_us}~{end_us}μs 에 해당하는 데이터가 없습니다.")
        return

    # 리샘플링
    resample_ts = np.arange(start_us, end_us + 1, interval_us)
    resample_vals = np.interp(resample_ts, df_filtered["timestamp_us"], df_filtered["adc_value"])

    # Plot
    plt.figure(figsize=(12, 4))
    plt.plot(df_filtered["timestamp_us"], df_filtered["adc_value"], label="Original", color='skyblue')
    plt.plot(resample_ts, resample_vals, label=f"Resampled ({interval_us}μs)", color='darkorange')
    plt.xlabel("Timestamp (μs)")
    plt.ylabel("ADC Value")
    plt.title(f"ADC Signal ({start_us}–{end_us}μs)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_resampled_range_2ch(csv_path, start_us=0, end_us=500, interval_us=2):
    """
    지정한 구간(start_us~end_us)에서 interval_us 간격으로 리샘플링 후
    두 트랜스듀서(A0, A1)의 원본 데이터 및 리샘플링 데이터를 함께 시각화

    Args:
        csv_path (str): CSV 파일 경로
        start_us (int): 시작 timestamp (μs)
        end_us (int): 끝 timestamp (μs)
        interval_us (int): 리샘플링 간격 (μs)
    """
    # CSV 로드 및 타입 변환
    df = pd.read_csv(csv_path)
    df["timestamp_us"] = pd.to_numeric(df["teensy_ts_us"], errors="coerce")
    df.dropna(inplace=True)
    df["timestamp_us"] = df["timestamp_us"].astype(int)

    # 범위 필터링
    df_filtered = df[(df["timestamp_us"] >= start_us) & (df["timestamp_us"] <= end_us)].copy()
    if df_filtered.empty:
        print(f"[경고] 지정한 범위 {start_us}~{end_us}μs 에 해당하는 데이터가 없습니다.")
        return

    # 리샘플링 대상 시점 생성
    resample_ts = np.arange(start_us, end_us + 1, interval_us)

    # 리샘플링 (양 채널)
    # resample_val0 = np.interp(resample_ts, df_filtered["timestamp_us"], df_filtered["adc_val0"])
    # resample_val1 = np.interp(resample_ts, df_filtered["timestamp_us"], df_filtered["adc_val1"])

    # Plot
    fig, axs = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

    axs[0].plot(df_filtered["timestamp_us"], df_filtered["adc_val0"], label="Original CH0", color='skyblue')
    #axs[0].plot(resample_ts, resample_val0, label=f"Resampled CH0 ({interval_us}μs)", color='darkorange')
    axs[0].set_ylabel("ADC Value (CH0)")
    axs[0].legend()
    axs[0].grid(True)

    axs[1].plot(df_filtered["timestamp_us"], df_filtered["adc_val1"], label="Original CH1", color='lightgreen')
    #axs[1].plot(resample_ts, resample_val1, label=f"Resampled CH1 ({interval_us}μs)", color='purple')
    axs[1].set_xlabel("Timestamp (μs)")
    axs[1].set_ylabel("ADC Value (CH1)")
    axs[1].legend()
    axs[1].grid(True)

    plt.suptitle(f"ADC Signal Comparison ({start_us}–{end_us}μs)", fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

def plot_resampled_range_3ch(csv_path, start_us=0, end_us=500, interval_us=2):
    """
    지정한 구간(start_us~end_us)에서 interval_us 간격으로 리샘플링 후
    3개의 트랜스듀서(adc_val0, adc_val1, adc_val2)의 원본 데이터 시각화

    Args:
        csv_path (str): CSV 파일 경로
        start_us (int): 시작 timestamp (μs)
        end_us (int): 끝 timestamp (μs)
        interval_us (int): 리샘플링 간격 (μs)
    """
    # CSV 로드 및 타입 변환
    df = pd.read_csv(csv_path)
    df["timestamp_us"] = pd.to_numeric(df["teensy_ts_us"], errors="coerce")
    df.dropna(inplace=True)
    df["timestamp_us"] = df["timestamp_us"].astype(int)

    # 범위 필터링
    df_filtered = df[(df["timestamp_us"] >= start_us) & (df["timestamp_us"] <= end_us)].copy()
    if df_filtered.empty:
        print(f"[경고] 지정한 범위 {start_us}~{end_us}μs 에 해당하는 데이터가 없습니다.")
        return

    # Plot
    fig, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

    axs[0].plot(df_filtered["timestamp_us"], df_filtered["adc_val0"], label="Original CH0", color='skyblue')
    axs[0].set_ylabel("ADC Value (CH0)")
    axs[0].legend()
    axs[0].grid(True)

    axs[1].plot(df_filtered["timestamp_us"], df_filtered["adc_val1"], label="Original CH1", color='lightgreen')
    axs[1].set_ylabel("ADC Value (CH1)")
    axs[1].legend()
    axs[1].grid(True)

    axs[2].plot(df_filtered["timestamp_us"], df_filtered["adc_val2"], label="Original CH2", color='salmon')
    axs[2].set_xlabel("Timestamp (μs)")
    axs[2].set_ylabel("ADC Value (CH2)")
    axs[2].legend()
    axs[2].grid(True)

    plt.suptitle(f"ADC Signal Comparison ({start_us}–{end_us}μs)", fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

def plot_resampled_range_step(csv_path, start_us=0, end_us=500, interval_us=2):
    df = pd.read_csv(csv_path)
    df["timestamp_us"] = pd.to_numeric(df["teensy_ts_us"], errors="coerce")
    df.dropna(inplace=True)
    df["timestamp_us"] = df["timestamp_us"].astype(int)

    df_filtered = df[(df["timestamp_us"] >= start_us) & (df["timestamp_us"] <= end_us)].copy()
    if df_filtered.empty:
        print(f"[경고] 지정한 범위 {start_us}~{end_us}μs 에 해당하는 데이터가 없습니다.")
        return

    # 리샘플링
    resample_ts = np.arange(start_us, end_us + 1, interval_us)
    resample_vals = np.interp(resample_ts, df_filtered["timestamp_us"], df_filtered["adc_value"])

    # Plot
    plt.figure(figsize=(12, 4))
    plt.step(df_filtered["timestamp_us"], df_filtered["adc_value"], label="Original", color='skyblue', where='post', alpha=0.5)
    plt.step(resample_ts, resample_vals, label=f"Resampled ({interval_us}μs)", color='orange', where='post')
    plt.xlabel("Timestamp (μs)")
    plt.ylabel("ADC Value")
    plt.title(f"ADC Signal ({start_us}–{end_us}μs)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def clip_data(csv_path, output_path,
              window_us=18000,
              detect_min_us=1300000,
              detect_max_us=1900000,
              window_size=20,
              k_sigma=4,
              buffer_us=1000):  # 🆕 buffer 파라미터 추가

    df = pd.read_csv(csv_path)
    df = df.sort_values('teensy_ts_us')
    t0 = df['teensy_ts_us'].iloc[0]
    df['t_rel'] = df['teensy_ts_us'] - t0

    # 1. Baseline 계산
    baseline = df[df['t_rel'] < detect_min_us]['adc_value']
    mu = baseline.mean()
    sigma = baseline.std()

    # 2. 탐지 구간 선택
    df_window = df[(df['t_rel'] >= detect_min_us) & (df['t_rel'] <= detect_max_us)].copy().reset_index(drop=True)
    adc_vals = df_window['adc_value'].values

    # 3. rolling mean
    rolling_mean = pd.Series(adc_vals).rolling(window=window_size).mean().fillna(0)

    # 4. threshold 초과 지점 탐지
    threshold = mu + k_sigma * sigma
    signal_start_idx = None
    for i in range(len(rolling_mean)):
        if rolling_mean[i] > threshold:
            signal_start_idx = max(i - int(buffer_us / 2), 0)  # 🆕 2µs 샘플 기준 buffer 보정
            break
    else:
        print("[WARN] 시작점 못 찾음")
        return

    signal_start_time = df_window.loc[signal_start_idx, 'teensy_ts_us']
    signal_end_time = signal_start_time + window_us

    # 5. 자르기
    segment = df[(df['teensy_ts_us'] >= signal_start_time) & (df['teensy_ts_us'] <= signal_end_time)].copy()

    # 6. 저장
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    segment.to_csv(output_path, index=False)
    print(f"[INFO] 저장 완료: {output_path} (시작: {signal_start_time}us, 기준: µ={mu:.2f}, σ={sigma:.2f})")

def clip_data_mad(csv_path, output_path,
              window_us=18000,
              detect_min_us=1300000,
              detect_max_us=1900000,
              k_sigma=5,         # 보통 MAD에서는 5 이상이 적절
              buffer_us=1000):   # 탐지 앞부분을 살짝 포함

    # 1. CSV 불러오기 및 시간 기준 정렬
    df = pd.read_csv(csv_path)
    df = df.sort_values('teensy_ts_us')
    t0 = df['teensy_ts_us'].iloc[0]
    df['t_rel'] = df['teensy_ts_us'] - t0

    # 2. baseline 구간 선택 (노이즈만 존재하는 부분)
    baseline = df[df['t_rel'] < detect_min_us]['adc_value']
    if baseline.empty:
        print(f"[WARN] baseline 구간이 비어 있음 → {csv_path}")
        return

    # 3. Median Absolute Deviation (MAD) 기반 threshold 계산
    med = np.median(baseline)
    mad = np.median(np.abs(baseline - med))
    threshold = med + k_sigma * mad

    # 4. 신호 탐지 대상 구간 추출
    df_window = df[(df['t_rel'] >= detect_min_us) & (df['t_rel'] <= detect_max_us)].copy().reset_index(drop=True)
    adc_vals = df_window['adc_value'].values

    # 5. threshold 초과 지점 탐색
    signal_start_idx = None
    for i in range(len(adc_vals)):
        if adc_vals[i] > threshold:
            signal_start_idx = max(i - int(buffer_us / 2), 0)  # 앞쪽 버퍼 보정
            break

    if signal_start_idx is None:
        print(f"[WARN] 시작점 탐지 실패 → {csv_path}")
        return

    signal_start_time = df_window.loc[signal_start_idx, 'teensy_ts_us']
    signal_end_time = signal_start_time + window_us

    # 6. 잘라내기
    segment = df[(df['teensy_ts_us'] >= signal_start_time) & (df['teensy_ts_us'] <= signal_end_time)].copy()

    # 7. 저장
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    segment.to_csv(output_path, index=False)
    print(f"[INFO] 저장 완료: {output_path} (시작: {signal_start_time}us, 기준: med={med:.2f}, MAD={mad:.2f})")

def clip_data_final(csv_path, output_path,
              window_us=18000,
              detect_min_us=1000000,#1300000,
              detect_max_us=1900000,
              window_size=40,#80,
              buffer_us=1000,
              mean_offset=12,#15,         # baseline보다 얼마나 높아야 신호로 볼지
              sustain_count=20):#30):      # 조건 만족이 최소 몇 번 연속돼야 하는지

    df = pd.read_csv(csv_path)
    df = df.sort_values('teensy_ts_us')
    t0 = df['teensy_ts_us'].iloc[0]
    df['t_rel'] = df['teensy_ts_us'] - t0

    # 1. baseline 평균 계산
    baseline = df[df['t_rel'] < detect_min_us]['adc_value']
    if baseline.empty:
        print(f"[WARN] baseline 구간 없음 → {csv_path}")
        return
    baseline_mean = baseline.mean()

    # 2. 탐지 대상 구간
    df_window = df[(df['t_rel'] >= detect_min_us) & (df['t_rel'] <= detect_max_us)].copy().reset_index(drop=True)
    adc_vals = df_window['adc_value'].values

    # 3. rolling 평균 계산
    rolling_mean = pd.Series(adc_vals).rolling(window=window_size).mean().fillna(0)
    threshold = baseline_mean + mean_offset

    # 4. threshold 이상이 sustain_count 이상 연속으로 나오는 구간 찾기
    over_thresh = rolling_mean > threshold
    counter = 0
    signal_start_idx = None
    for i, over in enumerate(over_thresh):
        if over:
            counter += 1
            if counter >= sustain_count:
                signal_start_idx = max(i - sustain_count - int(buffer_us / 2), 0)
                break
        else:
            counter = 0

    if signal_start_idx is None:
        print(f"[WARN] 신호 시작점 탐지 실패 → {csv_path}")
        return

    # 5. 시간으로 변환
    signal_start_time = df_window.loc[signal_start_idx, 'teensy_ts_us']
    signal_end_time = signal_start_time + window_us

    # 6. 클리핑 및 저장
    segment = df[(df['teensy_ts_us'] >= signal_start_time) & (df['teensy_ts_us'] <= signal_end_time)].copy()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    segment.to_csv(output_path, index=False)

    print(f"[INFO] 저장 완료: {output_path} (시작: {signal_start_time}us, 기준: mean>{threshold:.1f} sustained {sustain_count})")

def clip_all_data(index_dir="data_index", data_dir="data", clip_dir="data/clip_data"):
    index_files = [f for f in os.listdir(index_dir) if f.endswith(".csv")]

    for index_file in index_files:
        gesture = index_file.replace(".csv", "")
        gesture_dir = os.path.join(data_dir, gesture)
        clip_gesture_dir = os.path.join(clip_dir, gesture)
        os.makedirs(clip_gesture_dir, exist_ok=True)

        index_path = os.path.join(index_dir, index_file)
        with open(index_path, "r") as f:
            filenames = [line.strip() for line in f if line.strip().endswith(".csv")]

        for filename in filenames:
            src_path = os.path.join(gesture_dir, filename)
            dst_filename = filename.replace(".csv", "_clip.csv")
            dst_path = os.path.join(clip_gesture_dir, dst_filename)

            try:
                clip_data_dual_channel(csv_path=src_path, output_path=dst_path)
            except Exception as e:
                print(f"[에러] {gesture}/{filename} 처리 실패: {e}")

def clip_all_data_triple_channel(index_dir="data_index", data_dir="data", clip_dir="data/clip_data"):
    index_files = [f for f in os.listdir(index_dir) if f.endswith("_teensy2.csv")]

    for index_file in index_files:
        gesture = index_file.replace("_teensy2.csv", "")
        gesture_dir = os.path.join(data_dir, gesture)
        clip_gesture_dir = os.path.join(clip_dir, gesture)
        os.makedirs(clip_gesture_dir, exist_ok=True)

        index_path = os.path.join(index_dir, index_file)
        with open(index_path, "r") as f:
            filenames = [line.strip().replace("_teensy2.csv", "_merged.csv") for line in f if line.strip().endswith(".csv")]

        for filename in filenames:
            src_path = os.path.join(gesture_dir, filename)
            dst_filename = filename.replace("_merged.csv", "_clip.csv")
            dst_path = os.path.join(clip_gesture_dir, dst_filename)

            if not os.path.exists(src_path):
                print(f"[경고] 병합 파일 없음: {src_path}")
                continue

            try:
                clip_data_triple_channel(csv_path=src_path, output_path=dst_path)
            except Exception as e:
                print(f"[에러] {gesture}/{filename} 처리 실패: {e}")


def merge_all_teensy(index_folder: str, data_folder: str, gesture_name: str):
    """
    index 파일(extension.csv, extension_teensy2.csv)에 명시된 CSV 목록을 기준으로
    두 Teensy에서 저장된 데이터를 병합하여 저장합니다.

    Args:
        index_folder (str): data_index 폴더 경로
        data_folder (str): 실제 CSV 파일이 저장된 폴더 경로 (e.g., data/wrist_flexion)
        gesture_name (str): 제스처 이름 (e.g., 'extension')
    """
    index1_path = os.path.join(index_folder, f"{gesture_name}.csv")
    index2_path = os.path.join(index_folder, f"{gesture_name}_teensy2.csv")

    list1 = pd.read_csv(index1_path, header=None)[0].tolist()
    list2 = pd.read_csv(index2_path, header=None)[0].tolist()

    if len(list1) != len(list2):
        print("❌ 인덱스 파일의 길이가 다릅니다.")
        return

    for fname1, fname2 in zip(list1, list2):
        path1 = os.path.join(data_folder, fname1)
        path2 = os.path.join(data_folder, fname2)

        if not os.path.exists(path1) or not os.path.exists(path2):
            print(f"[경고] 누락된 파일 → {fname1}, {fname2}")
            continue

        df1 = pd.read_csv(path1)
        df2 = pd.read_csv(path2)

        if len(df1) != len(df2):
            print(f"[경고] 행 수 불일치 → {fname1}")
            continue

        # adc_val0 (세 번째 채널)만 추가
        df_merged = pd.concat([df1, df2[["adc_val0"]]], axis=1)
        df_merged.columns = ["teensy_ts_us", "readable_time", "adc_val0", "adc_val1", "adc_val2"]

        # _merged.csv로 저장
        basename = fname1.replace(".csv", "")
        out_path = os.path.join(data_folder, f"{basename}_merged.csv")
        df_merged.to_csv(out_path, index=False)
        print(f"[✓] 저장 완료: {out_path}")

import os
import pandas as pd

def merge_all_teensy_v2(index_folder: str, data_folder: str, gesture_name: str):
    """
    파일 이름을 기준으로 병합할 수 있는 짝을 찾아 Teensy 데이터 병합

    Args:
        index_folder (str): data_index 폴더 경로
        data_folder (str): 실제 CSV 파일이 저장된 폴더 경로
        gesture_name (str): 제스처 이름 (e.g., 'extension')
    """
    index1_path = os.path.join(index_folder, f"{gesture_name}.csv")
    index2_path = os.path.join(index_folder, f"{gesture_name}_teensy2.csv")

    list1 = pd.read_csv(index1_path, header=None)[0].tolist()
    list2 = pd.read_csv(index2_path, header=None)[0].tolist()

    # _teensy2.csv → 원래 이름으로 매핑 (ex: 2025-06-04_10-31-18.csv)
    base_to_teensy2 = {fname.replace("_teensy2.csv", ".csv"): fname for fname in list2}

    for fname1 in list1:
        if fname1 not in base_to_teensy2:
            print(f"[경고] 대응하는 teensy2 파일 없음: {fname1}")
            continue

        fname2 = base_to_teensy2[fname1]
        path1 = os.path.join(data_folder, fname1)
        path2 = os.path.join(data_folder, fname2)

        if not os.path.exists(path1) or not os.path.exists(path2):
            print(f"[경고] 누락된 파일 → {fname1}, {fname2}")
            continue

        df1 = pd.read_csv(path1)
        df2 = pd.read_csv(path2)

        if len(df1) != len(df2):
            print(f"[경고] 행 수 불일치 → {fname1}")
            continue

        df_merged = pd.concat([df1, df2[["adc_val0"]]], axis=1)
        df_merged.columns = ["teensy_ts_us", "readable_time", "adc_val0", "adc_val1", "adc_val2"]

        out_path = os.path.join(data_folder, fname1.replace(".csv", "_merged.csv"))
        df_merged.to_csv(out_path, index=False)
        print(f"[✓] 저장 완료: {out_path}")

def merge_all_teensy_final(index_folder: str, data_folder: str, gesture_name: str, delete_original: bool = True):
    """
    파일 이름을 기준으로 병합할 수 있는 짝을 찾아 Teensy 데이터 병합 후,
    병합에 사용된 원본 파일을 삭제할 수 있음.

    Args:
        index_folder (str): data_index 폴더 경로
        data_folder (str): 실제 CSV 파일이 저장된 폴더 경로
        gesture_name (str): 제스처 이름 (e.g., 'extension')
        delete_original (bool): 병합 후 원본 파일 삭제 여부
    """
    index1_path = os.path.join(index_folder, f"{gesture_name}.csv")
    index2_path = os.path.join(index_folder, f"{gesture_name}_teensy2.csv")

    list1 = pd.read_csv(index1_path, header=None)[0].tolist()
    list2 = pd.read_csv(index2_path, header=None)[0].tolist()

    base_to_teensy2 = {fname.replace("_teensy2.csv", ".csv"): fname for fname in list2}

    for fname1 in list1:
        if fname1 not in base_to_teensy2:
            print(f"[경고] 대응하는 teensy2 파일 없음: {fname1}")
            continue

        fname2 = base_to_teensy2[fname1]
        path1 = os.path.join(data_folder, fname1)
        path2 = os.path.join(data_folder, fname2)

        if not os.path.exists(path1) or not os.path.exists(path2):
            print(f"[경고] 누락된 파일 → {fname1}, {fname2}")
            continue

        df1 = pd.read_csv(path1)
        df2 = pd.read_csv(path2)

        if len(df1) != len(df2):
            print(f"[경고] 행 수 불일치 → {fname1}")
            continue

        df_merged = pd.concat([df1, df2[["adc_val0"]]], axis=1)
        df_merged.columns = ["teensy_ts_us", "readable_time", "adc_val0", "adc_val1", "adc_val2"]

        out_path = os.path.join(data_folder, fname1.replace(".csv", "_merged.csv"))
        df_merged.to_csv(out_path, index=False)
        print(f"[✓] 저장 완료: {out_path}")

        # 병합에 사용된 원본 파일 삭제
        if delete_original:
            try:
                os.remove(path1)
                os.remove(path2)
                print(f"[🗑️] 원본 삭제: {fname1}, {fname2}")
            except Exception as e:
                print(f"[오류] 파일 삭제 실패: {e}")

def clip_data_dual_channel(csv_path, output_path,
              window_us=18000,
              detect_min_us=1000000,
              detect_max_us=1900000,
              window_size=40,
              buffer_us=1000,
              mean_offset=12,
              sustain_count=20):
    """
    두 채널(adc_val0, adc_val1) 중 더 이른 신호 시작 시점을 기준으로 window_us 길이만큼 클리핑

    Args:
        csv_path (str): 입력 CSV 경로
        output_path (str): 클리핑 결과 저장 경로
        window_us (int): 잘라낼 시간 구간 (us)
        detect_min_us (int): 신호 탐지 시작 시점 (us)
        detect_max_us (int): 신호 탐지 종료 시점 (us)
        window_size (int): rolling mean 계산을 위한 윈도우 크기
        buffer_us (int): 신호 앞뒤 여유 버퍼 시간
        mean_offset (int): baseline 대비 offset 임계값
        sustain_count (int): threshold 이상 유지되어야 하는 최소 샘플 수
    """

    df = pd.read_csv(csv_path)
    df = df.sort_values('teensy_ts_us')
    t0 = df['teensy_ts_us'].iloc[0]
    df['t_rel'] = df['teensy_ts_us'] - t0

    def detect_start_time(channel_name):
        baseline = df[df['t_rel'] < detect_min_us][channel_name]
        if baseline.empty:
            print(f"[WARN] baseline 구간 없음 → {channel_name}")
            return None
        baseline_mean = baseline.mean()

        df_window = df[(df['t_rel'] >= detect_min_us) & (df['t_rel'] <= detect_max_us)].copy().reset_index(drop=True)
        adc_vals = df_window[channel_name].values
        rolling_mean = pd.Series(adc_vals).rolling(window=window_size).mean().fillna(0)
        threshold = baseline_mean + mean_offset

        over_thresh = rolling_mean > threshold
        counter = 0
        for i, over in enumerate(over_thresh):
            if over:
                counter += 1
                if counter >= sustain_count:
                    idx = max(i - sustain_count - int(buffer_us / 2), 0)
                    return df_window.loc[idx, 'teensy_ts_us']
            else:
                counter = 0
        return None

    start0 = detect_start_time('adc_val0')
    start1 = detect_start_time('adc_val1')

    if start0 is None and start1 is None:
        print(f"[WARN] 두 채널 모두에서 신호 시작점 탐지 실패 → {csv_path}")
        return

    # 둘 중 더 이른 시점 선택
    signal_start_time = min(filter(None, [start0, start1]))
    signal_end_time = signal_start_time + window_us

    segment = df[(df['teensy_ts_us'] >= signal_start_time) & (df['teensy_ts_us'] <= signal_end_time)].copy()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    segment.to_csv(output_path, index=False)

    print(f"[INFO] 저장 완료: {output_path} (시작: {signal_start_time}us, window: {window_us}us)")

def clip_data_triple_channel(csv_path, output_path,
              window_us=18000,
              detect_min_us=1000000,
              detect_max_us=1900000,
              window_size=40,
              buffer_us=1000,
              mean_offset=12,
              sustain_count=20):
    """
    세 채널(adc_val0, adc_val1, adc_val2) 중 더 이른 신호 시작 시점을 기준으로 window_us 길이만큼 클리핑

    Args:
        csv_path (str): 입력 CSV 경로
        output_path (str): 클리핑 결과 저장 경로
        window_us (int): 잘라낼 시간 구간 (us)
        detect_min_us (int): 신호 탐지 시작 시점 (us)
        detect_max_us (int): 신호 탐지 종료 시점 (us)
        window_size (int): rolling mean 계산을 위한 윈도우 크기
        buffer_us (int): 신호 앞뒤 여유 버퍼 시간
        mean_offset (int): baseline 대비 offset 임계값
        sustain_count (int): threshold 이상 유지되어야 하는 최소 샘플 수
    """
    df = pd.read_csv(csv_path)
    df = df.sort_values('teensy_ts_us')
    t0 = df['teensy_ts_us'].iloc[0]
    df['t_rel'] = df['teensy_ts_us'] - t0

    def detect_start_time(channel_name):
        baseline = df[df['t_rel'] < detect_min_us][channel_name]
        if baseline.empty:
            print(f"[WARN] baseline 구간 없음 → {channel_name}")
            return None
        baseline_mean = baseline.mean()

        df_window = df[(df['t_rel'] >= detect_min_us) & (df['t_rel'] <= detect_max_us)].copy().reset_index(drop=True)
        adc_vals = df_window[channel_name].values
        rolling_mean = pd.Series(adc_vals).rolling(window=window_size).mean().fillna(0)
        threshold = baseline_mean + mean_offset

        over_thresh = rolling_mean > threshold
        counter = 0
        for i, over in enumerate(over_thresh):
            if over:
                counter += 1
                if counter >= sustain_count:
                    idx = max(i - sustain_count - int(buffer_us / 2), 0)
                    return df_window.loc[idx, 'teensy_ts_us']
            else:
                counter = 0
        return None

    # 세 채널 모두에 대해 시작 시점 탐지
    start_times = []
    for ch in ['adc_val0', 'adc_val1', 'adc_val2']:
        start = detect_start_time(ch)
        if start:
            start_times.append(start)

    if not start_times:
        print(f"[WARN] 세 채널 모두에서 신호 시작점 탐지 실패 → {csv_path}")
        return

    signal_start_time = min(start_times)
    signal_end_time = signal_start_time + window_us

    segment = df[(df['teensy_ts_us'] >= signal_start_time) & (df['teensy_ts_us'] <= signal_end_time)].copy()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    segment.to_csv(output_path, index=False)

    print(f"[INFO] 저장 완료: {output_path} (시작: {signal_start_time}us, window: {window_us}us)")

"""
두 teensy로 취득한 데이터 파일 합치는 함수
"""
def merge_teensy_csvs_aligned(folder: str, basename: str):
    """
    순서가 정확히 맞는 두 CSV를 같은 행 기준으로 병합합니다.

    Parameters:
        folder (str): 폴더 경로
        basename (str): '2025-06-02_17-12-38'처럼 공통 파일명 (확장자 제외)
    """

    path1 = os.path.join(folder, f"{basename}.csv")
    path2 = os.path.join(folder, f"{basename}_teensy2.csv")
    out_path = os.path.join(folder, f"{basename}_merged.csv")

    df1 = pd.read_csv(path1)
    df2 = pd.read_csv(path2)

    assert len(df1) == len(df2), "❌ 두 CSV 파일의 행 개수가 다릅니다."

    # df_merged = pd.concat([df1, df2[["adc_val0", "adc_val1"]]], axis=1)
    # df_merged.columns = ["teensy_ts_us", "readable_time", "adc_val0", "adc_val1", "adc_val2", "adc_val3"]
    df_merged = pd.concat([df1, df2[["adc_val0"]]], axis=1)
    df_merged.columns = ["teensy_ts_us", "readable_time", "adc_val0", "adc_val1", "adc_val2"]

    df_merged.to_csv(out_path, index=False)
    print(f"[INFO] 저장 완료: {out_path}")

def csv_to_arduino_header(csv_path, output_path='phase_patterns.h'):
    with open(csv_path, newline='') as f:
        reader = csv.reader(f)
        header = next(reader)

        with open(output_path, 'w') as out:
            out.write('// Auto-generated pattern data from CSV\n\n')

            pattern_names = []
            for idx, row in enumerate(reader):
                name = f'pattern{idx}'
                pattern_names.append(name)

                data = ', '.join(f'0x{int(b):02X}' for b in row[3:])  # skip time, pos, name
                out.write(f'const byte {name}[] = {{ {data} }};\n')

            out.write('\nconst byte* patterns[] = {\n')
            for name in pattern_names:
                out.write(f'  {name},\n')
            out.write('};\n')

            out.write('\nconst int pattern_lengths[] = {\n')
            for name in pattern_names:
                out.write(f'  sizeof({name}),\n')
            out.write('};\n')


# 단독 실행 시 실행할 부분
if __name__ == "__main__":
    # file_path = os.path.join(".\data","extension", "2025-06-04_10-31-18.csv")
    # plot_resampled_range_2ch(file_path, start_us=96160008, end_us=98660008)
    # plot_resampled_range(file_path, start_us=8228464, end_us=10728464)
    # file_path2 = os.path.join(".\data","clip_data","wrist_flexion", "2025-05-17_14-44-23_clip.csv")
    # #clip_data(csv_path=file_path, output_path=file_path2)
    # clip_data_final(csv_path=file_path, output_path=file_path2)
    # plot_resampled_range(file_path2, start_us=238751732, end_us=238769732)
    
    # clip_all_data()

    #최종 버전 250522
    file_path2 = os.path.join(".\data","clip_data","wrist_flexion", "2025-06-04_10-49-00_clip.csv")
    # clip_data_dual_channel(csv_path=file_path, output_path=file_path2)
    # plot_resampled_range_2ch(file_path2, start_us=172312208, end_us=172330208)
    
    # merge_teensy_csvs_aligned(folder="data/wrist_flexion", basename="2025-06-02_17-36-34")
    # file_path = os.path.join(".\data","extension", "2025-06-04_10-31-18_merged.csv")
    plot_resampled_range_3ch(file_path2, start_us=19971118, end_us=19989118)
    # clip_data_triple_channel(csv_path=file_path, output_path=file_path)

    #merge_all_teensy(index_folder="data_index", data_folder="data/extension", gesture_name= "extension")
    #merge_all_teensy_final(index_folder="data_index", data_folder="data/wrist_flexion", gesture_name= "wrist_flexion", delete_original=True)

    # csv_to_arduino_header(csv_path="phase_patterns.csv")

    #clip_all_data_triple_channel()