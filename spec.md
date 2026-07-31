# AI SPEC — VLearn Cross-Lesson AI Tutor · Nhóm 5Bot-D304 · Zone K4

**Hướng:** B — Trợ lý Học viên
**Loại:** Tính năng mới / prototype working

## §1. User & Job

### User

Học viên VLearn cần học xuyên nhiều lesson, thường phải chuyển qua lại giữa slide, transcript và tài liệu cá nhân để tìm câu trả lời, kiểm tra nguồn và nhớ phần cần ôn lại.

### Core JTBD

Khi đang học một lesson và gặp câu hỏi, học viên muốn nhận được lời giải thích ngắn, có căn cứ và mở được đúng vị trí trong tài liệu để tự kiểm tra, từ đó tiếp tục học mà không mất thời gian tìm kiếm thủ công.

### Problem statement

Học viên mất thời gian tìm thông tin trong nhiều slide/transcript, khó biết câu trả lời có căn cứ ở đâu và dễ bỏ quên những phần cần ôn lại. Khi hệ thống không có nguồn phù hợp, việc trả lời chắc chắn sẽ làm giảm niềm tin của học viên.

### Evidence hiện có trong repository

| Evidence | Kết quả | Nguồn |
|---|---:|---|
| Backend unit tests | 8/8 pass | `codebase/backend/tests/` |
| QA unit tests | 10/10 pass | `qa/tests/` |
| Golden set validation | 31 cases hợp lệ | `qa/scripts/validate_golden_set.py` |
| Official evaluation trước đó | 21/21 pass, 0 critical fail | `qa/eval/reports/run-456be9f22a51_summary.md` |
| Frontend production build | Pass | `codebase/frontend/` — `npm run build` |
| Local HTTP health endpoint | 200 OK | `GET /api/health` |
| Local course outline API | 200 OK với `learner_id` | `GET /api/courses/vlearn-hackathon/outline?learner_id=demo-learner` |
| Local lesson detail API | 200 OK | `GET /api/courses/vlearn-hackathon/lessons/lesson-05` |
| Feedback sơ bộ | 3/3 người đánh giá core ổn; cần xem lại UI/UX | Feedback nhóm: T012 Nguyễn Trọng Toàn, T012 Sái Hồng Anh, T015 Nguyễn Hoàng Anh |

### Evidence cần bổ sung trước khi nộp

Feedback UI/UX của 3 người phải được ghi lại trong `qa/validation/observation_sheet.md` và `qa/validation/feedback_log.md`, kèm consent, task, hành vi quan sát được và quote nguyên văn. Không suy diễn thành số liệu nếu chưa có log.

## §2. Impact & quyết định chọn

| Ứng viên | Số người bị ảnh hưởng | Tần suất | Chi phí mỗi lần | Khả thi prototype | Quyết định |
|---|---:|---|---|---|---|
| Chat hỏi đáp có citation xuyên lesson | Cao | Nhiều lần mỗi buổi học | Cao: phải tìm thủ công | Cao: RAG local + agent | **Chọn** |
| Theo dõi tiến độ và gợi ý ôn tập | Cao | Mỗi buổi học | Trung bình: dễ quên phần yếu | Cao: SQLite local | Giữ trong prototype |
| Upload tài liệu cá nhân để hỏi | Trung bình | Khi có tài liệu ngoài khóa | Cao: phải đọc/tìm thủ công | Trung bình-cao | Giữ như capability bổ trợ |
| Dashboard phân tích học tập nâng cao | Chưa đủ evidence | Hàng tuần | Trung bình | Thấp trong thời gian prototype | Loại |
| Tự động chấm bài/cho điểm | Chưa đủ evidence | Theo bài kiểm tra | Rất cao nếu sai | Thấp và rủi ro cao | Loại |

### Ứng viên được chọn

Chọn **trợ lý hỏi đáp có citation và điều hướng nguồn** làm lát cắt trung tâm vì nó giải quyết trực tiếp điểm đau tìm kiếm học liệu, có thể kiểm chứng bằng Golden Set và tạo khác biệt rõ trong demo. Progress memory và upload là hai capability hỗ trợ, không được làm loãng core flow.

### Ứng viên đã loại

- Dashboard analytics: chưa có evidence nhu cầu đủ mạnh và không giúp giải quyết ngay câu hỏi trong lúc học.
- Tự động chấm điểm: cost-of-error cao, vượt non-goal của tutor và cần dữ liệu/authority mà prototype chưa có.
- Chat tự do không citation: rủi ro hallucination và không đáp ứng yêu cầu tin cậy.

