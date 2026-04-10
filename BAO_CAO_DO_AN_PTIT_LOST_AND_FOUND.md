# Báo cáo đồ án: PTIT Lost & Found

## 1. Thông tin tổng quan

### 1.1 Tên hệ thống
- PTIT Lost & Found

### 1.2 Mục tiêu
- Xây dựng nền tảng hỗ trợ sinh viên PTIT đăng tin mất đồ/nhặt được.
- Rút ngắn thời gian tìm lại tài sản thất lạc trong khuôn viên học viện.
- Cung cấp luồng liên hệ nhanh giữa người đăng tin và người tìm thấy/đánh mất.

### 1.3 Đối tượng sử dụng
- Sinh viên PTIT (user thường).
- Quản trị viên/điều phối (ADMIN/MOD) để kiểm duyệt nội dung.

### 1.4 Bài toán thực tế
- Tình trạng mất đồ diễn ra thường xuyên tại thư viện, nhà xe, căng tin, khu giảng đường.
- Kênh thông báo rời rạc (group chat, bài đăng cá nhân) khiến thông tin khó tổng hợp.
- Thiếu cơ chế thống nhất để đăng tin, tìm kiếm, bình luận, nhắn tin và theo dõi trạng thái xử lý.

---

## 2. Kiến trúc hệ thống

### 2.1 Thành phần chính
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: Reflex (Python)
- **Realtime**: WebSocket (thông báo/tin nhắn)
- **Lưu trữ media**: Cloudinary (ảnh bài đăng)

### 2.2 Cấu trúc thư mục mức cao
- `backend/`: API, model dữ liệu, nghiệp vụ, bảo mật, websocket.
- `Frontend/`: mã nguồn giao diện Reflex.
- `README.md`: hướng dẫn chạy nhanh.

### 2.3 Mô hình dữ liệu cốt lõi
- `users`: tài khoản người dùng, role, thông tin tạo tài khoản.
- `posts`: bài đăng mất đồ/nhặt được, danh mục, vị trí, trạng thái kiểm duyệt, trạng thái đã giải quyết.
- `comments`: bình luận theo bài đăng.
- `messages`: tin nhắn giữa các người dùng.
- `notifications`: thông báo hệ thống/liên quan tương tác.
- `reports`: báo cáo/yêu cầu gỡ bài.

---

## 3. Tổng quan chức năng

### 3.1 Nhóm chức năng tài khoản
- Đăng ký tài khoản.
- Đăng nhập/đăng xuất.
- Duy trì phiên làm việc bằng token.
- Phân quyền theo role (USER, MOD, ADMIN).

### 3.2 Nhóm chức năng bài đăng
- Tạo bài đăng mất đồ/nhặt được.
- Đính kèm ảnh cho bài đăng.
- Xem danh sách bài đăng.
- Xem chi tiết bài đăng.
- Quản lý bài đăng cá nhân (xem/xóa/đánh dấu đã giải quyết).

### 3.3 Nhóm chức năng tương tác
- Bình luận dưới bài đăng.
- Nhắn tin trực tiếp giữa người dùng.
- Nhận thông báo khi có hoạt động liên quan.

### 3.4 Nhóm chức năng tìm kiếm
- Tìm kiếm theo từ khóa.
- Lọc theo loại tin (mất đồ/nhặt được).
- Lọc theo danh mục.
- Phân trang kết quả.

### 3.5 Nhóm chức năng kiểm duyệt
- Người dùng gửi báo cáo hoặc yêu cầu gỡ bài.
- ADMIN/MOD duyệt/từ chối/gỡ bài.
- Theo dõi trạng thái kiểm duyệt: `PENDING`, `APPROVED`, `REJECTED`, `REMOVED`.

---

## 4. Chi tiết chức năng

## 4.1 Đăng ký / Đăng nhập

### Mô tả
- Cho phép người dùng tạo tài khoản và đăng nhập vào hệ thống.

