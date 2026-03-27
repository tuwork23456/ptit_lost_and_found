import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { useAppContext } from "../context/AppContext";
import { FaRegCalendarAlt, FaBoxOpen, FaEye } from "react-icons/fa";
import { IoChatbubbleEllipses } from "react-icons/io5";
import { MdOutlineLocationOn } from "react-icons/md";

const ProfilePage = () => {
  const { id } = useParams();
  const { navigate, user, openChatWithReceiver } = useAppContext();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  // Nếu id không được truyền từ URL (route /profile), mặc định dùng ID của user đăng nhập
  const targetId = id ? parseInt(id) : user?.id;

  useEffect(() => {
    if (!targetId) {
      setLoading(false);
      return;
    }
    axios.get(`http://localhost:8000/users/${targetId}`)
      .then((res) => setProfile(res.data))
      .catch(() => setProfile(null))
      .finally(() => setLoading(false));
  }, [targetId]);

  const isOwnProfile = user?.id === targetId;

  if (loading) return (
    <div className="min-h-screen flex justify-center items-center">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-red-500" />
    </div>
  );

  if (!profile) return (
    <div className="min-h-screen flex flex-col justify-center items-center gap-4">
      <p className="text-gray-500 text-lg font-medium">Không tìm thấy người dùng.</p>
      <button onClick={() => navigate("/")} className="text-red-500 hover:underline text-sm">← Về trang chủ</button>
    </div>
  );

  const joinYear = profile.created_at ? new Date(profile.created_at).getFullYear() : "?";

  return (
    <div className="w-full bg-[#f0f2f5] min-h-screen xl:px-[250px] px-4 md:px-10 py-10">
      <div className="flex flex-col gap-6">

        {/* === PROFILE CARD === */}
        <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
          {/* Cover gradient */}
          <div className="h-28 bg-gradient-to-r from-red-600 via-rose-500 to-pink-400" />

          <div className="px-8 pb-8 -mt-12">
            <div className="flex flex-col sm:flex-row items-start sm:items-end gap-4">
              {/* Avatar */}
              <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-red-500 to-rose-400 text-white flex items-center justify-center text-4xl font-black shadow-xl border-4 border-white">
                {profile.username?.charAt(0).toUpperCase()}
              </div>

              <div className="flex-1">
                <h1 className="text-2xl font-extrabold text-gray-800">{profile.username}</h1>
                <p className="text-sm text-gray-400 mt-0.5">{profile.email}</p>
              </div>

              {/* Action */}
              {!isOwnProfile && user && (
                <button
                  onClick={() => openChatWithReceiver({ id: profile.id, username: profile.username })}
                  className="flex items-center gap-2 bg-gradient-to-r from-red-600 to-rose-500 text-white font-bold px-5 py-2.5 rounded-xl text-sm hover:shadow-lg hover:shadow-red-200 hover:-translate-y-0.5 transition-all"
                >
                  <IoChatbubbleEllipses className="text-lg" /> Nhắn tin
                </button>
              )}
              {isOwnProfile && (
                <button
                  onClick={() => navigate("/manage-post")}
                  className="flex items-center gap-2 bg-gray-100 text-gray-700 font-bold px-5 py-2.5 rounded-xl text-sm hover:bg-gray-200 transition-all"
                >
                  Quản lý bài đăng →
                </button>
              )}
            </div>

            {/* Stats row */}
            <div className="flex gap-6 mt-6 pt-6 border-t border-gray-50">
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <FaBoxOpen className="text-red-400" />
                <span><strong className="text-gray-800">{profile.post_count}</strong> bài đăng</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <FaRegCalendarAlt className="text-red-400" />
                <span>Tham gia từ <strong className="text-gray-800">{joinYear}</strong></span>
              </div>
            </div>
          </div>
        </div>

        {/* === POSTS GRID === */}
        <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6 md:p-8">
          <h2 className="text-lg font-extrabold text-gray-800 mb-6">
            Bài đăng của {isOwnProfile ? "bạn" : profile.username}
            <span className="ml-2 text-red-500">({profile.post_count})</span>
          </h2>

          {profile.posts.length === 0 ? (
            <div className="text-center py-16 text-gray-400 text-sm">
              Chưa có bài đăng nào.
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {profile.posts.map((post) => (
                <div
                  key={post.id}
                  onClick={() => navigate(`/post/${post.id}`)}
                  className="border border-gray-100 rounded-2xl overflow-hidden hover:shadow-md hover:-translate-y-1 cursor-pointer transition-all duration-300 group"
                >
                  {/* Thumbnail */}
                  <div className="h-36 overflow-hidden bg-gray-100">
                    <img
                      src={post.image || "https://via.placeholder.com/300x200?text=No+Image"}
                      alt={post.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                  </div>

                  <div className="p-3">
                    <div className="flex gap-1 mb-2">
                      <span className={`text-[9px] font-black px-2 py-0.5 rounded uppercase ${post.type === "LOST" ? "bg-pink-100 text-pink-600" : "bg-emerald-100 text-emerald-600"}`}>
                        {post.type === "LOST" ? "Mất đồ" : "Nhặt được"}
                      </span>
                      <span className="text-[9px] font-black px-2 py-0.5 rounded bg-purple-100 text-purple-600 uppercase">
                        {post.category}
                      </span>
                    </div>
                    <h3 className="font-bold text-gray-800 text-sm line-clamp-2 mb-2 group-hover:text-red-600 transition-colors">
                      {post.title}
                    </h3>
                    <div className="flex justify-between text-[10px] text-gray-400">
                      <span className="flex items-center gap-1">
                        <MdOutlineLocationOn /> {post.location}
                      </span>
                      <span className="flex items-center gap-1">
                        <FaEye /> {post.views}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