## §3. Giải pháp tương tự đã nghiên cứu

### ChatGPT / chatbot tổng quát

- **Flow đáng học:** hỏi đáp hội thoại, clarification và gợi ý tiếp theo.
- **Đáng né:** trả lời ngoài nguồn nếu không khóa context; citation không luôn gắn với vị trí người dùng có thể kiểm tra.
- **Mình khác:** chỉ dùng context học liệu được truy xuất, citation do backend kiểm soát và click citation mở đúng slide/transcript.

### NotebookLM / công cụ hỏi đáp theo tài liệu

- **Flow đáng học:** trả lời dựa trên tài liệu người dùng cung cấp và hiển thị nguồn.
- **Đáng né:** trải nghiệm tìm nguồn có thể tách khỏi màn hình học chính.
- **Mình khác:** kết hợp course-wide search, tài liệu upload, lesson viewer ba vùng và long-term learning memory.

### VLearn tutor prototype hiện có

- **Flow đáng học:** tích hợp mục lục, viewer và chat trong cùng một màn hình.
- **Điểm cần cải thiện:** feedback sơ bộ từ 3 thành viên cho thấy core đã ổn nhưng UI và trải nghiệm cần rà soát lại trước demo cuối.

## §4. Thiết kế

### Lát cắt một câu

Một học viên đang học một lesson đặt một câu hỏi; AI truy xuất đúng context và trả lời kèm citation có thể mở tới nguồn; học viên kiểm tra nguồn và tiếp tục học.

### Core flow

1. Học viên chọn Day/Lesson ở vùng trái.
2. Viewer giữa hiển thị slide hoặc transcript hiện tại.
3. Học viên hỏi tutor ở vùng phải.
4. Backend chọn tool phù hợp: phân tích tài liệu đang mở hoặc tìm kiếm toàn khóa.
5. Tutor trả lời từ context, trả confidence và citation.
6. Học viên click citation để viewer mở đúng trang/đoạn.
7. Progress/memory lưu trạng thái học tập phục vụ gợi ý tiếp theo.

### Chat answer card interaction

Mỗi lượt hỏi–đáp được render thành một card riêng trong chat. Answer card hiển thị trạng thái đang tạo, mức confidence, citation có thể click, tool trace có thể mở rộng, suggested next action, nút sao chép và nút thử lại khi AI/provider lỗi. Suggested action không tự gửi request; nó điền câu hỏi vào composer để học viên kiểm soát trước khi gửi.

### Upload history interaction

Sidebar không còn hiển thị Memory hoặc khu vực upload tài liệu thêm. File cá nhân chỉ được thêm bằng nút upload trong chat; sau khi upload thành công, file được ghi vào lịch sử upload local của learner và xuất hiện ở sidebar để mở lại. Sidebar chỉ hiển thị Script, Slide và lịch sử các file đã upload qua chat.

### Non-goals

1. Không tự động chấm điểm hoặc quyết định điểm cuối kỳ.
2. Không làm hộ bài kiểm tra/đánh giá.
3. Không thay thế giảng viên hoặc tư vấn y tế/pháp lý/tài chính.
4. Không xây authentication/cloud production trong prototype.
5. Không coi memory người học là bằng chứng kiến thức.

### Mức prototype

**Working prototype.**

| Thành phần | Trạng thái |
|---|---|
| Backend API FastAPI | Thật, chạy local |
| Retrieval slide/transcript | Thật theo local data/index |
| AI answer generation | Có thể chạy provider thật qua OpenRouter |
| Citation contract | Thật, backend kiểm soát |
| Citation navigation | Thật trong frontend |
| Progress memory | Thật với SQLite local |
| Authentication/cloud storage | Mock/local, không nằm trong scope |
| User validation | Cần hoàn thiện log evidence trước khi nộp |

### Automation

Chọn **augment + conditional**:

- **Augment:** AI giải thích và định vị nguồn, nhưng người học vẫn kiểm tra citation.
- **Conditional:** chỉ trả lời chắc chắn khi retrieval có căn cứ; confidence thấp hoặc thiếu nguồn thì hỏi lại/từ chối.
- Không automate quyết định điểm, đánh giá cuối kỳ hoặc hành động có cost-of-error cao.

### §4b. Nguyên tắc đã áp dụng