### Luồng xử lý
1. Người dùng nhập email, mật khẩu, thông tin cơ bản.
2. Backend kiểm tra trùng email.
3. Mật khẩu được băm (hash) trước khi lưu DB.
4. Đăng nhập thành công trả về access token + user info.

### Ràng buộc chính
- Mật khẩu tối thiểu 8 ký tự, có chữ hoa, chữ thường và số.
- Chống brute-force mức cơ bản trên endpoint đăng nhập.

### Kết quả đầu ra
- Người dùng có session hợp lệ để truy cập các chức năng riêng tư.

---

## 4.2 Đăng bài mất đồ/nhặt được

### Mô tả
- Người dùng đăng tin gồm tiêu đề, mô tả, loại tin, danh mục, vị trí, liên hệ, ảnh.

### Luồng xử lý
1. Frontend thu thập form data.
2. Gửi multipart request lên backend.
3. Backend upload ảnh lên Cloudinary (nếu có).
4. Backend lưu bài đăng vào DB.
5. Feed cập nhật theo dữ liệu mới.

### Điểm kiểm soát
- Validate dữ liệu bắt buộc.
- Giới hạn kích thước ảnh trên frontend.
- Tích hợp trạng thái kiểm duyệt để kiểm soát hiển thị.

---

## 4.3 Quản lý tin cá nhân

### Mô tả
- Người dùng xem toàn bộ bài đã đăng, theo dõi trạng thái và thao tác nhanh.

### Dữ liệu hiển thị chính
- Loại tin, danh mục, tiêu đề, mô tả ngắn.
- Ngày tạo, vị trí, lượt xem.
- Trạng thái kiểm duyệt và trạng thái đã giải quyết.

### Hành động
- Xem chi tiết bài.
- Xóa bài.
- Đánh dấu bài đã giải quyết (owner).

---

## 4.4 Chi tiết bài đăng + bình luận

### Mô tả
- Trang chi tiết hiển thị đầy đủ nội dung bài và khối bình luận.

### Hành vi chính
- Người dùng xem ảnh, thông tin liên hệ, metadata.
- Đăng bình luận theo bài.
- Chủ bài có thể đánh dấu đã giải quyết.
- Người dùng khác có thể báo cáo bài.

---

## 4.5 Nhắn tin trực tiếp (A -> B)

### Mô tả
- Hỗ trợ trao đổi 1-1 để xác minh đồ vật và thống nhất trả lại.

### Luồng chính
1. User A mở chat với User B.
2. User A gửi tin nhắn qua API.
3. Backend lưu message vào DB.
4. User B nhận cập nhật unread và xem lịch sử chat.

### Thành phần kỹ thuật
- Endpoint gửi tin, lấy lịch sử, lấy hội thoại, đánh dấu đã đọc.
- WebSocket dùng để đẩy tín hiệu cập nhật realtime mức cơ bản.

---

## 4.6 Thông báo

### Mô tả
- Hiển thị thông báo về hoạt động liên quan bài đăng/tương tác.

### Chức năng
- Badge số lượng chưa đọc.
- Dropdown thông báo nhanh.
- Trang thông báo đầy đủ.
- Đánh dấu đã đọc từng cái hoặc toàn bộ.

---

## 4.7 Tìm kiếm và lọc bài

### Mô tả
- Cho phép tìm bài theo từ khóa và bộ lọc.

### Cơ chế hiện tại
- Backend có endpoint search tối thiểu: lọc theo keyword/type/category/location, phân trang.
- Frontend hiển thị danh sách kết quả và điều hướng trang.

### Mục tiêu hiệu quả
- Phù hợp quy mô đồ án sinh viên.
- Đủ nhanh với tập dữ liệu nhỏ-trung bình.

---

## 4.8 Kiểm duyệt nội dung (ADMIN/MOD)

### Mô tả
- Quản trị viên kiểm soát nội dung không phù hợp hoặc sai lệch.

### Nghiệp vụ
- Duyệt bài (`APPROVED`).
- Từ chối (`REJECTED`).
- Gỡ bài (`REMOVED`).
- Ghi nhận metadata người duyệt và thời điểm duyệt.

