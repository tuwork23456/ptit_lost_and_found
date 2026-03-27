import React from "react";
import icons from "../assets/icons/icon"; // Import bộ icon của bạn
import { FaFacebookF, FaEnvelope, FaGlobe } from "react-icons/fa";

const Footer = () => {
  const { IoSearch } = icons;

  return (
    <footer className="w-full bg-white border-t border-gray-100">
      {/* PHẦN NỘI DUNG CHÍNH */}
      <div className="xl:px-[250px] px-4 md:px-10 mx-auto py-12 grid grid-cols-1 md:grid-cols-3 gap-12">
        {/* Cột 1: Về chúng tôi */}
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-[#1e293b] uppercase tracking-wider border-b-2 border-orange-500 pb-2 w-fit">
            Về chúng tôi
          </h3>
          <div className="space-y-3">
            <h2 className="text-xl font-extrabold text-orange-600">Tìm Đồ Sinh Viên</h2>
            <p className="text-sm text-gray-500 leading-relaxed">
              Kết nối sinh viên, tìm lại đồ thất lạc
            </p>
            <p className="text-sm text-gray-600 font-semibold">
              Email: <span className="text-orange-500">support@sinhvien.edu.vn</span>
            </p>
          </div>
        </div>

        {/* Cột 2: Hỗ trợ & Hướng dẫn */}
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-[#1e293b] uppercase tracking-wider border-b-2 border-orange-500 pb-2 w-fit">
            Hỗ trợ & Hướng dẫn
          </h3>
          <div className="space-y-2.5">
            <p className="text-[14px] text-gray-500 font-medium">Hướng dẫn đăng tin</p>
            <p className="text-[14px] text-gray-500 font-medium">Câu hỏi thường gặp (FAQ)</p>
            <p className="text-[14px] text-gray-500 font-medium">Báo cáo vi phạm</p>
          </div>
        </div>

        {/* Cột 3: Pháp lý & Chính sách */}
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-[#1e293b] uppercase tracking-wider border-b-2 border-orange-500 pb-2 w-fit">
            Pháp lý & Chính sách
          </h3>
          <div className="space-y-2.5">
            <p className="text-[14px] text-gray-500 font-medium">Điều khoản sử dụng</p>
            <p className="text-[14px] text-gray-500 font-medium">Chính sách bảo mật</p>
            <p className="text-[14px] text-gray-500 font-medium">Miễn trừ trách nhiệm</p>
          </div>
        </div>
      </div>

      {/* DẢI COPYRIGHT - Xóa bỏ margin-top thừa để không bị hở trắng */}
      <div className="w-full bg-[#f1f5f9] py-4">
        <p className="text-center text-[12px] text-gray-500 font-medium">
          © 2026 Tìm Đồ Sinh Viên. Bảo lưu mọi quyền.
        </p>
      </div>
    </footer>
  );
};

export default Footer;