| Nguyên tắc | Áp dụng trong prototype |
|---|---|
| Make uncertainty visible | Trả confidence; khi thiếu nguồn nói rõ giới hạn và hỏi lại |
| Keep human in control | Citation mở nguồn để học viên tự kiểm chứng |
| Grounding before generation | Retrieval context đi trước AI answer; citation do backend bảo toàn |
| Separate source types | Phân biệt course source với learner-upload document |
| Minimize memory | Chỉ lưu progress, chủ đề yếu và gợi ý ôn, không mặc định lưu toàn bộ chat |
| Graceful failure | API/AI lỗi không bịa câu trả lời, trả thông báo giới hạn |
| Consistent mental model | Ba vùng trái–giữa–phải giữ mục lục, học liệu và chat trong cùng state lesson |
| Clear scope boundaries | Từ chối bài kiểm tra, điểm số và câu hỏi ngoài phạm vi tutor |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản

| Lớp | Kịch bản | Hành vi mong đợi |
|---|---|---|
| 1. Không có căn cứ | Hỏi “Trang 99 nói gì?” | Không bịa, thông báo không tìm thấy nguồn |
| 1. Không có căn cứ | Hỏi về file không tồn tại | Nói rõ không có tài liệu phù hợp |
| 2. Thiếu context | “Tóm tắt cái này” khi chưa chọn tài liệu | Hỏi học viên chọn/mở tài liệu |
| 2. Thiếu context | “Giải thích thêm” không có chủ đề | Hỏi lại chủ đề hoặc lesson |
| 3. Ngoài phạm vi | “Làm hộ bài kiểm tra” | Từ chối, chuyển sang hỗ trợ học |
| 3. Ngoài phạm vi | “Cho tôi điểm cuối kỳ” | Từ chối và hướng tới kênh chính thức |
| 3. Ngoài phạm vi | Tư vấn y tế | Từ chối lịch sự, không đưa chẩn đoán |
| 4. Sai domain | Đồng nhất agent với workflow | Phân biệt đúng theo học liệu |
| 4. Sai domain | Đồng nhất PRD với Risk Matrix | Giải thích khác biệt, không đơn giản hóa |
| 4. Sai domain | “AI product chỉ là chatbot?” | Sửa hiểu lầm bằng ví dụ có nguồn |
| 4. Kỹ thuật | Input rỗng/ký tự đặc biệt | Clarification, không trả lỗi 422 cho người dùng |
| 4. Kỹ thuật | AI provider lỗi | Thông báo giới hạn, không bịa câu trả lời |

## §6. Bốn đường đi của trải nghiệm

- **Happy path:** chọn lesson → hỏi câu có trong học liệu → nhận câu trả lời + citation → click citation → viewer mở đúng nguồn.
- **Low-confidence:** retrieval score thấp → hiển thị giới hạn/confidence thấp → hỏi học viên bổ sung lesson/chủ đề.
- **Failure/không căn cứ:** không có chunk phù hợp hoặc AI lỗi → không suy diễn, thông báo rõ và đưa hướng thử lại.
- **Correction:** học viên mở citation, đối chiếu nguồn, đặt câu hỏi sửa/tiếp theo; hệ thống giữ context lesson hiện tại.
- **Ngoài phạm vi:** từ chối ngắn gọn, giải thích giới hạn và chuyển hướng sang hành vi học tập an toàn.
- **Case đặc thù domain:** dùng context tương ứng, nêu khác biệt thuật ngữ và không tự hợp nhất các khái niệm gần nhau.

### Điểm cần kiểm tra UI/UX

Feedback sơ bộ của T012 Nguyễn Trọng Toàn, T012 Sái Hồng Anh và T015 Nguyễn Hoàng Anh đều cho rằng core flow ổn nhưng cần xem lại UI/UX. Trước khi nộp cần kiểm tra đặc biệt:

- Người dùng có biết phải chọn lesson/tài liệu trước khi hỏi không.
- Citation có đủ nổi bật và có affordance để click không.
- Khi clarification/low-confidence xảy ra, người dùng có hiểu cần làm gì tiếp không.
- Viewer có mở đúng vị trí mà không làm mất nội dung chat không.
- Layout ba vùng có dễ dùng trên màn hình nhỏ không.

## §7. Kiểm thử

### Chiều chất lượng

1. **Groundedness:** mọi khẳng định về khóa học phải có trong context.
2. **Citation correctness:** citation tồn tại và hỗ trợ câu trả lời.
3. **Answer correctness:** trả lời đúng khái niệm trong domain.
4. **Clarification:** hỏi lại khi thiếu tài liệu/chủ đề/context.
5. **Scope and safety:** từ chối yêu cầu ngoài phạm vi hoặc có rủi ro cao.
6. **Relevance:** câu trả lời trực tiếp, đủ dùng, không lan man.
7. **UX:** người dùng hoàn thành task và tìm được nguồn mà không cần hướng dẫn.

### Golden set