### Lợi ích
- Hạn chế spam, nội dung sai, yêu cầu gian lận.
- Tăng độ tin cậy của nền tảng.

---

## 5. Luồng hoạt động hệ thống (end-to-end)

## 5.1 Luồng người đăng mất đồ
1. Đăng nhập.
2. Tạo bài “Mất đồ” với thông tin chi tiết.
3. Bài lên feed/tìm kiếm (theo trạng thái kiểm duyệt).
4. Người khác bình luận hoặc nhắn tin trực tiếp.
5. Chủ bài xác minh và đánh dấu “đã giải quyết”.

## 5.2 Luồng người nhặt được đồ
1. Đăng nhập.
2. Tạo bài “Nhặt được”.
3. Người mất tìm thấy bài qua search/feed.
4. Hai bên nhắn tin xác minh (đặc điểm, thời gian, vị trí).
5. Bàn giao đồ và cập nhật trạng thái bài.

## 5.3 Luồng báo cáo và kiểm duyệt
1. User phát hiện nội dung bất thường.
2. Gửi báo cáo/yêu cầu gỡ.
3. ADMIN/MOD xem danh sách cần xử lý.
4. Quyết định duyệt/từ chối/gỡ.
5. Hệ thống cập nhật trạng thái hiển thị.

---

## 6. Bảo mật và độ ổn định

## 6.1 Bảo mật đã áp dụng
- Hash mật khẩu trước khi lưu.
- Token xác thực cho API cần quyền.
- Tách secret sang biến môi trường.
- Siết tiêu chuẩn mật khẩu.
- Giới hạn đăng nhập sai mức cơ bản.
- Bỏ cơ chế auto-admin từ đăng ký công khai.

## 6.2 Điểm ổn định vận hành
- Kiến trúc đơn giản, dễ debug.
- Luồng CRUD rõ ràng.
- Có health-check và chia module tương đối tách bạch.

## 6.3 Giới hạn hiện tại
- Realtime phụ thuộc kết nối WebSocket ổn định.
- SQLite phù hợp đồ án/nhóm nhỏ, chưa tối ưu cho tải lớn.
- Search mới ở mức cơ bản, chưa có ranking nâng cao.

---

## 7. Đánh giá mức độ hoàn thiện

## 7.1 Điểm mạnh
- Bao phủ đầy đủ chức năng cốt lõi của bài toán thất lạc.
- Luồng người dùng rõ ràng từ đăng tin -> liên hệ -> giải quyết.
- Có phân quyền và kiểm duyệt.
- UI đã được đồng bộ và tối ưu dần theo phản hồi thực tế.

## 7.2 Điểm cần nâng cấp nếu phát triển tiếp
- Chuẩn hóa realtime tốt hơn đa môi trường.
- Tối ưu search và phân trang sâu hơn ở backend.
- Bổ sung logging nghiệp vụ và dashboard theo dõi.
- Nâng cấp CSDL sang PostgreSQL nếu mở rộng quy mô.

---

## 8. Hướng dẫn demo nhanh cho hội đồng

1. Mở trang chủ, trình bày feed mất đồ/nhặt được.
2. Đăng nhập bằng 2 tài khoản khác nhau.
3. Tạo bài mới có ảnh.
4. Tìm bài bằng trang search + filter.
5. Mở chi tiết bài, thêm bình luận.
6. Nhắn tin giữa 2 tài khoản.
7. Thể hiện thông báo chưa đọc.
8. Vào quản lý tin, đổi trạng thái đã giải quyết.
9. Trình bày luồng admin kiểm duyệt.

---

## 9. Kết luận

PTIT Lost & Found đáp ứng tốt mục tiêu của một đồ án ứng dụng thực tế trong môi trường học viện: giúp sinh viên đăng tin, tìm kiếm, tương tác và xử lý đồ thất lạc theo quy trình rõ ràng. Hệ thống hiện đạt mức hoàn thiện tốt cho triển khai nội bộ/đồ án, đồng thời vẫn giữ được khả năng mở rộng khi cần nâng cấp ở các giai đoạn tiếp theo.
