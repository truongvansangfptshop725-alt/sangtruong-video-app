import streamlit as st
import time
import os
import tempfile
# Yêu cầu cài: pip install google-genai
from google import genai
from google.genai import types

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="SangTruong AI - Gemini 3 Pro Cloner", page_icon="🔥", layout="wide")

st.title("🔥 CỖ MÁY SAO CHÉP VIDEO - SANGTRUONG AUTOMATION")
st.markdown("🚀 **Sức mạnh:** **Gemini 3 Pro Preview** (Phân tích siêu sâu) + Veo 3.1 (Tạo video)")

# --- CỘT TRÁI: NHẬP LIỆU ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. NGUYÊN LIỆU ĐẦU VÀO")
    
    api_key = st.text_input("🔑 Google AI Studio API Key:", type="password", help="Lấy tại aistudio.google.com")
    
    # CẬP NHẬT MODEL THEO YÊU CẦU CỦA BẠN (CHỈ DÙNG GEMINI 3)
    # Lưu ý: Tên mã chính xác trong API thường là 'gemini-3.0-pro-preview' hoặc 'gemini-exp-1206'
    # Tôi sẽ để lựa chọn để bạn dễ đổi nếu Google thay đổi mã
    analysis_model_name = st.selectbox(
        "🧠 Model Phân Tích (Brain):", 
        [
            "gemini-3.0-pro-preview", # Ưu tiên số 1
            "gemini-exp-1206",        # Mã thử nghiệm của 2.0 Pro/3.0
        ]
    )
    
    # CHỌN MODEL TẠO VIDEO
    video_model_name = st.text_input("🎥 Model Tạo Video (Mặc định):", value="veo-3.1-generate-preview")

    uploaded_file = st.file_uploader("📂 Upload Video Gốc (Viral):", type=["mp4", "mov"])
    
    if uploaded_file is not None:
        st.video(uploaded_file)

    btn_start = st.button("🚀 BẮT ĐẦU SAO CHÉP NGAY (POWERED BY GEMINI 3)", type="primary")

# --- HÀM XỬ LÝ ---
def process_video_cloning(api_key, uploaded_file, analysis_model, video_model):
    client = genai.Client(api_key=api_key)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    try:
        # 1. UPLOAD VIDEO
        st.info("📤 Đang nạp video vào bộ nhớ AI...")
        video_file = client.files.upload(path=tmp_path)
        
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = client.files.get(name=video_file.name)
            
        if video_file.state.name == "FAILED":
            st.error("❌ Lỗi upload video!")
            return None

        # 2. PHÂN TÍCH BẰNG GEMINI 3 PRO (SIÊU PROMPT)
        st.info(f"👀 {analysis_model} đang dùng mắt thần phân tích video...")
        
        # SIÊU CÂU LỆNH CỦA BẠN (GIỮ NGUYÊN)
        analysis_prompt = """
        You are a world-class Visual Storytelling Expert. Your task is to meticulously analyze the provided video and generate a single, comprehensive, and vivid prompt in English. This prompt will be used by a Text-to-Video AI to create a new, visually stunning and emotionally engaging video that captures the essence and viral potential of the original.
        
        Analyze the following elements in order of priority:
        **1. Sound and Music:** Start by describing all audio elements in extreme detail. Include: ambient sounds, specific sound effects, and any dialogue. If there is music, identify its genre, key instruments, and the overall mood.
        **2. Cinematography and Style:** Describe the complete visual language. Camera Shot, Camera Angle, Camera Movement, Lens Effects, and the Overall Visual Style.
        **3. Subject and Action:** Detail the main subject(s). Describe their appearance, clothing, actions, and micro-expressions.
        **4. Setting and Environment:** Paint a picture of the location, key background objects, and their textures.
        **5. Lighting and Color:** Describe the lighting, shadows, and the dominant color palette.
        **6. The Viral Factor:** Briefly describe the single most important element that makes this video emotionally impactful or shareable.
        
        **Final Output Rule:** Combine ALL of the analysis above into a single, seamless, and coherent paragraph in English. The entire output must be one block of text. Do not use lists or headings in the final output. Start the paragraph with the description of the sound and music.
        """
        
        response = client.models.generate_content(
            model=analysis_model,
            contents=[video_file, analysis_prompt]
        )
        
        veo_prompt = response.text
        st.success("✅ Gemini 3 Pro đã viết xong kịch bản!")
        st.code(veo_prompt, language="text")

        # 3. TẠO VIDEO BẰNG VEO
        st.info(f"🎥 Đang gửi lệnh sang {video_model} để render...")
        
        operation = client.models.generate_videos(
            model=video_model,
            prompt=veo_prompt,
            config=types.GenerateVideosConfig(
                number_of_videos=1,
            )
        )
        
        with st.spinner("⏳ Veo đang vẽ... (Chờ khoảng 1-2 phút)..."):
            while not operation.done:
                time.sleep(5)
                pass 

            if operation.result and operation.result.video:
                return operation.result.video.uri
            else:
                st.error("❌ Lỗi Veo: Không trả về video. Kiểm tra lại quyền truy cập Model.")
                return None

    except Exception as e:
        st.error(f"❌ Lỗi hệ thống: {str(e)}")
        return None
    finally:
        try:
            os.remove(tmp_path)
        except:
            pass

# --- HIỂN THỊ KẾT QUẢ ---
with col2:
    st.subheader("2. KẾT QUẢ")
    if btn_start and api_key and uploaded_file:
        final_url = process_video_cloning(api_key, uploaded_file, analysis_model_name, video_model_name)
        if final_url:
            st.balloons()
            st.success("🎉 XONG! VIDEO MỚI CỦA BẠN:")
            st.video(final_url)
            st.markdown(f"🔗 [**Tải Video Về**]({final_url})")
