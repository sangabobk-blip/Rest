import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit.components.v1 as components

# 페이지 기본 설정
st.set_page_config(
    page_title="3D 인체 바이오파동 시뮬레이터",
    page_icon="🧬",
    layout="wide"
)

# 메인 제목
st.title("🧬 3D 입체 인체 생체신호(Bio-signal) 및 뇌파 시뮬레이터")
st.markdown("""
3D 인체 모델을 통해 신체 부위를 탐색하고, 각 부위에서 발생하는 **생체 전기 신호(EEG, ECG, EMG)의 수학적 중첩**을 시각화합니다.
""")

# --- 1. 3D 입체 인체 뷰어 (Three.js 기반) ---
st.subheader("🧍 3D 입체 인체 모델 (마우스로 드래그하여 360° 회전/확대 가능)")

# Three.js 3D 인체 렌더링 HTML/JS 코드
three_js_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; background-color: #0e1117; color: white; font-family: sans-serif; }
        #canvas-container { width: 100%; height: 420px; position: relative; }
        #info-overlay {
            position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7);
            padding: 8px 12px; border-radius: 8px; font-size: 13px; color: #00ffe1;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="canvas-container">
        <div id="info-overlay">💡 마우스 좌클릭 드래그: 회전 | 휠: 확대/축소 | 우클릭: 이동</div>
    </div>
    <script>
        const container = document.getElementById('canvas-container');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0e1117);

        const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
        camera.position.set(0, 1, 3.5);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.target.set(0, 0, 0);

        // 조명 설정
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);
        const dirLight = new THREE.DirectionalLight(0x00e5ff, 0.8);
        dirLight.position.set(5, 10, 7);
        scene.add(dirLight);

        // 3D 인체 마네킹 절차적 생성 (Procedural Humanoid Mesh)
        const bodyGroup = new THREE.Group();
        const mat = new THREE.MeshPhongMaterial({ color: 0x3a86ff, wireframe: true });
        const glowMat = new THREE.MeshPhongMaterial({ color: 0xff007f, emissive: 0x330011 });

        // 머리 (Brain)
        const head = new THREE.Mesh(new THREE.SphereGeometry(0.22, 16, 16), glowMat);
        head.position.y = 1.25;
        bodyGroup.add(head);

        // 목
        const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.09, 0.15, 12), mat);
        neck.position.y = 1.025;
        bodyGroup.add(neck);

        // 상체 (Heart/Chest)
        const chest = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.22, 0.65, 12), mat);
        chest.position.y = 0.625;
        bodyGroup.add(chest);

        // 심장 오버레이
        const heart = new THREE.Mesh(new THREE.SphereGeometry(0.09, 12, 12), new THREE.MeshBasicMaterial({color: 0xff4b4b}));
        heart.position.set(0.05, 0.68, 0.1);
        bodyGroup.add(heart);

        // 골반
        const pelvis = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.25, 0.25, 12), mat);
        pelvis.position.y = 0.175;
        bodyGroup.add(pelvis);

        // 팔 (Arm/Muscle)
        const leftArm = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.05, 0.7, 8), mat);
        leftArm.position.set(0.42, 0.55, 0);
        leftArm.rotation.z = -0.15;
        bodyGroup.add(leftArm);

        const rightArm = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.05, 0.7, 8), mat);
        rightArm.position.set(-0.42, 0.55, 0);
        rightArm.rotation.z = 0.15;
        bodyGroup.add(rightArm);

        // 다리
        const leftLeg = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.06, 0.85, 8), mat);
        leftLeg.position.set(0.14, -0.375, 0);
        bodyGroup.add(leftLeg);

        const rightLeg = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.06, 0.85, 8), mat);
        rightLeg.position.set(-0.14, -0.375, 0);
        bodyGroup.add(rightLeg);

        scene.add(bodyGroup);

        // 애니메이션 루프 (인체 천천히 회전)
        function animate() {
            requestAnimationFrame(animate);
            bodyGroup.rotation.y += 0.005;
            controls.update();
            renderer.render(scene, camera);
        }
        animate();

        window.addEventListener('resize', () => {
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        });
    </script>
