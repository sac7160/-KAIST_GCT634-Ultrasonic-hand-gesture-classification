import os
import zipfile
import pandas as pd
import numpy as np
from io import TextIOWrapper
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from scipy.stats import skew, kurtosis
import matplotlib.pyplot as plt
import itertools

from umap import UMAP
from scipy.signal import spectrogram

# 현재 py 파일 위치 기준으로 zip 경로 설정
CURRENT_DIR = os.path.dirname(__file__)
ZIP_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "..", "data", "3mics_clip_data_V0606.zip"))



def extract_features(adc0, adc1):
    feat = []
    for signal in [adc0, adc1]:
        feat.append(signal.mean())
        feat.append(signal.std())
        feat.append(signal.max())
        feat.append(signal.min())
        feat.append(skew(signal))
        feat.append(kurtosis(signal))
        feat.append((signal ** 2).sum())  # Energy
        feat.append((signal > 300).sum())  # Peak count
    return feat


X, y = [], []
X_all, y_all = [], []


#################################
#제스쳐별 스펙토그램
# Spectrogram 특징 추출
# def extract_spectrogram_features(adc0, adc1, fs=500000):
#     def get_spec(signal):
#         f, t, Sxx = spectrogram(signal, fs=fs, nperseg=256, noverlap=128)
#         return np.log1p(Sxx).flatten()  # log scale
#     return np.concatenate([get_spec(adc0), get_spec(adc1)])

# # 전체 데이터 로딩
# X_all, y_all = [], []

# with zipfile.ZipFile(ZIP_PATH, 'r') as zipf:
#     for zipinfo in zipf.infolist():
#         if zipinfo.filename.endswith(".csv") and "__MACOSX" not in zipinfo.filename:
#             label = zipinfo.filename.split("/")[1]
#             with zipf.open(zipinfo.filename) as file:
#                 df = pd.read_csv(TextIOWrapper(file, 'utf-8'))
#                 if "adc_val0" not in df.columns or "adc_val1" not in df.columns:
#                     continue
#                 adc0 = df["adc_val0"].values.astype(np.float32)
#                 adc1 = df["adc_val1"].values.astype(np.float32)
#                 X_all.append(extract_spectrogram_features(adc0, adc1))
#                 y_all.append(label)

# X_all = np.array(X_all)
# y_all = np.array(y_all)

# # 두 제스처씩 조합
# unique_labels = np.unique(y_all)
# pairs = list(itertools.combinations(unique_labels, 2))

# # 시각화
# fig, axes = plt.subplots(nrows=3, ncols=7, figsize=(21, 9))
# axes = axes.flatten()

# for idx, (label1, label2) in enumerate(pairs):
#     ax = axes[idx]
#     mask = np.isin(y_all, [label1, label2])
#     X_pair = X_all[mask]
#     y_pair = y_all[mask]

#     X_pair = StandardScaler().fit_transform(X_pair)

#     tsne = TSNE(n_components=2, perplexity=min(30, len(X_pair) - 1), random_state=42)
#     X_embedded = tsne.fit_transform(X_pair)

#     for label in [label1, label2]:
#         idxs = y_pair == label
#         ax.scatter(X_embedded[idxs, 0], X_embedded[idxs, 1], label=label, s=10, alpha=0.7)

#     ax.set_title(f"{label1} vs {label2}")
#     ax.set_xticks([])
#     ax.set_yticks([])
#     ax.legend(fontsize="small")

# plt.tight_layout()
# plt.suptitle("t-SNE of Gesture Pairs (Spectrogram Features)", fontsize=16, y=1.02)
# plt.show()


##########################
#spectogram으로 1개
########################33
# def extract_spectrogram_features(adc0, adc1, fs=500000):
#     """
#     각 채널에 대해 log-scaled spectrogram을 계산한 후 flatten
#     """
#     def get_spec(signal):
#         f, t, Sxx = spectrogram(signal, fs=fs, nperseg=256, noverlap=128)
#         Sxx = np.log1p(Sxx)
#         return Sxx.flatten()

#     feat0 = get_spec(adc0)
#     feat1 = get_spec(adc1)
#     return np.concatenate([feat0, feat1])

# X_all, y_all = [], []

# print(f"[INFO] ZIP 파일 로드: {ZIP_PATH}")
# with zipfile.ZipFile(ZIP_PATH, 'r') as zipf:
#     for zipinfo in zipf.infolist():
#         if zipinfo.filename.endswith(".csv") and "__MACOSX" not in zipinfo.filename:
#             label = zipinfo.filename.split("/")[1]
#             with zipf.open(zipinfo.filename) as file:
#                 df = pd.read_csv(TextIOWrapper(file, 'utf-8'))
#                 if "adc_val0" not in df.columns or "adc_val1" not in df.columns:
#                     continue
#                 adc0 = df["adc_val0"].values.astype(np.float32)
#                 adc1 = df["adc_val1"].values.astype(np.float32)
#                 features = extract_spectrogram_features(adc0, adc1)
#                 X_all.append(features)
#                 y_all.append(label)

