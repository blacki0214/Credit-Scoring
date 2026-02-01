import joblib
import numpy as np
import pandas as pd

# --- Load model and scaler ---
model = joblib.load("../output/models/logistic_model.pkl")
scaler = joblib.load("../output/models/scaler.pkl")

print("💳 Credit Scoring CLI — Logistic Regression Baseline Model")
print("----------------------------------------------------------")
print("Nhập các thông tin khách hàng theo hướng dẫn dưới đây:")
print("(Bấm Enter để sử dụng giá trị mặc định trong ngoặc)\n")

# --- Tooltip hướng dẫn người dùng nhập dữ liệu ---
def get_input(prompt, default):
    """Hàm nhận input từ user và chuyển sang float, có giá trị mặc định."""
    val = input(f"{prompt} [{default}]: ").strip()
    return float(val) if val != "" else float(default)

# --- Nhập dữ liệu từ user ---
dpd_mean = get_input("Trung bình số ngày trễ hạn (dpd_mean)", 2.0)
dpd_max = get_input("Số ngày trễ hạn tối đa (dpd_max)", 10.0)
on_time_ratio = get_input("Tỷ lệ trả đúng hạn (on_time_ratio, từ 0–1)", 0.8)
num_payments = get_input("Số kỳ thanh toán đã ghi nhận (num_payments)", 12)
AMT_CREDIT_SUM = get_input("Tổng hạn mức tín dụng (AMT_CREDIT_SUM)", 150000)
AMT_CREDIT_SUM_DEBT = get_input("Tổng dư nợ hiện tại (AMT_CREDIT_SUM_DEBT)", 40000)
CREDIT_ACTIVE_FLAG = get_input("Số khoản vay đang hoạt động (CREDIT_ACTIVE_FLAG)", 2)
total_utilization = get_input("Tỷ lệ sử dụng tín dụng (total_utilization)", 0.25)
credit_card_utilization = get_input("Tỷ lệ sử dụng thẻ tín dụng (credit_card_utilization)", 0.3)
oldest_account_m = get_input("Số tháng kể từ tài khoản lâu nhất (oldest_account_m)", 48)
newest_account_m = get_input("Số tháng kể từ tài khoản mới nhất (newest_account_m)", 12)
aaoa_m = get_input("Tuổi trung bình tài khoản (aaoa_m)", 30)
thin_file_flag = get_input("Khách hàng không có lịch sử tín dụng? (1 = Có, 0 = Không)", 0)

# --- Tạo DataFrame từ input ---
data = pd.DataFrame([{
    "dpd_mean": dpd_mean,
    "dpd_max": dpd_max,
    "on_time_ratio": on_time_ratio,
    "num_payments": num_payments,
    "AMT_CREDIT_SUM": AMT_CREDIT_SUM,
    "AMT_CREDIT_SUM_DEBT": AMT_CREDIT_SUM_DEBT,
    "CREDIT_ACTIVE_FLAG": CREDIT_ACTIVE_FLAG,
    "total_utilization": total_utilization,
    "credit_card_utilization": credit_card_utilization,
    "oldest_account_m": oldest_account_m,
    "newest_account_m": newest_account_m,
    "aaoa_m": aaoa_m,
    "thin_file_flag": thin_file_flag
}])

# --- Chuẩn hóa dữ liệu ---
X_scaled = scaler.transform(data)

# --- Dự đoán xác suất vỡ nợ ---
prob_default = model.predict_proba(X_scaled)[0, 1]
prediction = "❌ Rủi ro cao (Có thể vỡ nợ)" if prob_default > 0.5 else "✅ Rủi ro thấp (Khách hàng tốt)"

# --- In kết quả ---
print("\n----------------------------------------------------------")
print("🔍 Kết quả đánh giá mô hình:")
print(f"→ Xác suất vỡ nợ: {prob_default:.2%}")
print(f"→ Kết luận: {prediction}")
print("----------------------------------------------------------")
