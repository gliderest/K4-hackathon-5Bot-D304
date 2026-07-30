// script.js
import { SLIDE_FILES, MOCK_DATA } from './constants.js';

// Trạng thái hiện tại
let currentKey = "day05";
const API_URL = 'http://127.0.0.1:5000/summarize'; // Backend đang chạy local

// Hàm chuyển slide (Copy từ Mock)
function selectLesson(key, element, fileName) {
    currentKey = key;
    const data = MOCK_DATA[key];

    document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));
    element.classList.add('active');

    document.getElementById('docTitleDisplay').innerText = `${fileName} (Trang 1 / 44)`;
    document.getElementById('docBodyContent').innerHTML = data.content;
    appendMessage(`<i>Đã chuyển ngữ cảnh sang tài liệu: <b>${fileName}</b></i>`, 'system');
}
// Gán hàm ra global để HTML onclick gọi được
window.selectLesson = selectLesson;

// Hàm gọi API Tóm tắt Slide THẬT
async function handleSummarize() {
    // Tìm thông tin file PDF tương ứng với currentKey (day05, day04...)
    const currentFile = SLIDE_FILES.find(f => f.id === currentKey);
    if (!currentFile) {
        appendMessage("Không tìm thấy file PDF cho slide này để tóm tắt.", 'ai');
        return;
    }

    appendMessage(`Tóm tắt nội dung ${currentFile.label} cho tôi.`, 'user');
    
    // Thêm tin nhắn loading
    const loadingMsg = document.createElement('div');
    loadingMsg.className = 'msg ai';
    loadingMsg.textContent = '⏳ Đang đọc slide và tóm tắt...';
    document.getElementById('chatHistory').appendChild(loadingMsg);

    try {
        // Gọi API Backend (Flask)
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pdf_path: currentFile.path, // Gửi đường dẫn file PDF tương đối
                day_info: currentFile.label
            })
        });

        // Xóa dòng loading
        loadingMsg.remove();

        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                appendMessage(data.summary.replace(/\n/g, '<br>'), 'ai');
            } else {
                appendMessage(`❌ Lỗi từ AI: ${data.error}`, 'ai');
            }
        } else {
            appendMessage(`❌ Lỗi kết nối Backend. Hãy chắc chắn đã chạy 'python main.py' ở terminal.`, 'ai');
        }
    } catch (error) {
        loadingMsg.remove();
        appendMessage(`🚨 Lỗi mạng: ${error.message}`, 'ai');
    }
}
// Gán ra global
window.handleSummarize = handleSummarize;

// Hàm xử lý nút Link Old (Giữ lại Mock để minh họa kịch bản)
function handleLinkOld() {
    appendMessage(`Tài liệu này có liên quan gì đến các bài trước không?`, 'user');
    setTimeout(() => {
        appendMessage(`[Mock]: Day04 là bài học nền tảng kỹ thuật đầu tiên trong chuỗi.`, 'ai');
    }, 400);
}
window.handleLinkOld = handleLinkOld;

// Hàm chat tự do
function sendMessage() {
    const input = document.getElementById('userInput');
    const text = input.value.trim();
    if (!text) return;

    appendMessage(text, 'user');
    input.value = '';

    setTimeout(() => {
        appendMessage(`[Mock]: Tôi đang xem tài liệu Day hiện tại. Hãy bấm "⚡ Tóm tắt" để thấy AI thật hoạt động.`, 'ai');
    }, 500);
}
window.sendMessage = sendMessage;

// Hàm thêm tin nhắn vào khung chat
function appendMessage(text, sender) {
    const history = document.getElementById('chatHistory');
    const msgDiv = document.createElement('div');
    msgDiv.className = `msg ${sender}`;
    msgDiv.innerHTML = text;
    history.appendChild(msgDiv);
    history.scrollTop = history.scrollHeight;
}