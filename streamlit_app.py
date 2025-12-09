import streamlit as st
import time
import os
import tempfile
# Yêu cầu cài: pip install google-genai
from google import genai
from google.genai import types

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="SangTruong AI - Video Cloner", page_icon="🔥", layout="wide")

st.title("🔥 CỖ MÁY SAO CHÉP VIDEO - SANGTRUONG AUTOMATION")
st.markdown("🚀 **Sức mạnh:** **Gemini 3 Pro** + Veo 3.1 (Fixed Upload)")

# --- CỘT TRÁI: NHẬP LIỆU ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. NGUYÊN LIỆU ĐẦU VÀO")
    
    api_key = st.text_input("🔑 Google AI Studio API Key:", type="password", help="Lấy tại aistudio.google.com")
    
    analysis_model_name = st.selectbox(
        "🧠 Model Phân Tích (Brain):", 
        [
            "gemini-2.0-flash-exp", # Dùng Flash cho nhanh và ổn định
            "gemini-1.5-pro-002",
        ]
    )
    
    video_model_name = st.text_input("🎥 Model Tạo Video (Mặc định):", value="veo-3.1-generate-preview")

    uploaded_file = st.file_uploader("📂 Upload Video Gốc (Viral):", type=["mp4", "mov"])
    
    if uploaded_file is not None:
        st.video(uploaded_file)

    btn_start = st.button("🚀 BẮT ĐẦU SAO CHÉP NGAY", type="primary")

# --- HÀM XỬ LÝ ---
def process_video_cloning(api_key, uploaded_file, analysis_model, video_model):
    client = genai.Client(api_key=api_key)
    
    # Lưu file tạm
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    try:
        # 1. UPLOAD VIDEO (ĐÃ SỬA LỖI - Dùng file object)
        st.info("📤 Đang nạp video vào bộ nhớ AI...")
        
        # Sửa lỗi: Mở file ra để upload thay vì dùng path trực tiếp nếu SDK cũ
        with open(tmp_path, "rb") as f:
            # Cách upload chuẩn cho google-genai SDK mới
            video_file = client.files.upload(file=f, config={'mime_type': 'video/mp4'})
        
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = client.files.get(name=video_file.name)
            
        if video_file.state.name == "FAILED":
            st.error("❌ Lỗi upload video!")
            return None

        # 2. PHÂN TÍCH (GEMINI)
        st.info(f"👀 {analysis_model} đang phân tích...")
        
        analysis_prompt = "Describe this video in detail to recreate it with AI. Focus on camera, lighting, action, mood. Output only the prompt in English."
        
        response = client.models.generate_content(
            model=analysis_model,
            contents=[video_file, analysis_prompt]
        )
        
        veo_prompt = response.text
        st.success("✅ Đã có kịch bản!")
        st.code(veo_prompt, language="text")

        # 3. TẠO VIDEO (VEO)
        st.info(f"🎥 Đang gửi lệnh sang {video_model}...")
        
        operation = client.models.generate_videos(
            model=video_model,
            prompt=veo_prompt,
            config=types.GenerateVideosConfig(number_of_videos=1)
        )
        
        with st.spinner("⏳ Veo đang vẽ... (Chờ 1-2 phút)..."):
            while not operation.done:
                time.sleep(5)
                pass 

            if operation.result and operation.result.video:
                return operation.result.video.uri
            else:
                st.error("❌ Lỗi Veo: Không trả về video. (Check Quota/Quyền).")
                return None

    except Exception as e:
        # Fallback error handling
        st.error(f"❌ Lỗi hệ thống: {str(e)}")
        # Gợi ý fix nếu lỗi thư viện
        if "keyword argument" in str(e):
             st.warning("💡 Gợi ý: Hãy thử cập nhật lại file requirements.txt trên GitHub thành: google-genai>=0.2.0")
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