# X_all = np.array(X_all)
# y_all = np.array(y_all)

# print(f"[INFO] 총 {len(X_all)}개 샘플 로드 완료.")

# # 정규화
# X_scaled = StandardScaler().fit_transform(X_all)

# # t-SNE
# tsne = TSNE(n_components=2, perplexity=min(30, len(X_all) - 1), random_state=42)
# X_embedded = tsne.fit_transform(X_scaled)

# # 시각화
# plt.figure(figsize=(10, 7))
# for label in np.unique(y_all):
#     idxs = y_all == label
#     plt.scatter(X_embedded[idxs, 0], X_embedded[idxs, 1], label=label, alpha=0.6)

# plt.title("t-SNE Visualization with Time-Frequency Features")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()

###########################
#제스쳐별 tSNE, UMAP
############################
EXPECTED_LENGTH = 9001 * 2  # 2채널 flatten 된 길이 (9001행 * 2열)

with zipfile.ZipFile(ZIP_PATH, 'r') as zipf:
    for zipinfo in zipf.infolist():
        if zipinfo.filename.endswith(".csv") and "__MACOSX" not in zipinfo.filename:
            label = zipinfo.filename.split("/")[1]
            with zipf.open(zipinfo.filename) as file:
                df = pd.read_csv(TextIOWrapper(file, 'utf-8'))

                if "adc_val0" not in df.columns or "adc_val1" not in df.columns:
                    continue

                signal = df[["adc_val0", "adc_val1"]].values.flatten()

                if len(signal) != EXPECTED_LENGTH:
                    print(f"[WARNING] Skipping {zipinfo.filename}, unexpected length: {len(signal)}")
                    continue  # 길이 다른 경우 제외

                X_all.append(signal)
                y_all.append(label)

X_all = np.array(X_all, dtype=np.float32)
y_all = np.array(y_all)

# 제스처 종류 조합
unique_labels = np.unique(y_all)
pairs = list(itertools.combinations(unique_labels, 2))

# 시각화 준비
fig, axes = plt.subplots(nrows=3, ncols=7, figsize=(21, 9))
axes = axes.flatten()

for idx, (label1, label2) in enumerate(pairs):
    ax = axes[idx]
    mask = np.isin(y_all, [label1, label2])
    X_pair = X_all[mask]
    y_pair = y_all[mask]

    # 정규화
    X_pair = StandardScaler().fit_transform(X_pair)

    # t-SNE
    # tsne = TSNE(n_components=2, perplexity=min(30, len(X_pair)-1), random_state=42)
    # X_embedded = tsne.fit_transform(X_pair)

    X_embedded = UMAP(n_neighbors=15, min_dist=0.1).fit_transform(X_pair)

    # 시각화
    for label in [label1, label2]:
        idxs = y_pair == label
        ax.scatter(X_embedded[idxs, 0], X_embedded[idxs, 1], label=label, alpha=0.6, s=10)

    ax.set_title(f"{label1} vs {label2}")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.legend(fontsize="small")

plt.tight_layout()
plt.suptitle("t-SNE of Gesture Pairs", fontsize=16, y=1.02)
plt.show()


##########################
#t-SNE 1개
##########################
# with zipfile.ZipFile(ZIP_PATH, 'r') as zipf:
#     for zipinfo in zipf.infolist():
#         if zipinfo.filename.endswith(".csv") and "__MACOSX" not in zipinfo.filename:
#             label = zipinfo.filename.split("/")[1]
#             with zipf.open(zipinfo.filename) as file:
#                 df = pd.read_csv(TextIOWrapper(file, 'utf-8'))

#                 if "adc_val0" not in df.columns or "adc_val1" not in df.columns:
#                     continue

#                 # 두 채널 모두 포함하여 flatten
#                 signal = df[["adc_val0", "adc_val1"]].values.flatten()
#                 X.append(signal)
#                 y.append(label)

# X = np.array(X)
# y = np.array(y)

# print(f"[INFO] 총 {len(X)}개 샘플 로드 완료. 각 벡터 shape: {X[0].shape}")

# # 정규화 (샘플 단위로 전체 채널 포함)
# scaler = StandardScaler()
# X_scaled = scaler.fit_transform(X)

# # t-SNE
# perplexity = min(30, len(X_scaled) - 1)
# tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42)
# X_embedded = tsne.fit_transform(X_scaled)

# # 시각화
# plt.figure(figsize=(10, 7))
# for label in np.unique(y):
#     idxs = np.array(y) == label
#     plt.scatter(X_embedded[idxs, 0], X_embedded[idxs, 1], label=label, alpha=0.6)

# plt.title("t-SNE Visualization of Gesture Data (Raw Signal Flattened)")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()
