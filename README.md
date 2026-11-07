# CỜ CARO · ĐẤU AI & HAI NGƯỜI

Game Python + Streamlit dành cho học sinh lớp 8: bàn cờ tùy chọn từ **5 × 5 đến 20 × 20** (mặc định 10 × 10), chế độ **Đấu AI** và **Hai người (1 vs 1)**, giao diện tiếng Việt và ba mức AI chạy nội bộ. Không cần tài khoản để chơi, cơ sở dữ liệu, khóa API hay dịch vụ AI trả phí.

## 1. Cài và chạy trên Windows

1. Cài **Python 3.12 trở lên** từ [python.org](https://www.python.org/downloads/). Khi cài trên Windows, chọn **Add Python to PATH**.
2. Mở thư mục dự án bằng VS Code, chọn **Terminal → New Terminal** (PowerShell).
3. Tạo môi trường riêng và cài thư viện:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

4. Chạy game:

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```

5. Mở **http://localhost:8501** trong trình duyệt. Giữ terminal đang chạy; nhấn **Ctrl+C** để dừng.

Nếu đã kích hoạt môi trường bằng `.\.venv\Scripts\Activate.ps1`, có thể dùng lệnh ngắn:

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Nếu PowerShell chặn Activate.ps1, dùng thẳng đường dẫn Python ở bước 3–4; không cần thay đổi chính sách máy. Trên macOS/Linux, thay `.venv\Scripts\python.exe` bằng `.venv/bin/python`.

## 2. Cách chơi

- Chọn **Chế độ cho trận mới** rồi bấm **Trận mới** để áp dụng.
- **Đấu AI**: bạn cầm X, luôn đi trước. Bấm ô trống; máy tự đặt O.
- **Hai người (1 vs 1)**: hai bạn chơi trên **cùng một thiết bị, cùng trang game**. Người chơi 1 cầm X đi trước, người chơi 2 cầm O; thay phiên bấm ô trống. Máy không tự đánh trong chế độ này. Đây là chế độ chơi tại chỗ; hai thiết bị mở hai phiên riêng chưa thể chơi chung một ván qua mạng.
- Có **ít nhất 5 quân liên tiếp** theo hàng ngang, dọc, chéo xuống hoặc chéo lên là thắng. Chuỗi dài hơn 5 và chuỗi bị chặn hai đầu đều thắng, không có luật cấm.
- Chuỗi thắng được tô xanh lá; nước vừa đánh có viền cam. Khi hết ô và chưa ai thắng thì hòa.
- Ô đã có quân, lúc máy đang nghĩ và khi ván kết thúc đều bị khóa.
- Chọn **Kích thước bàn cờ cho trận mới**: mọi kích thước vuông từ 5 × 5 đến 20 × 20. Luật thắng luôn là ít nhất 5 quân liên tiếp.
- **Chơi lại**: xóa bàn cờ, giữ chế độ, kích thước và độ khó của ván hiện tại.
- **Trận mới**: xóa bàn cờ, áp dụng chế độ, kích thước và độ khó đã chọn. Đổi lựa chọn trong lúc chơi không làm thay đổi ván đang chơi. Độ khó chỉ dùng khi đấu AI.
- Bảng điểm được lưu riêng theo chế độ: thắng/thua/hòa khi đấu AI và X thắng/O thắng/hòa khi chơi hai người. Điểm giữ trong phiên Streamlit; ván bỏ dở không tính vào điểm. Tải lại trang, ngắt phiên hoặc máy chủ khởi động lại có thể mất điểm. Không lưu thông tin người chơi.
- Trên máy tính, bàn cờ tận dụng chiều rộng màn hình, bảng điều khiển bên phải rộng 320 px. Trên màn hình nhỏ, bảng điều khiển chuyển xuống dưới; bàn cờ giữ ô đủ lớn để bấm và cho phép vuốt ngang nếu cần.

## 3. Giải thích AI để trình bày với thầy

| Mức | Thuật toán |
| --- | --- |
| Dễ | Chọn ngẫu nhiên một ô trống kề quân đã đánh; nếu bàn trống thì chọn gần trung tâm. |
| Vừa | Tìm nước thắng ngay; nếu không có, chặn đối thủ thắng ngay; sau đó so điểm tấn công và phòng thủ dựa trên độ dài chuỗi và số đầu mở. |
| Khó | Cũng ưu tiên thắng/chặn ngay; dùng minimax và cắt tỉa alpha-beta ở độ sâu 2–3 lượt. Tìm sâu dần trong khoảng 0,8 giây, chỉ xét các ô gần quân và giới hạn số ứng viên. Khi hết thời gian, dùng kết quả vòng đã hoàn tất hoặc nước có điểm tốt nhất. |

Minimax giả sử cả hai bên đều chọn nước có lợi cho mình. Alpha-beta bỏ qua nhánh không thể cải thiện kết quả. Việc giới hạn ứng viên và thời gian giúp máy phản hồi nhanh, nhưng **AI Khó không được bảo đảm luôn thắng hoặc tìm nước tối ưu**. Giới hạn thời gian là mục tiêu cho bước tìm kiếm; tổng thời gian hiển thị còn tùy máy và Streamlit.

## 4. Cấu trúc mã nguồn

```text
app.py                     Giao diện, callback, session_state và bảng điểm
game_logic.py              Bàn cờ, kiểm tra nước đi, thắng/hòa, lớp Game
ai_engine.py               AI Dễ/Vừa/Khó, minimax và alpha-beta
requirements.txt           Streamlit đã ghim phiên bản
.streamlit/config.toml     Màu giao diện, tắt thống kê sử dụng
tests/test_game_logic.py   Luật chơi, các hướng và mép bàn, bàn hòa
tests/test_ai_engine.py    Thắng/chặn, thời gian tìm kiếm, ván chơi hoàn chỉnh
tests/test_app.py          Luồng Streamlit, rerun, khóa bàn, bảng điểm, chơi lại
```

`st.session_state.game` lưu bàn cờ dạng list hai chiều (rỗng/X/O), chế độ, lượt, độ khó đang chơi, lịch sử và kết quả. `stats` giữ bảng điểm đấu AI, `pvp_stats` giữ bảng điểm hai người. Mỗi nút chứa mã ván và số nước; callback bỏ qua sự kiện từ lượt cũ. Khi đấu AI, sau nước X, script xử lý O đúng một lần khi đến lượt máy rồi rerun để cập nhật bàn cờ. Trong chế độ hai người, mỗi lần bấm hợp lệ chỉ đặt một quân theo lượt hiện tại. Kết quả mỗi ván chỉ được cộng một lần.

## 5. Chạy kiểm thử

Không cần cài pytest: các bài kiểm thử dùng `unittest` có sẵn và `AppTest` của Streamlit.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Các kiểm thử bao gồm mọi vị trí chuỗi 5 hợp lệ theo bốn hướng, hai loại quân, chuỗi dài hơn 5, luật chặn hai đầu, nước sai, bàn hòa, AI thắng/chặn, trả lại bàn cờ sau khi hết giờ và rerun không sinh thêm lượt/điểm.

Trước khi nộp, tự chơi thử ván thắng, thua và một ván kéo dài; thử nút Chơi lại/Trận mới và kiểm tra vuốt bàn trên điện thoại thật.

Đã kiểm tra trên Python 3.14 + Streamlit 1.66.0: 32 bài kiểm thử tự động đạt, gồm đổi kích thước, chơi ở ô cuối bàn 20 × 20, lượt X/O khi chơi hai người, thắng của cả hai bên, hòa và bảng điểm riêng theo chế độ; máy chủ trả HTTP 200; Chromium chạy được lượt X/O ở khung nhìn 1280 px và khung nhìn điện thoại 390 px, cuộn ngang bàn cờ không làm tràn chiều rộng trang. Khung nhìn điện thoại mô phỏng chưa thay thế thử nghiệm trên thiết bị thật.

## 6. Đưa mã nguồn lên GitHub

Repository hiện dùng cho dự án: [giabaothcslongthanh810/gamecocaro](https://github.com/giabaothcslongthanh810/gamecocaro).

Trong terminal ở thư mục dự án:

```powershell
git status
git add app.py game_logic.py ai_engine.py requirements.txt README.md .gitignore .streamlit/config.toml tests
git commit -m "Build Vietnamese Gomoku game with three AI levels"
git push -u origin HEAD
```

Nếu Git yêu cầu danh tính, cấu hình tên/email của em rồi commit lại. Nếu GitHub yêu cầu đăng nhập, hoàn tất qua trình duyệt hoặc Git Credential Manager; không ghi mật khẩu/token vào mã nguồn. `.gitignore` đã loại môi trường ảo, bộ nhớ đệm, `.env` và secrets.

Nếu tạo bản sao ở thư mục khác chưa có Git: tạo repository trống trên GitHub, chạy `git init`, thêm các file như trên, commit, rồi `git remote add origin <URL repository của em>` và `git push -u origin HEAD`. Không thêm remote lần nữa nếu `origin` đã tồn tại.

## 7. Triển khai để lấy link nộp bài

1. Đẩy các file đã kiểm thử lên GitHub theo mục 6.
2. Mở [Streamlit Community Cloud](https://share.streamlit.io/), đăng nhập và kết nối GitHub.
3. Chọn **Create app** → **Yup, I have an app** nếu được hỏi.
4. Chọn repository `giabaothcslongthanh810/gamecocaro`, đúng branch vừa push, và **Main file path: `app.py`** (ở gốc repository).
5. Trong **Advanced settings**, chọn Python **3.12 trở lên** phù hợp `requirements.txt`. Ứng dụng không cần khai báo secrets.
6. Chọn **Deploy**, đợi cài thư viện và mở game. Nếu lỗi, xem log để kiểm tra branch, đường dẫn file hoặc cài thư viện.
7. Sao chép URL thực tế kết thúc bằng **`.streamlit.app`**. Mở thử trong cửa sổ ẩn danh để bảo đảm thầy có thể chơi mà không đăng nhập.

**Link thật chỉ được cấp sau khi deploy thành công**; dự án này chuẩn bị mã nguồn và hướng dẫn, chưa tự tạo đường link công khai. Ứng dụng có thể ngủ khi ít dùng và cần thời gian khởi động lại.

Tham khảo [hướng dẫn triển khai chính thức của Streamlit](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [callback của nút](https://docs.streamlit.io/develop/concepts/design/buttons) và [AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest).
