require('dotenv').config();
const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static('codebase')); // Phục vụ giao diện từ thư mục codebase/

// Kho dữ liệu Ngữ cảnh tài liệu (Context)
const COURSE_CONTEXTS = {
    "day04": `[Tài liệu: day04-multi-agent-system.pdf]
- Chủ đề: Multi-Agent Systems.
- Trọng tâm: Kiến trúc phối hợp giữa các Agent, phân chia nhiệm vụ và chia sẻ ngữ cảnh.
- Trích dẫn chính: day04-multi-agent-system.pdf (Trang 5, Trang 12).`,

    "day05": `[Tài liệu: day05-ai-product-thinking.pdf & day05-lecture-slides.pdf]
- Chủ đề: AI Product Thinking.
- Trọng tâm: Khác biệt giữa phần mềm truyền thống và sản phẩm AI, viết AI PRD, xây dựng Risk Register (Likelihood x Impact).
- Sản phẩm cần nộp: 1 bản PRD (3-5 trang) + Risk Matrix.
- Trích dẫn chính: day05-ai-product-thinking.pdf (Trang 3), day05-lecture-slides.pdf (Trang 24).
- Mối liên hệ bài cũ: Kế thừa kiến thức Multi-Agent System từ Day04 để thiết kế tính năng AI trong PRD ở Day05.`,

    "day05_slide": `[Tài liệu: day05-lecture-slides.pdf]
- Chủ đề: Anatomy of AI PRD.
- Trọng tâm: Thiết kế 4 lớp chỗ khó (Nguồn sự thật, Mơ hồ, Thẩm quyền, Domain).
- Trích dẫn chính: day05-lecture-slides.pdf (Trang 15).`
};

// API Route xử lý câu hỏi người dùng
app.post('/api/chat', async (req, res) => {
    const { prompt, lessonKey } = req.body;
    const apiKey = process.env.OPENAI_API_KEY;

    if (!apiKey) {
        return res.status(500).json({ error: "Chưa cấu hình OPENAI_API_KEY trong file .env!" });
    }

    const contextData = COURSE_CONTEXTS[lessonKey] || COURSE_CONTEXTS["day05"];
    
    const systemPrompt = `Bạn là VLearn Adaptive Tutor - Trợ lý học tập thông minh.
Nhiệm vụ của bạn:
1. Trả lời câu hỏi dựa trên Ngữ cảnh tài liệu được cung cấp dưới đây.
2. Nếu câu hỏi yêu cầu tóm tắt, hãy tóm tắt ngắn gọn 3-4 ý chính và LUÔN KÈM THEO trích dẫn nguồn [Tên file, Trang].
3. Nếu người học hỏi về liên kết bài cũ, hãy chỉ ra điểm kết nối với bài trước dựa trên dữ liệu context.
4. Nếu thông tin không có trong context, hãy lịch sự từ chối và đề xuất người học cung cấp thêm thông tin thay vì bịa đặt.

NGỮ CẢNH TÀI LIỆU HIỆN TẠI:
${contextData}`;

    try {
        const response = await fetch("https://api.openai.com/v1/chat/completions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: "gpt-4o-mini",
                messages: [
                    { role: "system", content: systemPrompt },
                    { role: "user", content: prompt }
                ],
                temperature: 0.2
            })
        });

        const data = await response.json();

        if (data.choices && data.choices.length > 0) {
            res.json({ reply: data.choices[0].message.content });
        } else {
            res.status(500).json({ error: "Lỗi kết nối API", details: data });
        }
    } catch (err) {
        res.status(500).json({ error: "Lỗi máy chủ: " + err.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`VLearn Server đang chạy tại: http://localhost:${PORT}`);
});