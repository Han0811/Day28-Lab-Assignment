# Lab #28 — Full Platform Integration Sprint
**AICB-P2T2 · Ngày 28 · Chương 6: Tổng Hợp**

AI Platform với kiến trúc Hybrid (Local Orchestration + Kaggle GPU Server) tích hợp Prefect, Kafka, Qdrant, Prometheus, Grafana, Feast Redis và Delta Lake.

---

## 📁 Cấu Trúc Thư Mục Dự Án (Repository Structure)

Thư mục dự án đã được sắp xếp chuẩn chỉnh theo đúng yêu cầu nộp bài:
* `lab28/` — Chứa toàn bộ mã nguồn của nền tảng (Docker, Flows, API Gateway, Scripts).
* `screenshots/` — Chứa các ảnh demo giao diện quản lý.
* `smoke_tests_results.png` — Ảnh chụp màn hình kết quả chạy bộ Smoke Tests thành công.
* `production_readiness.png` — Ảnh chụp màn hình kết quả đánh giá chất lượng Production Readiness đạt 100%.

---

## 🚀 Hướng Dẫn Setup & Chạy Hệ Thống

### 1. Khởi Động Nền Tảng (Start Platform)
Di chuyển vào thư mục `lab28` và khởi chạy các dịch vụ Docker:
```bash
cd lab28
docker compose up -d
docker compose ps
```

### 2. Triển Khai Prefect Flow (Deploy Prefect Flows)
Tải các thư viện Python cần thiết và chạy Prefect flow tiêu thụ dữ liệu từ Kafka ghi vào Delta Lake:
```bash
# Di chuyển vào thư mục flows của Prefect
cd prefect/flows

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# Khởi chạy flow tiêu thụ Kafka ghi vào Delta Lake
python kafka_to_delta.py
```

### 3. Chạy Kiểm Thử Khói (Run Smoke Tests)
Bộ kiểm thử tự động xác minh toàn bộ luồng tích hợp hệ thống. Để khởi chạy kiểm thử:
```bash
# Di chuyển về thư mục gốc lab28
cd lab28

# Khởi chạy kiểm thử khói
pytest smoke-tests/ -v
```
*(Kỳ vọng: 8/8 tests PASSED tuyệt đối).*

---

## 📊 Đường Dẫn Truy Cập Dashboard (Access Dashboards)

Sau khi khởi động thành công Docker Compose, bạn có thể truy cập các trang quản lý và giám sát tại các cổng sau:

* **Grafana Dashboard:** [http://localhost:3000](http://localhost:3000) (Giám sát chỉ số API Gateway & Kafka realtime, tài khoản: `admin` / `admin`).
* **Prometheus:** [http://localhost:9090](http://localhost:9090) (Nguồn thu thập metrics của hệ thống).
* **Prefect Server UI:** [http://127.0.0.1:4200](http://127.0.0.1:4200) (Theo dõi trạng thái các Flow và lịch trình dữ liệu).
* **Qdrant Dashboard:** [http://localhost:6333/dashboard](http://localhost:6333/dashboard) (Quản lý và xem các vector nhúng được lưu trữ).
* **API Gateway docs:** [http://localhost:8080/docs](http://localhost:8080/docs) (Tài liệu Swagger UI tương tác với API).

---

## 🛠️ Các Lỗi Hệ Thống Đã Được Sửa (Bug Fixes)
1. **Lỗi Prefect Orion không thể chạy:** Đã cập nhật lệnh khởi động từ `prefect orion start` cũ thành `prefect server start` chuẩn theo phiên bản Prefect `2.14.0`.
2. **Lỗi kết nối Kafka của Prefect:** Cấu hình thành công **Dual-Listener** cổng kép cho Kafka (`localhost:9092` cho host và `kafka:29092` cho Docker nội bộ).
3. **Lỗi lệch kích thước Vector:** API Gateway tự động đệm/cắt vector về đúng `384` chiều trước khi gửi tới Qdrant.
4. **Lỗi vLLM Offline:** Implement cơ chế **Graceful Fallback** tự động lấy Context từ Qdrant và sinh phản hồi có ích kể cả khi máy chủ vLLM trên Kaggle bị sập.
