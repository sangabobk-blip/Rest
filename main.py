import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 페이지 기본 설정
st.set_page_config(
    page_title="뇌파(EEG) 시각화 및 삼각함수 합성 시뮬레이터",
    page_icon="🧠",
    layout="wide"
)

# 제목 및 설명
st.title("🧠 뇌파(EEG) 시각화 및 삼각함수 중첩 시뮬레이터")
st.markdown("""
불규칙해 보이는 뇌파 신호는 사실 서로 다른 주파수와 진폭을 가진 **여러 삼각함수(사인·코사인 파동)들의 수학적 중첩(합성)**입니다.  
아래 슬라이더를 조절하여 각 뇌파 파동을 생성하고, 합성된 최종 뇌파 파형을 확인해보세요.
""")

st.sidebar.header("⚙️ 뇌파 구성 요인 설정 (주파수 & 진폭)")

# 1. 델타파 (Delta: 0.5 ~ 4 Hz) - 깊은 수면
st.sidebar.subheader("1. 델타파 (Delta Wave)")
st.sidebar.caption("0.5~4 Hz | 깊은 수면 상태")
delta_freq = st.sidebar.slider("델타파 주파수 (Hz)", 0.5, 4.0, 2.0, 0.1)
delta_amp = st.sidebar.slider("델타파 진폭 (Amp)", 0.0, 5.0, 1.0, 0.1)

# 2. 세타파 (Theta: 4 ~ 8 Hz) - 명상, 얕은 수면
st.sidebar.subheader("2. 세타파 (Theta Wave)")
st.sidebar.caption("4~8 Hz | 명상, 창의적 생각, 얕은 수면")
theta_freq = st.sidebar.slider("세타파 주파수 (Hz)", 4.0, 8.0, 6.0, 0.1)
theta_amp = st.sidebar.slider("세타파 진폭 (Amp)", 0.0, 5.0, 0.5, 0.1)

# 3. 알파파 (Alpha: 8 ~ 13 Hz) - 휴식, 안정한 상태
st.sidebar.subheader("3. 알파파 (Alpha Wave)")
st.sidebar.caption("8~13 Hz | 편안한 휴식, 눈을 감은 상태")
alpha_freq = st.sidebar.slider("알파파 주파수 (Hz)", 8.0, 13.0, 10.0, 0.1)
alpha_amp = st.sidebar.slider("알파파 진폭 (Amp)", 0.0, 5.0, 2.0, 0.1)

# 4. 베터파 (Beta: 13 ~ 30 Hz) - 집중, 활발한 뇌 활동
st.sidebar.subheader("4. 베터파 (Beta Wave)")
st.sidebar.caption("13~30 Hz | 일반적인 의식, 집중, 문제 해결")
beta_freq = st.sidebar.slider("베터파 주파수 (Hz)", 13.0, 30.0, 20.0, 0.5)
beta_amp = st.sidebar.slider("베터파 진폭 (Amp)", 0.0, 5.0, 1.5, 0.1)

# 노이즈 추가 옵션
st.sidebar.markdown("---")
add_noise = st.sidebar.checkbox("미세 무작위 노이즈(Noise) 추가", value=False)
noise_level = st.sidebar.slider("노이즈 세기", 0.0, 2.0, 0.3, 0.1) if add_noise else 0.0

# 시간 축 생성 (1초 동안의 신호, 1000개 샘플링)
t = np.linspace(0, 1, 1000)

# 각각의 삼각함수 파동 계산: A * sin(2 * pi * f * t)
wave_delta = delta_amp * np.sin(2 * np.pi * delta_freq * t)
wave_theta = theta_amp * np.sin(2 * np.pi * theta_freq * t)
wave_alpha = alpha_amp * np.sin(2 * np.pi * alpha_freq * t)
wave_beta = beta_amp * np.sin(2 * np.pi * beta_freq * t)

# 노이즈 생성
noise = np.random.normal(0, noise_level, size=t.shape) if add_noise else np.zeros_like(t)

# 개별 파동 합성 (삼각함수의 중첩)
combined_wave = wave_delta + wave_theta + wave_alpha + wave_beta + noise

# 데이터프레임 생성 (Streamlit 차트용)
df_individual = pd.DataFrame({
    'Time (s)': t,
    'Delta': wave_delta,
    'Theta': wave_theta,
    'Alpha': wave_alpha,
    'Beta': wave_beta
}).set_index('Time (s)')

df_combined = pd.DataFrame({
    'Time (s)': t,
    'Combined EEG Signal': combined_wave
}).set_index('Time (s)')

# --- 메인 화면 레이아웃 구성 ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 1. 개별 뇌파 파동 (각 삼각함수)")
    st.line_chart(df_individual)

with col2:
    st.subheader("🧠 2. 최종 합성 뇌파 (삼각함수의 중첩)")
    st.line_chart(df_combined, color="#FF4B4B")

# 푸리에 변환 (FFT) 분석 섹션
st.markdown("---")
st.subheader("🔬 푸리에 변환 (FFT)을 통한 주파수 영역 분석")
st.markdown("""
**푸리에 변환(Fourier Transform)**은 복잡한 합성 파형을 다시 원본 삼각함수(주파수 성분)들로 분해하는 수학적 기술입니다.  
아래 그래프는 현재 합성 뇌파에 어떤 주파수 성분이 얼마만큼 포함되어 있는지를 보여줍니다.
""")

# FFT 계산
fft_result = np.fft.fft(combined_wave)
fft_freq = np.fft.fftfreq(len(t), d=t[1]-t[0])

# 양의 주파수 영역만 선택
positive_freq_idx = fft_freq > 0
freqs = fft_freq[positive_freq_idx]
magnitudes = np.abs(fft_result[positive_freq_idx]) * 2 / len(t)

# Matplotlib으로 FFT 스펙트럼 시각화
fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(freqs, magnitudes, color='purple')
ax.set_xlim(0, 35)
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Amplitude")
ax.set_title("FFT Frequency Spectrum Analysis")
ax.grid(True, linestyle='--', alpha=0.6)

st.pyplot(fig)

# 하단 요약 및 원리 설명
with st.expander("📌 학술적 배경 및 탐구 포인트"):
    st.markdown("""
    - **삼각함수의 중첩 원리:** 복잡한 뇌파 $y(t)$는 아래와 같이 여러 사인 파동의 합으로 표현될 수 있습니다.
      $$y(t) = \\sum_{i} A_i \\sin(2\\pi f_i t + \\phi_i)$$
    - **생명과학 및 뇌과학과의 연계:** 뇌 세포의 동시적 전기 활동(생전기)은 머리표면에서 종합적인 전위차 형태로 측정됩니다.
    - **BCI 및 뇌파 분석의 기초:** 생체 신호 처리 과정에서는 푸리에 변환을 통해 합성된 신호에서 주파수를 추출함으로써 현재 사용자의 뇌 상태(집중, 수면, 스트레스 등)를 정밀하게 파악합니다.
    """)
