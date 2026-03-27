import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; // 1. Import useNavigate
import icons from "../assets/icons/icon";

const NoScrollbarStyle = () => (
  <style dangerouslySetInnerHTML={{ __html: `
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
  `}} />
);

const DetailedSearch = () => {
  const navigate = useNavigate(); // 2. Khởi tạo navigate
  const [viewMode, setViewMode] = useState("list");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 6;

  const [allPosts, setAllPosts] = useState([]);
  const [filteredPosts, setFilteredPosts] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("Tất cả danh mục");
  const [selectedType, setSelectedType] = useState("Tất cả loại tin");
  const [selectedLocation, setSelectedLocation] = useState("Mọi địa điểm");

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

  const QUICK_TAGS = [
    { label: "Thẻ sinh viên", icon: "📄" },
    { label: "Căn cước công dân", icon: "💳" },
    { label: "Chìa khóa", icon: "🔑" },
    { label: "Điện thoại/Laptop", icon: "💻" },
    { label: "Balo/Túi xách", icon: "💼" },
    { label: "Ví/Bóp", icon: "👛" },
  ];

  React.useEffect(() => {
    const fetchPosts = async () => {
      try {
        const { getAllPosts } = await import("../services/postService");
        const data = await getAllPosts();
        
        const formatted = data.map(post => ({
          id: post.id,
          title: post.title,
          description: post.description,
          date: new Date(post.created_at).toLocaleDateString("vi-VN"),
          location: post.location,
          type: post.type === "FOUND" ? "Nhặt được" : "Mất đồ",
          category: post.category,
          image: post.image || "https://via.placeholder.com/300x200",  // ✅ sửa image_url → image
          author: post.owner?.username || "Ẩn danh",
          views: post.views,
          comments: 0,  // Backend không trả về comment count, hiện 0 tạm thời
          isUrgent: false,
        }));
        setAllPosts(formatted);
        setFilteredPosts(formatted);
      } catch (err) {
        console.error("Lỗi lấy danh sách bài đăng:", err);
      }
    };
    fetchPosts();
  }, []);

  React.useEffect(() => {
    let result = allPosts;

    if (searchQuery) {
      result = result.filter(post => 
        post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        post.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (selectedCategory !== "Tất cả danh mục") {
      result = result.filter(post => post.category === selectedCategory);
    }

    if (selectedType !== "Tất cả loại tin") {
      result = result.filter(post => post.type === selectedType);
    }
    
    if (selectedLocation !== "Mọi địa điểm") {
      result = result.filter(post => post.location && post.location.toLowerCase().includes(selectedLocation.toLowerCase()));
    }

    setFilteredPosts(result);
    setCurrentPage(1);
  }, [searchQuery, selectedCategory, selectedType, selectedLocation, allPosts]);

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentPosts = filteredPosts.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredPosts.length / itemsPerPage);

  const paginate = (pageNumber) => {
    setCurrentPage(pageNumber);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="w-full bg-[#fcfcfc] min-h-screen xl:px-[250px] px-4 md:px-10 py-16 flex flex-col items-center">
      <NoScrollbarStyle />
      
      <div className="w-full max-w-4xl space-y-12">
        
        {/* SECTION 1: CENTRAL SEARCH BAR */}
        <div className="relative w-full group">
          <div className="absolute -inset-0.5 bg-gray-100 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
          <div className="relative flex items-center bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden pr-1.5 focus-within:ring-2 focus-within:ring-red-100 transition-all">
            <span className="pl-6 text-gray-300 text-lg">🔍</span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Vui lòng nhập món đồ muốn tìm"
              className="w-full px-4 py-5 outline-none text-gray-600 text-[16px] font-normal placeholder:text-gray-300"
            />
            <button 
              className="bg-[#dc2626] text-white px-8 py-3.5 rounded-xl font-bold text-sm hover:bg-[#b91c1c] transition-all active:scale-95 shadow-lg shadow-red-500/20"
            >
              Tìm kiếm
            </button>
          </div>
        </div>


        {/* RESULTS FEED */}
        <div className="w-full space-y-8 pt-8 border-t border-gray-50">
        </div>

        {/* GRID/LIST RENDER */}
        <div
          className={
            viewMode === "grid"
              ? "grid grid-cols-1 md:grid-cols-3 gap-6"
              : "space-y-6"
          }
        >
          {currentPosts.map((post, index) =>
            viewMode === "list" ? (
              <ListItem
                key={index}
                post={post}
                onNavigate={() => navigate(`/post/${post.id}`)}
              />
            ) : (
              <GridItem
                key={index}
                post={post}
                onNavigate={() => navigate(`/post/${post.id}`)}
              />
            ),
          )}
        </div>

        {/* PAGINATION */}
        <div className="flex justify-center items-center gap-2 mt-12">
          <button
            disabled={currentPage === 1}
            onClick={() => paginate(currentPage - 1)}
            className="w-8 h-8 flex items-center justify-center rounded-lg border border-gray-100 text-gray-400 disabled:opacity-30"
          >
            ‹
          </button>
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((number) => (
            <button
              key={number}
              onClick={() => paginate(number)}
              className={`w-8 h-8 flex items-center justify-center rounded-lg font-bold transition-all ${currentPage === number ? "bg-[#dc2626] text-white" : "border border-gray-100 text-gray-400"}`}
            >
              {number}
            </button>
          ))}
          <button
            disabled={currentPage === totalPages}
            onClick={() => paginate(currentPage + 1)}
            className="w-8 h-8 flex items-center justify-center rounded-lg border border-gray-100 text-gray-400 disabled:opacity-30"
          >
            ›
          </button>
        </div>
      </div>
    </div>
  );
};

