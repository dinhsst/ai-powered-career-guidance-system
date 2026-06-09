1. Tin cậy (Reliability) Đảm bảo tính nhất quán của lời khuyên và triệt tiêu hiện tượng "ảo tưởng" (hallucination). 
    - Rủi ro: LLM tự bịa ra các ngành nghề không có thật, đưa ra lộ trình học tập phi thực tế, hoặc dự báo sai lệch về nhu cầu thị trường lao động trong tương lai.
    - Giải pháp kỹ thuật: Áp dụng RAG (Retrieval-Augmented Generation): Không để AI tự sinh văn bản tự do. Cần kết nối API với các nguồn dữ liệu chuẩn hóa: Danh mục nghề nghiệp của Bộ LĐ-TB&XH, báo cáo thị trường việc làm uy tín, hoặc dữ liệu tuyển sinh từ các trường Đại học/Cao đẳng.Kiểm soát tham số (Temperature): Đặt temperature thấp (gần bằng 0) khi gọi LLM API để câu trả lời mang tính chính xác và nhất quán cao, tránh sự bay bổng sáng tạo không cần thiết.Hệ thống chấm điểm câu trả lời (Evaluation Metric): Sử dụng các framework như Ragas hoặc TruLens để đo lường độ trung thực (Faithfulness) và mức độ liên quan (Answer Relevance) của câu trả lời dựa trên ngữ cảnh được cung cấp.
2. Thiên vị (Bias/Fairness) Đảm bảo cơ hội công bằng, không phân biệt đối xử dựa trên các đặc tính nhân khẩu học.
    - Rủi ro:
        + Giới tính: AI tự động hướng nam giới vào khối ngành STEM và nữ giới vào khối ngành Sư phạm, Ngôn ngữ.
        + Vùng miền & Kinh tế: Hệ thống chỉ gợi ý các trường đại học học phí cao ở thành phố lớn, bỏ qua các lựa chọn phù hợp tại địa phương hoặc các trường có chính sách học bổng tốt cho học sinh vùng sâu vùng xa.
    - Giải pháp kỹ thuật:
        + Khử nhiễu dữ liệu đầu vào (De-biasing Prompting): Sử dụng kỹ thuật định hướng vai trò (System Prompt) nghiêm ngặt: "Bạn là một chuyên gia tư vấn hướng nghiệp trung lập. Tuyệt đối không đưa ra gợi ý dựa trên định kiến giới tính, vùng miền hoặc tôn giáo.
        + Cân bằng dữ liệu (Fairness-aware ML): Nếu dùng mô hình ML/DL tự huấn luyện để phân loại tính cách/ngành nghề (ví dụ: dựa trên trắc nghiệm Holland), cần đảm bảo tập dữ liệu huấn luyện (Training dataset) có tỷ lệ phân bố đồng đều giữa các nhóm giới tính và vùng miền.
3. Chống chịu và Bảo mật (Robustness) Đảm bảo hệ thống vận hành ổn định trước dữ liệu nhiễu và các cuộc tấn công cố ý.
    - Rủi ro: Học sinh cố tình nhập dữ liệu sai lệch (ví dụ: điểm số âm, sở thích mâu thuẫn) để làm hệ thống bị lỗi, hoặc sử dụng Prompt Injection để ép AI trả lời các nội dung độc hại, không liên quan đến hướng nghiệp.
    - Giải pháp kỹ thuật:
        + Lớp lọc dữ liệu đầu vào (Input Validation & Guardrails): Sử dụng các thư viện như NeMo Guardrails hoặc Llama Guard để phát hiện và chặn đứng các câu lệnh tấn công (Prompt Injection) trước khi chúng tiếp cận mô hình lõi.
        + Xử lý dữ liệu nhiễu (Data Noise Handling): Thiết kế schema kiểm tra dữ liệu nghiêm ngặt ở tầng Frontend/Backend (ví dụ: Điểm số phải nằm trong khoảng 0-10, các câu hỏi trắc nghiệm bắt buộc phải chọn theo format định sẵn).
        + Cơ chế dự phòng (Fallback Mechanism): Khi LLM API gặp sự cố (quá tải, mất kết nối), hệ thống tự động chuyển hướng sang mô hình ML dạng Rule-based truyền thống để đưa ra kết quả hướng nghiệp cơ bản thay vì báo lỗi hệ thống.
