import React, { useState } from "react";
import { Link } from "react-router-dom";
import { FaRegEnvelope, FaRegEye, FaRegEyeSlash } from "react-icons/fa6";
import { MdLockOutline } from "react-icons/md";
import { FcGoogle } from "react-icons/fc";
import { MdCheckCircle } from "react-icons/md";
import { useAppContext } from "../context/AppContext";

// 1. Import hàm login từ service bạn đã tạo
import { login } from "../services/authService";

const Login = () => {
  const { setUser, navigate } = useAppContext();
  const [showPassword, setShowPassword] = useState(false);

  // 2. Thêm state để quản lý form và trạng thái gửi dữ liệu
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // 3. Hàm xử lý thay đổi input
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (error) setError(""); // Xóa thông báo lỗi khi người dùng gõ lại
  };

  // 4. Hàm xử lý Submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const result = await login(formData);
      console.log("Đăng nhập thành công:", result);

      // Chuyển hướng sang trang chủ hoặc dashboard
      navigate("/");
      setUser(result.user);
    } catch (err) {
      // Lấy message lỗi từ FastAPI (detail)
      const errorMsg =
        err.response?.data?.detail || "Đăng nhập thất bại. Vui lòng thử lại.";
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen w-full font-sans">
      {/* --- LEFT SIDE: BANNER --- */}
      <div className="relative hidden w-2/3 flex-col items-center justify-center bg-gradient-to-br from-[#38b2ac] via-[#2c7a7b] to-[#285e61] p-12 lg:flex overflow-hidden">
        {" "}
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
        <div className="absolute bottom-0 left-0 w-full z-0 pointer-events-none select-none">
          <svg
            className="block w-full h-[150px] md:h-[250px]"
            viewBox="0 0 1440 320"
            preserveAspectRatio="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fill="#ffffff"
              fillOpacity="0.15"
              d="M0,224L48,213.3C96,203,192,181,288,181.3C384,181,480,203,576,224C672,245,768,267,864,250.7C960,235,1056,181,1152,165.3C1248,149,1344,171,1392,181.3L1440,192L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
            ></path>
          </svg>
        </div>
      </div>

      {/* --- RIGHT SIDE: LOGIN FORM --- */}
      <div className="flex w-full flex-col items-center justify-center bg-white px-8 md:px-16 lg:w-1/3">
        <div className="w-full max-w-sm">
          <h2 className="text-2xl font-bold text-gray-800 mb-8">Đăng nhập</h2>

          {/* 5. Hiển thị thông báo lỗi nếu có */}
          {error && (
            <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-500 border border-red-100">
              {error}
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            {/* Email */}
            <div>
              <label className="text-sm font-semibold text-gray-600 mb-1 block">
                Email
              </label>
              <div className="relative group">
                <FaRegEnvelope className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-[#319795]" />
                <input
                  name="email" // Quan trọng: Khớp với key trong formData
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="Nhập email tại đây"
                  className="w-full rounded-xl border border-gray-100 bg-gray-50 py-3 pl-12 pr-4 text-sm outline-none transition-all focus:border-[#319795] focus:bg-white focus:ring-4 focus:ring-teal-50"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="text-sm font-semibold text-gray-600 mb-1 block">
                Mật khẩu
              </label>
              <div className="relative group">
                <MdLockOutline className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 text-lg group-focus-within:text-[#319795]" />
                <input
                  name="password" // Quan trọng: Khớp với key trong formData
                  type={showPassword ? "text" : "password"}
                  required
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Nhập mật khẩu tại đây"
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

            {/* Remember & Forgot */}
            <div className="flex items-center justify-between text-xs font-medium">
              <label className="flex items-center gap-2 cursor-pointer text-gray-500 hover:text-gray-700">
                <input
                  type="checkbox"
                  className="accent-[#319795] w-4 h-4 rounded"
                />
                Ghi nhớ mật khẩu
              </label>
              <Link
                to="/forgot-password"
                size="small"
                className="text-[#dd6b20] hover:underline font-semibold"
              >
                Quên mật khẩu?
              </Link>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              disabled={loading} // Disable khi đang call API
              className={`w-full rounded-xl py-3.5 font-bold text-white shadow-lg transition-all active:scale-[0.98] ${
                loading
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-[#319795] hover:bg-[#2c7a7b] shadow-teal-100"
              }`}
            >
              {loading ? "ĐANG XỬ LÝ..." : "ĐĂNG NHẬP"}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-8 flex items-center justify-center">
            <div className="w-full border-t border-gray-100"></div>
            <span className="absolute bg-white px-4 text-xs font-medium text-gray-400 uppercase">
              Hoặc
            </span>
          </div>

          {/* Google Login */}
          <button className="flex w-full items-center justify-center gap-3 rounded-xl border border-gray-200 py-3 text-sm font-bold text-gray-700 transition-all hover:bg-gray-50 active:scale-[0.98]">
            <FcGoogle className="text-xl" /> Đăng nhập bằng Google
          </button>

          {/* Sign Up Link */}
          <p className="mt-8 text-center text-sm font-medium text-gray-500">
            Bạn chưa có tài khoản?{" "}
            <Link to="/register" className="text-[#319795] hover:underline">
              Đăng ký ngay
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
