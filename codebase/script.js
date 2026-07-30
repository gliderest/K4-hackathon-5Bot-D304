// Lấy các element
const btnSummarize = document.getElementById('btnSummarize');
const chatBody = document.getElementById('chatBody');

// URL Backend Flask đang chạy local
const API_URL = 'http://127.0.0.1:5000/summarize';

// Hàm thêm tin nhắn vào khung chat
function addMessage(text, isUser = false, isSummary = false) {
    const msgDiv = document.createElement('div');
    if (isSummary) {
        msgDiv.className = 'message summary-response';
        // Chuyển đổi xuống dòng \n thành thẻ <br> để hiển thị đẹp
        msgDiv.innerHTML = text.replace(/\n/g, '<br>');
    } else if (isUser) {
        msgDiv.className = 'message user-message';
        msgDiv.textContent = text;
    } else {
        msgDiv.className = 'message bot-message';
        msgDiv.textContent = text;
    }
    chatBody.appendChild(msgDiv);
    // Tự động cuộn xuống dưới cùng
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Hàm xử lý khi bấm nút Tóm tắt
async function handleSummarize() {
    // 1. Vô hiệu hóa nút để tránh spam
    btnSummarize.disabled = true;
    btnSummarize.textContent = '⏳ Đang tóm tắt...';

    // 2. Thêm tin nhắn user và trạng thái loading vào chat
    addMessage('Tôi cần tóm tắt nội dung slide này.', true);
    const loadingMsg = document.createElement('div');
    loadingMsg.className = 'message bot-message loading-dots';
    loadingMsg.textContent = 'Đang đọc slide và tóm tắt... ⏳';
    chatBody.appendChild(loadingMsg);

    try {
        // 3. Gọi API Backend
        // Lưu ý: "test_slide.pdf" phải nằm cùng thư mục với main.py bên backend
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pdf_path: 'test_slide.pdf',
                day_info: 'Day 5 - AI Product Thinking'
            })
        });

        // 4. Xóa dòng loading
        chatBody.removeChild(loadingMsg);

        // 5. Xử lý kết quả
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                addMessage(data.summary, false, true); // Hiển thị bản tóm tắt
            } else {
                addMessage(`❌ Có lỗi xảy ra: ${data.error}`);
            }
        } else {
            const errorData = await response.json();
            addMessage(`❌ Lỗi hệ thống: ${errorData.error || 'Không thể kết nối Backend'}`);
        }

    } catch (error) {
        // Xóa dòng loading nếu bị lỗi mạng
        if (chatBody.contains(loadingMsg)) chatBody.removeChild(loadingMsg);
        addMessage(`🚨 Lỗi mạng: Không thể gọi API. Hãy chắc chắn Backend đang chạy ở port 5000. Chi tiết: ${error.message}`);
    } finally {
        // 6. Kích hoạt lại nút
        btnSummarize.disabled = false;
        btnSummarize.textContent = '🤖 Tóm tắt Slide';
    }
}

// Gán sự kiện click cho nút
btnSummarize.addEventListener('click', handleSummarize);