4. Tác động xã hội lên nhóm yếu thế (Social Impact)Hỗ trợ học sinh nghèo, học sinh vùng nông thôn, dân tộc thiểu số và học sinh có học lực trung bình/kém.
    - Rủi ro: Ứng dụng chỉ phục vụ tốt cho "học sinh giỏi, có điều kiện", vô tình bỏ rơi hoặc làm nản chí các nhóm yếu thế khi liên tục gợi ý những lộ trình vượt quá khả năng tài chính hoặc năng lực hiện tại của họ.
    - Giải pháp tính năng:
        + Trục tối ưu chi phí: Thêm bộ lọc "Mức học phí kỳ vọng" hoặc "Lộ trình vừa học vừa làm", "Hệ cao đẳng nghề/trung cấp". AI phải ưu tiên gợi ý các trường có chính sách hỗ trợ học bổng, miễn giảm học phí cho học sinh nghèo, dân tộc thiểu số.
        + Cá nhân hóa theo năng lực thực tế: Đối với học sinh có học lực trung bình, AI không chỉ trích mà cần thiết lập lộ trình cải thiện từng bước, gợi ý các ngành nghề thực tế có nhu cầu tuyển dụng cao thay vì chỉ tập trung vào các ngành "hot" điểm chuẩn ngất ngưỡng.
        + Đa dạng hóa ngôn ngữ/giao diện: Hỗ trợ nhập liệu bằng giọng nói (cho học sinh thao tác chưa quen trên máy tính) và tối ưu hóa giao diện chạy mượt mà ngay cả trên điện thoại cấu hình thấp, mạng 3G/4G yếu.
5. Minh bạch và Giải thích (Explainability) Giúp học sinh và phụ huynh hiểu rõ "Tại sao AI lại đưa ra lời khuyên này?
    - Rủi ro: AI hoạt động như một "hộp đen" (Black box). Gợi ý một học sinh đi học ngành Công nghệ thông tin nhưng không giải thích lý do, khiến người dùng hoang mang và không có cơ sở để tin tưởng đưa ra quyết định cuộc đời.
    - Giải pháp kỹ thuật & Trải nghiệm (UX):
        + Giải thích dựa trên bằng chứng (Chain-of-Thought Prompting): Ép LLM giải thích tường tận các bước tư duy: Dựa vào điểm số môn Toán (8.5) + Sở thích thích mày mò máy tính + Tính cách hướng nội -> Đề xuất ngành Khoa học dữ liệu.
        + Áp dụng XAI (Explainable AI) cho mô hình ML: Nếu hệ thống dùng mô hình phân loại (Random Forest, SVM...), hãy sử dụng SHAP (SHapley Additive exPlanations) hoặc LIME để vẽ biểu đồ trực quan hóa: Trực giác (30%), Điểm số (40%), Khả năng tài chính (30%) đã đóng góp thế nào vào kết quả ngành nghề được gợi ý.
        + Ngôn ngữ bình dân (Accessible Language): Chuyển đổi các thuật ngữ học thuật phức tạp sang ngôn ngữ dễ hiểu đối với học sinh cấp 2, cấp 3 và phụ huynh ở nông thôn (ví dụ: Thay vì nói "Ngành này phù hợp với chỉ số trí tuệ logic-toán học cao", hãy nói "Bạn có thế mạnh ở các môn tính toán và tư duy tìm nguyên nhân").💡 
6. Tech Stack:
    - Frontend: Angular + angular material
    - Backend: Python (FastAPI) để dễ dàng tích hợp các thư viện AI.
    - AI Core: Trắc nghiệm & Khớp điểm số (ML): Scikit-learn (Mô hình Classification/Recommendation).
    - Tư vấn sâu & Trò chuyện (LLM API): Gemini 1.5 Flash (để tiết kiệm chi phí API), kết hợp thư viện LangChain để làm RAG kết nối database giáo dục.
    - Bảo mật: Dùng Guardrails AI để chặn prompt injection.