// 3. Cập nhật ListItem: Thêm onClick vào thẻ cha và nút
const ListItem = ({ post, onNavigate }) => (
  <div
    onClick={onNavigate}
    className="group flex flex-col md:flex-row gap-6 p-4 border border-gray-100 rounded-2xl hover:border-red-500 hover:shadow-md transition-all relative cursor-pointer"
  >
    {post.isUrgent && (
      <span className="absolute -top-2 -left-2 bg-red-500 text-white text-[10px] px-2 py-1 rounded-lg font-bold z-10 shadow-sm">
        TIN GẤP
      </span>
    )}
    <div className="w-full md:w-48 h-40 md:h-32 rounded-xl overflow-hidden flex-shrink-0">
      <img
        src={post.image}
        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        alt=""
      />
    </div>
    <div className="flex-1 flex flex-col justify-between py-1">
      <div>
        <div className="flex gap-2 mb-2">
          <span className="bg-red-50 text-red-600 text-[10px] font-bold px-2 py-1 rounded">
            {post.type}
          </span>
          <span className="bg-red-50 text-red-500 text-[10px] font-bold px-2 py-1 rounded">
            {post.category}
          </span>
        </div>
        <h3 className="font-bold text-gray-800 mb-1 group-hover:text-[#dc2626] transition-colors">
          {post.title}
        </h3>
        <p className="text-[11px] text-gray-400 flex flex-wrap gap-4 mb-2">
          <span>📅 {post.date}</span>
          {post.location && <span>📍 {post.location}</span>}
        </p>
        <p className="text-xs text-gray-500 line-clamp-2">{post.description}</p>
      </div>
      <div className="flex justify-between items-center pt-3 mt-4 border-t border-gray-50">
        <div className="flex items-center gap-4 text-[10px] font-bold text-gray-400">
          <span className="flex items-center gap-1">👤 {post.author}</span>
          <span>👁️ {post.views}</span>
          <span>💬 {post.comments}</span>
        </div>
        <button className="text-[#dc2626] text-xs font-bold hover:translate-x-1 transition-transform">
          Xem chi tiết ❯
        </button>
      </div>
    </div>
  </div>
);

// 4. Cập nhật GridItem: Thêm onClick vào thẻ cha và nút
const GridItem = ({ post, onNavigate }) => (
  <div
    onClick={onNavigate}
    className="group border border-gray-100 rounded-3xl overflow-hidden hover:border-red-500 hover:shadow-xl transition-all bg-white flex flex-col h-full cursor-pointer"
  >
    <div className="relative h-48 overflow-hidden">
      {post.isUrgent && (
        <span className="absolute top-3 left-3 bg-red-500 text-white text-[10px] px-2 py-1 rounded-lg font-bold z-10">
          TIN GẤP
        </span>
      )}
      <img
        src={post.image}
        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        alt=""
      />
      <div className="absolute bottom-3 right-3 flex gap-2">
        <span className="bg-black/40 backdrop-blur-md text-white text-[10px] px-2 py-1 rounded flex items-center gap-1">
          👁️ {post.views}
        </span>
        <span className="bg-black/40 backdrop-blur-md text-white text-[10px] px-2 py-1 rounded flex items-center gap-1">
          💬 {post.comments}
        </span>
      </div>
    </div>
    <div className="p-5 flex flex-col flex-grow">
      <div className="flex gap-2 mb-3">
        <span className="bg-red-50 text-red-600 text-[10px] font-bold px-2 py-1 rounded">
          {post.type}
        </span>
        <span className="bg-red-50 text-red-500 text-[10px] font-bold px-2 py-1 rounded">
          {post.category}
        </span>
      </div>
      <h3 className="font-bold text-gray-800 mb-2 truncate uppercase text-sm group-hover:text-[#dc2626] transition-colors">
        {post.title}
      </h3>
      <p className="text-xs text-gray-500 line-clamp-2 mb-4 leading-relaxed flex-grow">
        {post.description}
      </p>
      <div className="flex justify-between items-center pt-4 border-t border-gray-50">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-red-500 text-white flex items-center justify-center text-[10px] font-bold">
            👤
          </div>
          <span className="text-[10px] font-bold text-gray-500">
            {post.author}
          </span>
        </div>
        <button className="bg-[#2ecc71] text-white px-4 py-2 rounded-full text-[11px] font-bold hover:bg-[#27ae60] shadow-sm transition-all active:scale-95">
          Xem ❯
        </button>
      </div>
    </div>
  </div>
);

export default DetailedSearch;
