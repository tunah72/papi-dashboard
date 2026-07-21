import { Link, useLocation } from 'react-router-dom'

const STREAMLIT_URL = 'http://127.0.0.1:8501'

export function AiAssistantPending() {
  const location = useLocation()
  const overviewHref = `/overview${location.search}`

  return <article className="ai-boundary">
    <div className="title-row">
      <div>
        <p className="eyebrow">Trợ lý AI · đang chuyển đổi</p>
        <h1>Quyền chạy code vẫn thuộc về bạn</h1>
        <p className="lede">Route React này chưa kết nối API AI, API Thực thi hoặc API Logs. Vì vậy, mở trang không sinh code và không chạy bất kỳ phân tích nào.</p>
      </div>
      <p className="status">Không có thực thi ngầm</p>
    </div>

    <section className="ai-boundary-panel" aria-labelledby="approval-flow-title">
      <div>
        <p className="eyebrow">Luồng hiện hành ở fallback</p>
        <h2 id="approval-flow-title">Bốn bước human-in-the-loop</h2>
        <p>Streamlit tiếp tục là bề mặt AI dùng cho demo cho đến khi React đạt đủ parity. Mọi mã đề xuất phải hiện rõ trước khi có thể chạy local.</p>
      </div>
      <ol>
        <li><span>01</span><strong>Đặt yêu cầu</strong><small>Bạn chọn kỹ thuật hoặc tự viết câu hỏi phân tích.</small></li>
        <li><span>02</span><strong>Xem code và giải thích</strong><small>AI chỉ đề xuất; code ở trạng thái chờ duyệt.</small></li>
        <li><span>03</span><strong>Sửa và quyết định</strong><small>Bạn kiểm tra, sửa tham số rồi chủ động phê duyệt.</small></li>
        <li><span>04</span><strong>Chạy local và lưu log</strong><small>Chỉ bản code đã phê duyệt mới được thực thi và ghi kết quả.</small></li>
      </ol>
    </section>

    <section className="ai-boundary-actions" aria-label="Lựa chọn tiếp theo">
      <div>
        <p className="eyebrow">Dùng AI trong bản demo hiện tại</p>
        <h2>Khởi động Streamlit fallback</h2>
        <p>Chạy <code>python3 -m streamlit run app/main.py</code>, sau đó mở mục <strong>AI Assistant</strong>. Không nhập secret vào giao diện hoặc log.</p>
      </div>
      <div className="action-row">
        <a className="cta" href={STREAMLIT_URL}>Mở fallback local <span aria-hidden="true">↗</span></a>
        <Link className="secondary-link" to={overviewHref}>Quay lại Tổng quan</Link>
      </div>
    </section>
  </article>
}
