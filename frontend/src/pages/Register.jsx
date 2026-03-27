import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  FaRegEnvelope,
  FaRegEye,
  FaRegEyeSlash,
  FaRegUser,
} from "react-icons/fa6";
import { MdLockOutline, MdCheckCircle } from "react-icons/md";
import { FcGoogle } from "react-icons/fc";

// 1. Import hàm register từ service
import { register } from "../services/authService";

const Register = () => {
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  // 2. Quản lý State form
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // 3. Xử lý thay đổi input
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (error) setError("");
  };

  // 4. Xử lý Đăng ký
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Kiểm tra mật khẩu khớp nhau (Frontend validation)
    if (formData.password !== formData.confirmPassword) {
      return setError("Mật khẩu xác nhận không khớp!");
    }

    // Kiểm tra độ dài mật khẩu (Khớp với Pydantic backend nếu có)
    if (formData.password.length < 6) {
      return setError("Mật khẩu phải có ít nhất 6 ký tự!");
    }

    setLoading(true);
    try {
      // Gửi dữ liệu (không gửi confirmPassword lên backend)
      const { confirmPassword, ...dataToSubmit } = formData;
      await register(dataToSubmit);

      alert("Đăng ký thành công! Đang chuyển hướng sang trang đăng nhập.");
      navigate("/login");
    } catch (err) {
      const errorMsg =
        err.response?.data?.detail || "Đăng ký thất bại. Vui lòng thử lại.";
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen w-full font-sans bg-white">
      {/* --- LEFT SIDE: BANNER (Giữ nguyên UI của bạn) --- */}
      <div className="relative hidden w-2/3 flex-col items-center justify-center bg-gradient-to-br from-[#38b2ac] via-[#2c7a7b] to-[#285e61] p-12 lg:flex overflow-hidden">
        {/* Animated Bubbles */}
        <div className="absolute top-[10%] left-[10%] w-32 h-12 bg-white/10 rounded-full blur-md animate-float"></div>
        <div className="absolute top-[20%] right-[15%] w-24 h-8 bg-white/10 rounded-full blur-sm animate-float-delayed"></div>
        <div className="absolute bottom-[30%] left-[15%] w-28 h-10 bg-white/10 rounded-full blur-md animate-float-slow"></div>
        {/* Content */}
        <div className="relative z-10 text-white max-w-lg">
          <h1 className="text-4xl font-bold leading-tight mb-4">
            Tìm Đồ Sinh Viên <br />
            Kết nối và tìm lại đồ thất lạc cho sinh viên
          </h1>

          <ul className="space-y-4 mt-8">
            {[
              "Đăng tin mất/nhặt được đồ miễn phí",
              "Tìm kiếm trên bản đồ dễ dàng",
              "AI thông báo tin trùng khớp",
              "Hỗ trợ nhanh chóng",
            ].map((text, idx) => (
              <li
                key={idx}
                className="flex items-center gap-3 text-white/90 font-medium"
              >
                <MdCheckCircle className="text-[#9ed3a6] text-xl" /> {text}
              </li>
            ))}
          </ul>
        </div>
        {/* Decorative Mountains */}
        <div className="absolute bottom-0 left-0 w-full z-0 pointer-events-none select-none leading-[0]">
          <svg
            className="block w-full h-[150px] md:h-[250px]"
            viewBox="0 0 1440 320"
            preserveAspectRatio="none"
          >
            <path
              fill="#ffffff"
              fillOpacity="0.15"
              d="M0,224L48,213.3C96,203,192,181,288,181.3C384,181,480,203,576,224C672,245,768,267,864,250.7C960,235,1056,181,1152,165.3C1248,149,1344,171,1392,181.3L1440,192L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
            ></path>
          </svg>
        </div>
      </div>

      {/* --- RIGHT SIDE: REGISTER FORM --- */}
      <div className="flex w-full flex-col items-center justify-center bg-white px-8 md:px-16 lg:w-1/3 py-10 overflow-y-auto">
        <div className="w-full max-w-sm">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Đăng ký tài khoản
          </h2>
          <p className="text-gray-400 text-sm mb-6 font-medium">
            Tham gia cộng đồng Tìm Đồ Sinh Viên ngay!
          </p>

          {/* 5. Hiển thị thông báo lỗi */}
          {error && (
            <div className="mb-4 rounded-lg bg-red-50 p-3 text-xs text-red-500 border border-red-100">
              {error}
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            {/* Họ và Tên */}
            <div>
              <label className="text-sm font-semibold text-gray-600 mb-1 block">
                Họ và Tên
              </label>
              <div className="relative group">
                <FaRegUser className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-[#319795]" />
                <input
                  name="username"
                  type="text"
                  required
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="Nguyễn Văn A"
                  className="w-full rounded-xl border border-gray-100 bg-gray-50 py-3 pl-12 pr-4 text-sm outline-none transition-all focus:border-[#319795] focus:bg-white focus:ring-4 focus:ring-teal-50"
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="text-sm font-semibold text-gray-600 mb-1 block">
                Email
              </label>
              <div className="relative group">
                <FaRegEnvelope className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-[#319795]" />
                <input
                  name="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="example@student.ptit.edu.vn"
                  className="w-full rounded-xl border border-gray-100 bg-gray-50 py-3 pl-12 pr-4 text-sm outline-none transition-all focus:border-[#319795] focus:bg-white focus:ring-4 focus:ring-teal-50"
                />
              </div>
            </div>

            {/* Mật khẩu */}
            <div>
              <label className="text-sm font-semibold text-gray-600 mb-1 block">
                Mật khẩu
              </label>
              <div className="relative group">
                <MdLockOutline className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 text-lg group-focus-within:text-[#319795]" />
                <input
                  name="password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Tối thiểu 6 ký tự"
                  className="w-full rounded-xl border border-gray-100 bg-gray-50 py-3 pl-12 pr-12 text-sm outline-none transition-all focus:border-[#319795] focus:bg-white focus:ring-4 focus:ring-teal-50"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <FaRegEyeSlash /> : <FaRegEye />}
                </button>
              </div>
            </div>

            {/* Xác nhận mật khẩu */}
            <div>
              <label className="text-sm font-semibold text-gray-600 mb-1 block">
                Xác nhận mật khẩu
              </label>
              <div className="relative group">
                <MdLockOutline className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 text-lg group-focus-within:text-[#319795]" />
                <input
                  name="confirmPassword"
                  type="password"
                  required
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="Nhập lại mật khẩu"
                  className="w-full rounded-xl border border-gray-100 bg-gray-50 py-3 pl-12 pr-4 text-sm outline-none transition-all focus:border-[#319795] focus:bg-white focus:ring-4 focus:ring-teal-50"
                />
              </div>
            </div>

            {/* Điều khoản */}
            <div className="flex items-start gap-2 py-2">
              <input
                type="checkbox"
                required
                className="accent-[#319795] w-4 h-4 rounded mt-0.5"
                id="terms"
              />
              <label
                htmlFor="terms"
                className="text-xs text-gray-500 leading-relaxed cursor-pointer"
              >
                Tôi đồng ý với các{" "}
                <span className="text-[#319795] font-bold">Điều khoản</span> và{" "}
                <span className="text-[#319795] font-bold">Chính sách</span>.
              </label>
            </div>

            {/* Register Button */}
            <button
              type="submit"
              disabled={loading}
              className={`w-full rounded-xl py-3.5 font-bold text-white shadow-lg transition-all active:scale-[0.98] mt-2 ${
                loading
                  ? "bg-gray-400"
                  : "bg-[#319795] hover:bg-[#2c7a7b] shadow-teal-100"
              }`}
            >
              {loading ? "ĐANG TẠO TÀI KHOẢN..." : "ĐĂNG KÝ NGAY"}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-6 flex items-center justify-center">
            <div className="w-full border-t border-gray-100"></div>
            <span className="absolute bg-white px-4 text-xs font-medium text-gray-400 uppercase">
              Hoặc
            </span>
          </div>

          <button className="flex w-full items-center justify-center gap-3 rounded-xl border border-gray-200 py-3 text-sm font-bold text-gray-700 transition-all hover:bg-gray-50 active:scale-[0.98]">
            <FcGoogle className="text-xl" /> Đăng ký với Google
          </button>

          <p className="mt-8 text-center text-sm font-medium text-gray-500">
            Đã có tài khoản?{" "}
            <Link
              to="/login"
              className="text-[#319795] font-bold hover:underline"
            >
              Đăng nhập ngay
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