Golden set hiện có **31 case**, bao phủ happy path, source truth, ambiguous/missing context, out-of-scope, domain-specific error và edge case trong `qa/eval/golden_set.csv`.

### Quality bar đã chốt

- Overall pass rate: **≥80%**.
- Case yêu cầu citation: **100% phải có citation tồn tại**.
- Critical hallucination/citation giả: **0**.
- Không trả lời chắc chắn khi thiếu context.
- Official run phải chạy trên toàn bộ Golden Set hiện hành; report cũ 21 case chỉ là evidence lịch sử, không thay thế run 31 case.

### Kết quả đã có

| Run/evidence | Kết quả | Ghi chú |
|---|---:|---|
| Backend tests | 8/8 | Pass |
| QA tests | 10/10 | Pass |
| Golden set validator | 31 cases valid | Pass cấu trúc |
| Official HTTP run cũ | 21/21, 100% | 0 critical fail; cần chạy lại với 31 case |
| Frontend build | Pass | Vite/TypeScript |

## §8. Phân công & kế hoạch

| Người | Mã | Vai trò |
|---|---|---|
| Nguyễn Trọng Toàn | T012 | Core/product, rà soát spec và UX |
| Sái Hồng Anh | T012 | Core/product, kiểm tra trải nghiệm và validation |
| Nguyễn Hoàng Anh | T015 | Core/product, kiểm tra prototype và demo |

### Kế hoạch validation CP5/CP6

Mời 3 thành viên trên làm người review nội bộ có consent. Với mỗi người:

1. Mở một lesson và hỏi tutor để tóm tắt.
2. Hỏi “AI product khác software feature thế nào?”
3. Mở citation và tự kiểm tra nguồn.

Ghi lại: task completion, thời gian, hành động đầu tiên, hesitation, misclick, citation opened, needed help, quote nguyên văn và câu trả lời cho ba câu hỏi:

1. Điều gì khó hiểu hoặc khó chịu nhất?
2. Bạn có tin kết quả này không? Vì sao?
3. Bạn có dùng tính năng này thật không? Vì sao hoặc vì sao chưa?

### Multi-prototype

Không triển khai hai prototype độc lập. So sánh hai hướng UI trong review:

- **A:** giữ layout ba vùng cố định.
- **B:** layout ưu tiên chat, viewer mở dạng drawer/modal khi click citation.

Chọn hướng có ít hesitation hơn, citation dễ tìm hơn và task completion tốt hơn. Nếu chưa có số đo, không tuyên bố hướng nào thắng.

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| CP3 | Bổ sung Golden Set và evaluation runner | Cố định các risk class và kiểm tra regression |
| CP3 | Bổ sung citation contract và refusal/clarification behavior | Giảm hallucination và tăng khả năng kiểm chứng |
| CP4 | Bổ sung document analysis, upload và routing theo tài liệu đang mở | Hỗ trợ đúng ngữ cảnh học viên |
| CP4 | Bổ sung backend/frontend tests | Kiểm tra flow core và các edge case |
| CP5 | Ghi nhận feedback sơ bộ của 3 core members: core ổn, cần rà soát UI/UX | Chuẩn bị validation và cải thiện trải nghiệm trước demo cuối |
| CP6 | Nâng cấp chat thành các question/answer card có confidence, citation, suggested action, copy và retry | Làm rõ trạng thái sinh câu trả lời và tăng tương tác ngay trong chat |
| CP6 | Chuyển upload cá nhân vào chat, sidebar chỉ giữ lịch sử upload và bỏ Memory | Có một điểm upload duy nhất, giảm trùng lặp và làm sidebar tập trung vào học liệu |
| CP6 | Cập nhật sau user validation thật | Chỉ điền sau khi có observation, quote và quyết định thay đổi |

## Trạng thái nộp bài

- [x] Prototype working
- [x] Backend/QA tests
- [x] Golden set validator
- [x] System prompt và scope rules
- [ ] Hoàn thiện observation sheet và feedback log có evidence thật
- [ ] Chạy official evaluation lại trên 31 case
- [ ] Hoàn thiện UI/UX theo feedback
- [x] Demo pitch deck hoàn thành trên Canva
- [x] Cập nhật README và hướng dẫn chạy
- [ ] Kiểm tra secret và dọn file tạm trước khi nộp

### Pitch deck hiện có

https://slidecp1vlearn.my.canva.site/vlearn-copilot-pitch-deck

Link Canva là nguồn trình chiếu hiện tại. Cần tải bản PDF offline và thay file `demo-slides.pdf` placeholder nếu submission yêu cầu PDF trong repository.