</body>
</html>
"""

components.html(three_js_code, height=430)

st.markdown("---")

# --- 2. 신체 부위 선택 및 인터랙션 ---
st.subheader("🎯 탐구할 신체 부위 선택")
selected_organ = st.radio(
    "분석할 신체 부위를 선택하세요:",
    ["🧠 머리 (뇌파 - EEG)", "🫀 가슴 (심전도 - ECG)", "💪 팔/다리 (근전도 - EMG)"],
    horizontal=True
)

t = np.linspace(0, 1, 1000)

# --- A. 🧠 머리 (뇌파 - EEG) ---
if "🧠 머리" in selected_organ:
    st.markdown("### 🧠 뇌파(EEG) 삼각함수 중첩 및 FFT 분석")
    st.info("뇌세포(신경원)의 동시 전기 활동은 주파수와 진폭이 다른 여러 파동의 합성으로 나타납니다.")

    col_side, col_main = st.columns([1, 2])

    with col_side:
        st.subheader("⚙️ 뇌파 파동 조절")
        delta_f = st.slider("델타파 (Delta: 수면)", 0.5, 4.0, 2.0)
        theta_f = st.slider("세타파 (Theta: 명상)", 4.0, 8.0, 6.0)
        alpha_f = st.slider("알파파 (Alpha: 휴식)", 8.0, 13.0, 10.0)
        beta_f = st.slider("베타파 (Beta: 집중)", 13.0, 30.0, 20.0)
        
        noise_level = st.slider("무작위 노이즈 세기", 0.0, 1.5, 0.2)

    with col_main:
        w_delta = 1.0 * np.sin(2 * np.pi * delta_f * t)
        w_theta = 0.8 * np.sin(2 * np.pi * theta_f * t)
        w_alpha = 1.5 * np.sin(2 * np.pi * alpha_f * t)
        w_beta = 1.2 * np.sin(2 * np.pi * beta_f * t)
        noise = np.random.normal(0, noise_level, len(t))

        eeg_signal = w_delta + w_theta + w_alpha + w_beta + noise

        df_eeg = pd.DataFrame({"Time (s)": t, "Synthesized EEG": eeg_signal}).set_index("Time (s)")
        st.line_chart(df_eeg, color="#FF4B4B")

        # FFT 분석
        fft_res = np.fft.fft(eeg_signal)
        fft_freq = np.fft.fftfreq(len(t), d=t[1]-t[0])
        pos_mask = fft_freq > 0

        fig, ax = plt.subplots(figsize=(8, 2.5))
        ax.plot(fft_freq[pos_mask], np.abs(fft_res[pos_mask]) * 2 / len(t), color='purple')
        ax.set_xlim(0, 35)
        ax.set_title("FFT Frequency Spectrum (Hz)")
        ax.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)

# --- B. 🫀 가슴 (심전도 - ECG) ---
elif "🫀 가슴" in selected_organ:
    st.markdown("### 🫀 심전도(ECG) 주기적 펄스 파동 시뮬레이션")
    st.info("심장의 동방노드(SA node)에서 발생하는 주기적 전기 자극(P-QRS-T 파형)을 모델링합니다.")

    bpm = st.slider("심박수 (BPM - Beats Per Minute)", 40, 180, 75)
    
    # ECG 파형 주기 계산
    freq = bpm / 60.0
    # 합성 심전도 근사파 생성 (푸리에 급수적 합성)
    ecg_signal = (
        0.1 * np.sin(2 * np.pi * freq * t) +
        0.8 * np.sin(2 * np.pi * freq * t * 5)**10 +  # QRS 군 (뾰족한 피크)
        0.2 * np.sin(2 * np.pi * freq * t * 2 + 1)   # T파
    )
    ecg_signal += np.random.normal(0, 0.03, len(t))

    df_ecg = pd.DataFrame({"Time (s)": t, "ECG Pulse": ecg_signal}).set_index("Time (s)")
    st.line_chart(df_ecg, color="#00E5FF")

    st.markdown("""
    - **P파:** 심방 탈분극
    - **QRS군:** 심실 탈분극 (수축)
    - **T파:** 심실 재분극 (이완)
    """)

# --- C. 💪 팔/다리 (근전도 - EMG) ---
else:
    st.markdown("### 💪 근전도(EMG) 근육 수축 자극 파동")
    st.info("골격근이 수축할 때 근섬유에서 발생하는 고주파 무작위 전위차(EMG)를 나타냅니다.")

    muscle_force = st.slider("근육 수축 강도 (%)", 10, 100, 50)
    
    # 수축 강도에 따른 버스트(Burst) 임의 파동 생성
    emg_freq = np.random.uniform(50, 150)
    base_emg = np.sin(2 * np.pi * emg_freq * t)
    amplitude_env = (muscle_force / 100.0) * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * t))
    emg_signal = base_emg * amplitude_env + np.random.normal(0, muscle_force / 200.0, len(t))

    df_emg = pd.DataFrame({"Time (s)": t, "EMG Signal": emg_signal}).set_index("Time (s)")
    st.line_chart(df_emg, color="#00FF7F")

    st.markdown("""
    - **근전도 특징:** 근육의 수축력이 강해질수록 개입하는 운동 단위(Motor Unit)가 늘어나 파동의 **진폭(Amplitude)**과 **밀도**가 커집니다.
    """)

# --- 3. 하단 학술 요약 ---
with st.expander("🔬 생명과학 & 수학 통합 탐구 포인트"):
    st.markdown("""
    1. **생체 전위차의 원리:** 인체의 신경과 근육 세포막에 존재하는 이온( $Na^+$, $K^+$ 등)의 이동으로 발생하는 막전위 변화가 생체 신호의 근원입니다.
    2. **수학적 중첩 (Superposition):** 미세한 생체 전위차들이 중첩되어 피부 표면에서 복잡한 삼각함수의 합 형태(파동)로 측정됩니다.
    3. **신호 처리와 BCI 기술:** 복잡한 합성파를 푸리에 변환(FFT)으로 분해하면 의도한 동작이나 뇌 상태를 해독할 수 있어 BCI(뇌-컴퓨터 인터페이스) 기술의 기초가 됩니다.
    """)
