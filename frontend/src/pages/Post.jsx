import React, { useState, useRef } from "react";
import { MdCheckCircle, MdCloudUpload, MdClose } from "react-icons/md";
import { useAppContext } from "../context/AppContext";
import { createPost } from "../services/postService";
import { FaMagnifyingGlassChart, FaHandHolding } from "react-icons/fa6";

const CreatePost = () => {
  const { user } = useAppContext();
  const fileInputRef = useRef(null);

  const [postType, setPostType] = useState("lost");
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false); // Thêm trạng thái chờ khi đang upload

  const CATEGORIES = [
    "Thẻ sinh viên",
    "Căn cước công dân",
    "Bằng lái xe",
    "Thẻ ATM/Ngân hàng",
    "Ví/Bóp",
    "Điện thoại/Laptop",
    "Chìa khóa",
    "Balo/Túi xách",
    "Giấy tờ khác",
    "Khác",
  ];
  
  const LOCATION_OPTIONS = [
    "Tòa A1",
    "Tòa A2",
    "Tòa A3",
    "Sảnh A1",
    "Sảnh A2",
    "Căn tin",
    "Bãi gửi xe",
    "Không có",
    "Khác",
  ];

  const [formData, setFormData] = useState({
    description: "",
    category: "",
    location: "",
    customLocation: "",
    contact: "",
    customCategory: "",
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        // Giới hạn 5MB
        alert("File ảnh quá lớn, vui lòng chọn file dưới 5MB");
        return;
      }
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const removeImage = () => {
    setImageFile(null);
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!imageFile) return alert("Vui lòng tải lên ảnh minh họa");

    setLoading(true);

    // 1. Lấy token từ localStorage (hoặc nơi bạn lưu khi đăng nhập)
    const token = localStorage.getItem("token");

    // Kiểm tra nhanh xem có token không trước khi gửi
    if (!token) {
      alert("Phiên đăng nhập hết hạn, vui lòng đăng nhập lại!");
      setLoading(false);
      return;
    }

    const finalCategory = (formData.category === "Khác" ? formData.customCategory : formData.category) || "Khác";
    const finalLocation = (formData.location === "Khác" ? formData.customLocation : (formData.location === "Không có" ? "" : formData.location)) || "";
    
    const locationText = finalLocation ? ` tại ${finalLocation}` : "";
    const generatedTitle = `${postType === "lost" ? "Tìm" : "Nhặt được"} ${finalCategory}${locationText}`;
 
    const data = new FormData();
    data.append("title", generatedTitle);
    data.append("description", formData.description || "");
    data.append("type", postType.toUpperCase());
    data.append("category", finalCategory);
    data.append("location", finalLocation);
    data.append("contact", formData.contact || "");
    data.append("file", imageFile);
 
    try {
      const responseData = await createPost(data);
      if (responseData) {
        alert("Đăng tin thành công!");
        setFormData({
          description: "",
          category: "",
          location: "",
          customLocation: "",
          contact: "",
          customCategory: "",
        });
        removeImage();
      }
    } catch (error) {
      console.error("Lỗi đăng tin:", error);
      const status = error.response?.status;
      const detail = error.response?.data?.detail;
      const errorMessage = detail ? JSON.stringify(detail) : (error.message || "Lỗi không xác định");

      if (status === 401) {
        alert("Bạn cần đăng nhập lại để thực hiện hành động này.");
      } else {
        alert(`Lỗi (${status || "Network"}): ${errorMessage}. Vui lòng thử lại sau!`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full bg-[#f0f2f5] min-h-screen">
      <div className="xl:px-[250px] px-4 md:px-10 mx-auto py-4 md:py-8">
        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 md:p-12">
      {/* Header Section */}
      <div className="text-center mb-10">
        <h1 className="text-3xl font-extrabold text-[#1e293b] uppercase tracking-wider">
          Trang Đăng Tin
        </h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          {!user ? (
            <div className="py-10 text-center bg-gray-50 rounded-2xl border border-dashed border-gray-200">
              <h2 className="text-xl font-bold text-gray-800 mb-2">
                Bạn cần đăng nhập để đăng tin
              </h2>
              <p className="text-gray-500 text-sm">
                Vui lòng đăng nhập bằng tài khoản Google để tiếp tục.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="bg-white p-6 md:p-8 rounded-3xl border border-gray-100 shadow-2xl shadow-red-500/5 space-y-8">
              {/* Loại tin */}
              <div>
                <label className="text-sm font-bold text-gray-800 block mb-3">
                  1. Loại tin đăng
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div
                    onClick={() => setPostType("lost")}
                    className={`cursor-pointer p-4 rounded-xl border-2 transition-all flex items-center gap-4 ${postType === "lost" ? "border-pink-500 bg-pink-50" : "border-gray-50 hover:border-pink-200"}`}
                  >
                    <div className="w-12 h-12 rounded-full bg-pink-100 flex items-center justify-center text-pink-500 text-2xl">
                    <FaMagnifyingGlassChart />
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-800">
                        Tìm đồ thất lạc
                      </h3>
                      <p className="text-[11px] text-gray-400">
                        Đăng bài tìm kiếm đồ bị mất
                      </p>
                    </div>
                  </div>
                  <div
                    onClick={() => setPostType("found")}
                    className={`cursor-pointer p-4 rounded-xl border-2 transition-all flex items-center gap-4 ${postType === "found" ? "border-red-500 bg-red-50" : "border-gray-100 hover:border-red-500"}`}
                  >
                    <div className="w-12 h-12 rounded-full bg-red-500 flex items-center justify-center text-white text-2xl">
                    <FaHandHolding />
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-800">Nhặt được đồ</h3>
                      <p className="text-[11px] text-gray-400">
                        Đăng bài món đồ nhặt được
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Tải ảnh */}
              <div>
                <label className="text-sm font-bold text-gray-800 block mb-3">
                  2. Ảnh minh họa (Khuyến nghị)
                </label>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleImageChange}
                  accept="image/*"
                  className="hidden"
                />
                <div
                  onClick={() => !imagePreview && fileInputRef.current.click()}
                  className={`border-2 border-dashed rounded-2xl py-12 flex flex-col items-center justify-center transition-all cursor-pointer relative ${imagePreview ? "border-red-500" : "border-gray-200 bg-gray-50 hover:bg-white"}`}
                >
                  {imagePreview ? (
                    <div className="relative group">
                      <img
                        src={imagePreview}
                        alt="Preview"
                        className="max-h-64 rounded-lg object-contain"
                      />
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeImage();
                        }}
                        className="absolute -top-2 -right-2 bg-red-500 text-white p-1 rounded-full shadow-lg hover:scale-110 transition-transform"
                      >
                        <MdClose size={20} />
                      </button>
                    </div>
                  ) : (
                    <>
                      <MdCloudUpload className="text-5xl text-gray-300" />
                      <p className="mt-4 text-[#dc2626] font-bold text-sm">
                        Nhấp để tải ảnh
                      </p>
                      <p className="text-gray-400 text-[10px] mt-1">
                        Hỗ trợ JPG, PNG (Tối đa 5MB)
                      </p>
                    </>
                  )}
                </div>
              </div>

              {/* Thông tin chi tiết */}
              <div className="space-y-5">
                <label className="text-sm font-bold text-gray-800 block mb-3">
                  3. Thông tin chi tiết
                </label>
                <div className="space-y-4">
                  <div>
                    <label className="text-xs font-bold text-gray-700 block mb-1.5">
                      Nội dung *
                    </label>
                    <textarea
                      name="description"
                      value={formData.description}
                      onChange={handleInputChange}
                      required
                      rows="3"
                      placeholder="Mô tả chi tiết món đồ..."
                      className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:border-[#dc2626] outline-none resize-none"
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs font-bold text-gray-700 block mb-1.5">
                        Khu vực *
                      </label>
                      <select
                        name="location"
                        value={formData.location}
                        onChange={handleInputChange}
                        required
                        className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:border-[#dc2626] outline-none"
                      >
                        <option value="">-- Chọn tòa nhà --</option>
                        {LOCATION_OPTIONS.map((loc) => (
                          <option key={loc} value={loc}>
                            {loc}
                          </option>
                        ))}
                      </select>
                      {formData.location === "Khác" && (
                        <div className="mt-3">
                          <input
                            name="customLocation"
                            value={formData.customLocation}
                            onChange={handleInputChange}
                            required
                            type="text"
                            placeholder="Nhập khu vực cụ thể..."
                            className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:border-[#dc2626] outline-none"
                          />
                        </div>
                      )}
                    </div>
                    <div>
                      <label className="text-xs font-bold text-gray-700 block mb-1.5">
                        Loại đồ *
                      </label>
                      <select
                        name="category"
                        value={formData.category}
                        onChange={handleInputChange}
                        required
                        className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:border-[#dc2626] outline-none"
                      >
                        <option value="">-- Chọn loại --</option>
                        {CATEGORIES.map((cat) => (
                          <option key={cat} value={cat}>
                            {cat}
                          </option>
                        ))}
                      </select>
                      {formData.category === "Khác" && (
                        <div className="mt-3">
                          <input
                            name="customCategory"
                            value={formData.customCategory}
                            onChange={handleInputChange}
                            required
                            type="text"
                            placeholder="Nhập tên đồ vật..."
                            className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:border-[#dc2626] outline-none"
                          />
                        </div>
                      )}
                    </div>
                  </div>
                  <div>
                    <label className="text-xs font-bold text-gray-700 block mb-1.5">
                      Thông tin liên hệ *
                    </label>
                    <input
                      name="contact"
                      value={formData.contact}
                      onChange={handleInputChange}
                      required
                      type="text"
                      placeholder="SĐT hoặc Facebook..."
                      className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:border-[#dc2626] outline-none"
                    />
                  </div>
                </div>

                <button
                  disabled={loading}
                  type="submit"
                  className={`w-full ${loading ? "bg-gray-400" : "bg-[#dc2626] hover:bg-[#b91c1c]"} text-white font-bold py-4 rounded-2xl shadow-lg transition-all active:scale-[0.98] mt-4`}
                >
                  {loading ? "Đang xử lý..." : "Đăng tin ngay"}
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm space-y-8">
            <h3 className="text-xl font-extrabold text-[#1e293b] flex items-center gap-2 border-b border-gray-100 pb-4">
              💡 Mẹo đăng tin sát sườn
            </h3>

            {/* Mục 1: Nhặt được đồ */}
            <div className="space-y-4">
              <h4 className="text-sm font-bold text-emerald-600 flex items-center gap-2 bg-emerald-50 px-3 py-1.5 rounded-lg w-fit">
                📍 Cho người Nhặt được
              </h4>
              <div className="space-y-3">
                <div className="group border-l-2 border-emerald-100 pl-4 py-1">
                  <p className="text-[13px] font-bold text-gray-800 mb-1">Giữ lại "Chi tiết bí mật"</p>
                  <p className="text-[12px] text-gray-500 leading-relaxed">
                    Hãy che đi một vài thông tin đặc biệt (4 số cuối ATM, phụ kiện nhỏ, hình nền...). Giúp xác minh đúng chủ nhân, tránh "nhận vơ".
                  </p>
                </div>
                <div className="group border-l-2 border-emerald-100 pl-4 py-1">
                  <p className="text-[13px] font-bold text-gray-800 mb-1">Địa điểm bàn giao</p>
                  <p className="text-[12px] text-gray-500 leading-relaxed">
                    Ưu tiên nơi công cộng: Sảnh A2, Căn tin, hoặc gửi tại Văn phòng Đoàn/Hội để đảm bảo an toàn.
                  </p>
                </div>
              </div>
            </div>

            {/* Mục 2: Mất đồ */}
            <div className="space-y-4">
              <h4 className="text-sm font-bold text-red-600 flex items-center gap-2 bg-red-50 px-3 py-1.5 rounded-lg w-fit">
                🔍 Cho người Mất đồ
              </h4>
              <div className="space-y-3">
                <div className="group border-l-2 border-red-100 pl-4 py-1">
                  <p className="text-[13px] font-bold text-gray-800 mb-1">"Dấu hiệu nhận biết"</p>
                  <p className="text-[12px] text-gray-500 leading-relaxed">
                    Ghi rõ đặc điểm riêng (móc khóa hình Loopy, vết trầy ở góc...). Càng chi tiết, càng dễ nhận ra đồ của bạn.
                  </p>
                </div>
                <div className="group border-l-2 border-red-100 pl-4 py-1">
                  <p className="text-[13px] font-bold text-gray-800 mb-1">Mốc thời gian</p>
                  <p className="text-[12px] text-gray-500 leading-relaxed">
                    Cố gắng nhớ lại khoảng thời gian hẹp nhất (VD: Giữa ca 2 và ca 3 tại phòng 402-A2) để lọc tin nhanh hơn.
                  </p>
                </div>
              </div>
            </div>

            {/* Mục 3: Hình ảnh */}
            <div className="space-y-4">
              <h4 className="text-sm font-bold text-blue-600 flex items-center gap-2 bg-blue-50 px-3 py-1.5 rounded-lg w-fit">
                📸 Về Hình ảnh
              </h4>
              <div className="space-y-3">
                <div className="group border-l-2 border-blue-100 pl-4 py-1">
                  <p className="text-[13px] font-bold text-gray-800 mb-1">Ảnh thật - Việc thật</p>
                  <p className="text-[12px] text-gray-500 leading-relaxed">
                    Hạn chế dùng ảnh mạng. Một tấm ảnh chụp vội tại hiện trường có giá trị tin cậy cao hơn gấp nhiều lần.
                  </p>
                </div>
                <div className="group border-l-2 border-blue-100 pl-4 py-1">
                  <p className="text-[13px] font-bold text-gray-800 mb-1">Góc chụp thông minh</p>
                  <p className="text-[12px] text-gray-500 leading-relaxed">
                    Chụp các vết trầy xước đặc trưng nhưng tuyệt đối XÓA mật khẩu hoặc mã PIN dán sau máy.
                  </p>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</div>
);
};

export default CreatePost;
