import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { getAllPosts } from "../services/postService";

const PostCarousel = ({ title, badge, badgeColor, type, filterFn }) => {
  const navigate = useNavigate();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activePage, setActivePage] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(4);
  const trackRef = useRef(null);
  const dragStartX = useRef(0);
  const isDragging = useRef(false);

  useEffect(() => {
    getAllPosts()
      .then((data) => {
        const filtered = data
          .filter(filterFn)
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        setPosts(filtered);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // Calculate total pages and handle scroll sync
  useEffect(() => {
    if (!trackRef.current || posts.length === 0) return;

    const updateMetrics = () => {
      const perPage = window.innerWidth >= 768 ? 4 : 1;
      setItemsPerPage(perPage);
      setTotalPages(Math.ceil(posts.length / perPage));
    };

    updateMetrics();
    window.addEventListener("resize", updateMetrics);

    const handleScrollSync = () => {
      if (!trackRef.current || isScrolling.current) return;
      const scrollLeft = trackRef.current.scrollLeft;
      const containerWidth = trackRef.current.offsetWidth || 1;
      const pageIndex = Math.round(scrollLeft / containerWidth);
      setActivePage(pageIndex);
    };

    trackRef.current.addEventListener("scroll", handleScrollSync);
    return () => {
      window.removeEventListener("resize", updateMetrics);
      if (trackRef.current) trackRef.current.removeEventListener("scroll", handleScrollSync);
    };
  }, [posts, loading]);

  const isScrolling = useRef(false);

  const goToPage = (pageIndex) => {
    if (!trackRef.current) return;
    isScrolling.current = true;
    setActivePage(pageIndex);
    const containerWidth = trackRef.current.offsetWidth;
    trackRef.current.scrollTo({ left: pageIndex * containerWidth, behavior: "smooth" });
    
    // Unlock after animation finishes (approx 800ms)
    setTimeout(() => { isScrolling.current = false; }, 800);
  };

  const wheelCooldown = useRef(false);

  const handleWheel = (e) => {
    e.preventDefault();
    if (wheelCooldown.current) return;

    const track = trackRef.current;
    if (!track) return;

    const delta = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY;
    if (Math.abs(delta) < 20) return;

    const containerWidth = track.offsetWidth;
    track.scrollBy({ left: delta > 0 ? containerWidth : -containerWidth, behavior: "smooth" });

    wheelCooldown.current = true;
    setTimeout(() => { wheelCooldown.current = false; }, 400);
  };

  return (
    <div className="bg-white/80 backdrop-blur-2xl rounded-3xl p-6 shadow-2xl shadow-red-500/5 border border-white mt-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-5">
        <div className="flex items-center gap-2">
          <div className={`${badgeColor} text-white px-4 py-2 rounded-xl text-sm font-extrabold animate-bounce uppercase shadow-lg shadow-red-500/20`}>
            {badge}
          </div>
        </div>
        <button
          onClick={() => navigate("/search")}
          className="text-red-500 bg-red-50/50 border border-red-200/50 px-5 py-2 rounded-xl text-sm font-bold hover:bg-gradient-to-r hover:from-red-600 hover:to-rose-500 hover:text-white hover:border-transparent hover:shadow-lg hover:shadow-red-500/30 hover:-translate-y-0.5 transition-all duration-300"
        >
          Xem thêm →
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500" />
        </div>
      ) : posts.length === 0 ? (
        <div className="text-center py-12 text-gray-400 text-sm">Chưa có bài viết nào.</div>
      ) : (
        <div className="space-y-6">
          <style>{`.no-scrollbar::-webkit-scrollbar { display: none; }`}</style>
          <div
            ref={trackRef}
            onWheel={handleWheel}
            className="flex gap-4 overflow-x-auto pb-3 scroll-smooth no-scrollbar"
            style={{
              scrollSnapType: "x mandatory",
              scrollbarWidth: "none",
              msOverflowStyle: "none",
            }}
          >
            {posts.map((post) => (
              <div
                key={post.id}
                onMouseDown={(e) => {
                  dragStartX.current = e.clientX;
                  isDragging.current = false;
                }}
                onMouseMove={(e) => {
                  if (Math.abs(e.clientX - dragStartX.current) > 5) isDragging.current = true;
                }}
                onClick={() => {
                  if (!isDragging.current) navigate(`/post/${post.id}`);
                }}
                className="snap-card flex-shrink-0 w-full md:w-[calc((100%-48px)/4)] border border-white/60 rounded-3xl overflow-hidden hover:shadow-[0_20px_40px_-15px_rgba(220,38,38,0.25)] hover:border-red-100 bg-white/60 backdrop-blur-xl flex flex-col group cursor-pointer hover:-translate-y-2 transition-all duration-500"
                style={{ scrollSnapAlign: "start" }}
              >
                {/* Image */}
                <div className="relative h-40 overflow-hidden">
                  <img
                    src={post.image || "https://via.placeholder.com/300x200?text=No+Image"}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                    alt={post.title}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-gray-900/60 via-transparent to-transparent" />
                  <div className="absolute bottom-3 left-3 flex gap-1.5">
                    <span className={`${type === "LOST" ? "bg-pink-500" : "bg-emerald-500"} text-white text-[9px] px-2 py-1 rounded font-bold uppercase`}>
                      {type === "LOST" ? "Mất đồ" : "Nhặt được"}
                    </span>
                    <span className="bg-[#dc2626]/90 text-white text-[9px] px-2 py-1 rounded font-bold uppercase">
                      {post.category}
                    </span>
                  </div>
                </div>

                {/* Content */}
                <div className="p-4 flex flex-col flex-1">
                  <h3 className="font-extrabold text-gray-800 text-sm mb-1.5 line-clamp-2 uppercase tracking-wide group-hover:text-red-600 transition-colors duration-300">
                    {post.title}
                  </h3>
                  <p className="text-gray-500 text-[11px] line-clamp-2 mb-3 leading-relaxed flex-1">
                    {post.description}
                  </p>
                  {post.location && (
                    <div className="flex items-center gap-1 text-red-600 text-[11px] font-semibold mb-3">
                      <span>📍</span> {post.location}
                    </div>
                  )}
                  <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-red-500 to-rose-400 text-white flex items-center justify-center font-bold text-xs shadow-md">
                        {post.owner?.username?.charAt(0).toUpperCase() || "?"}
                      </div>
                      <span className="text-[11px] text-gray-700 font-bold truncate max-w-[80px]">
                        {post.owner?.username || "Ẩn danh"}
                      </span>
                    </div>
                    <span className="w-7 h-7 rounded-full bg-red-50 text-red-500 flex items-center justify-center font-bold text-sm group-hover:bg-red-500 group-hover:text-white transition-all duration-300">
                      →
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-3 pt-2">
              {[...Array(totalPages)].map((_, i) => (
                <button
                  key={i}
                  onClick={() => goToPage(i)}
                  className={`w-8 h-8 rounded-full text-xs font-bold transition-all duration-300 flex items-center justify-center border ${
                    activePage === i
                      ? "bg-[#dc2626] text-white border-[#dc2626] shadow-lg shadow-red-500/30 scale-110"
                      : "bg-white text-gray-400 border-gray-100 hover:border-red-200 hover:text-red-500"
                  }`}
                >
                  {i + 1}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const LatestNews = () => (
  <>
    <PostCarousel
      badge="Mất Đồ"
      badgeColor="bg-pink-500"
      type="LOST"
      filterFn={(p) => p.type === "LOST"}
    />
    <PostCarousel
      badge="Nhặt Được"
      badgeColor="bg-emerald-500"
      type="FOUND"
      filterFn={(p) => p.type === "FOUND"}
    />
  </>
);

export default LatestNews;
