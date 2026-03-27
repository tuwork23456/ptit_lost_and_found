import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAppContext } from "../context/AppContext";
import { getMyPosts, deletePost } from "../services/postService";
import { FaTrashAlt, FaRegEye, FaExclamationTriangle } from "react-icons/fa";
import { IoChatbubbleEllipses } from "react-icons/io5";

const ManagePost = () => {
  const { user, navigate } = useAppContext();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    if (!user) { navigate("/login"); return; }
    fetchMyPosts();
  }, [user]);

  const fetchMyPosts = async () => {
    try {
      setLoading(true);
      const data = await getMyPosts();
      const sorted = data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      setPosts(sorted);
    } catch (err) {
      console.error("Lỗi tải bài đăng:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (postId) => {
    if (!window.confirm("Bạn chắc chắn muốn xóa bài này?")) return;
    try {
      setDeletingId(postId);
      await deletePost(postId);
      setPosts((prev) => prev.filter((p) => p.id !== postId));
    } catch (err) {
      alert("Xóa thất bại. Vui lòng thử lại!");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="w-full bg-[#f0f2f5] min-h-screen xl:px-[250px] px-4 md:px-10 py-8">
      <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 md:p-10 min-h-[500px]">

        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-extrabold text-gray-800">Quản lý bài đăng</h2>
            <p className="text-sm text-gray-400 mt-1">Tổng {posts.length} bài đã đăng</p>
          </div>
          <button
            onClick={() => navigate("/post")}
            className="bg-gradient-to-r from-red-600 to-rose-500 text-white font-bold px-5 py-2.5 rounded-xl text-sm hover:shadow-lg hover:shadow-red-200 hover:-translate-y-0.5 transition-all"
          >
            + Đăng tin mới
          </button>
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex justify-center py-20">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-red-500" />
          </div>
        )}

        {/* Empty */}
        {!loading && posts.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-gray-400 gap-4">
            <FaExclamationTriangle className="text-5xl text-gray-200" />
            <p className="text-sm font-medium">Bạn chưa đăng tin nào.</p>
            <button
              onClick={() => navigate("/post")}
              className="bg-red-500 text-white text-sm font-bold px-6 py-2.5 rounded-xl hover:bg-red-600 transition"
            >
              Đăng tin ngay
            </button>
          </div>
        )}

        {/* Post List */}
        {!loading && posts.length > 0 && (
          <div className="space-y-4">
            {posts.map((post) => (
              <div
                key={post.id}
                className="flex gap-4 items-start bg-gray-50 border border-gray-100 rounded-2xl p-4 hover:border-red-100 hover:shadow-sm transition-all group"
              >
                {/* Thumbnail */}
                <div className="w-24 h-20 rounded-xl overflow-hidden flex-shrink-0 bg-gray-200">
                  <img
                    src={post.image || "https://via.placeholder.com/100?text=No+Img"}
                    alt={post.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-[9px] font-black px-2 py-0.5 rounded uppercase ${post.type === "LOST" ? "bg-pink-100 text-pink-600" : "bg-emerald-100 text-emerald-600"}`}>
                      {post.type === "LOST" ? "Mất đồ" : "Nhặt được"}
                    </span>
                    <span className="text-[9px] font-black px-2 py-0.5 rounded bg-purple-100 text-purple-600 uppercase">
                      {post.category}
                    </span>
                  </div>
                  <h3 className="font-bold text-gray-800 text-sm truncate mb-1">{post.title}</h3>
                  <p className="text-xs text-gray-400 truncate">{post.description}</p>
                  <div className="flex items-center gap-3 mt-2 text-[11px] text-gray-400">
                    <span>📍 {post.location}</span>
                    <span>📅 {new Date(post.created_at).toLocaleDateString("vi-VN")}</span>
                    <span>👁 {post.views} lượt xem</span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex flex-col gap-2 flex-shrink-0">
                  <button
                    onClick={() => navigate(`/post/${post.id}`)}
                    className="flex items-center gap-1.5 text-[11px] font-bold text-blue-500 bg-blue-50 px-3 py-2 rounded-xl hover:bg-blue-500 hover:text-white transition-all"
                  >
                    <FaRegEye /> Xem
                  </button>
                  <button
                    onClick={() => handleDelete(post.id)}
                    disabled={deletingId === post.id}
                    className="flex items-center gap-1.5 text-[11px] font-bold text-red-500 bg-red-50 px-3 py-2 rounded-xl hover:bg-red-500 hover:text-white transition-all disabled:opacity-50"
                  >
                    <FaTrashAlt /> {deletingId === post.id ? "Đang xóa..." : "Xóa"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ManagePost;
