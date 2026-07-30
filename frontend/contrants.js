// constants.js
// Danh sách các Slide có sẵn trong thư mục slides/ (Để dùng cho API thật)
export const SLIDE_FILES = [
    { id: 'day05', label: 'Day 05 - AI Product Thinking', path: '../slides/day05-ai-product-thinking-requirements.pdf' },
    { id: 'day04', label: 'Day 04 - Multi-Agent Systems', path: '../slides/day04-llm-multi-agent.pdf' } // Ví dụ
];

// Mock Content hiển thị trên giao diện (Vì chưa có PDF viewer thật)
export const MOCK_DATA = {
    "day05": {
        title: "Mục tiêu Ngày 5 - AI Product Thinking",
        content: `<h4>Mục tiêu Ngày 5</h4><br><p>1. Hiểu khác biệt giữa <span class="highlight-text">AI product</span> và software feature thông thường.</p><p>2. Biết cách chuyển user needs thành requirements đo được.</p><p>3. Viết PRD và Risk Register.</p>`,
    },
    "day04": {
        title: "Mục tiêu Ngày 4 - Multi-Agent Systems",
        content: `<h4>Mục tiêu Ngày 4</h4><br><p>• Học về kiến trúc Multi-Agent System.<br>• Cách phân chia role và giao tiếp giữa các agent.</p>`,
    }
};