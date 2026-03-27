import React, { useState, useRef, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useAppContext } from "../context/AppContext";
import { getPostById } from "../services/postService";
import { getComments, createComment } from "../services/commentService";
import { resolvePost, reportPost } from "../services/postService";
import {
  FaFacebook,
  FaLink,
  FaRegCommentDots,
  FaPaperPlane,
  FaEllipsisV,
  FaCheckCircle,
  FaTrashAlt,
} from "react-icons/fa";
import {
  MdOutlineLocationOn,
  MdOutlineSchool,
  MdOutlineCalendarToday,
  MdOutlineRemoveRedEye,
} from "react-icons/md";
import { IoChatbubbleEllipses } from "react-icons/io5";

const PostDetailCard = () => {
  const { id } = useParams();
  const { user, navigate, openChatWithReceiver } = useAppContext();
  
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [commentText, setCommentText] = useState("");

  // State cho Menu 3 chấm
  const [showActionMenu, setShowActionMenu] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [postData, commentsData] = await Promise.all([
          getPostById(id),
          getComments(id)
        ]);
        setPost(postData);
        // Sắp xếp comment mới nhất nổi lên trên
        setComments(commentsData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)));
      } catch (error) {
        console.error("Lỗi khi tải dữ liệu bài viết:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  // Xử lý đóng menu khi click ra ngoài
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowActionMenu(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSendComment = async () => {
    if (!commentText.trim()) return;
    try {
      const newComment = await createComment(id, commentText);
      // Gắn thông tin user hiện tại vào comment ảo để hiện ngay lập tức
      const formattedComment = {
        ...newComment,
        user: { id: user.id, username: user.username, email: user.email }
      };
      setComments([formattedComment, ...comments]);
      setCommentText("");
    } catch (error) {
      alert(error.response?.data?.detail || "Gửi bình luận thất bại!");
    }
  };

  if (loading) {
    return (
      <div className="w-full bg-[#f0f2f5] min-h-screen flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500"></div>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="w-full bg-[#f0f2f5] min-h-screen flex flex-col justify-center items-center">
        <h2 className="text-2xl font-bold text-gray-700">Không tìm thấy bài viết!</h2>
        <button onClick={() => navigate("/")} className="mt-4 text-red-500 hover:underline">Về trang chủ</button>
      </div>
    );
  }

  return (
    <div className="w-full bg-[#f0f2f5] min-h-screen xl:px-[250px] px-4 md:px-10 py-10">
      <div className="flex flex-col gap-6">
        {/* KHỐI 1: CHI TIẾT TIN CHÍNH */}
        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6 md:p-10">
          <h1 className="text-2xl font-bold text-[#2d3436] text-center mb-10 uppercase tracking-tight">
            Chi tiết tin
          </h1>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* CỘT TRÁI: ẢNH */}
            <div className="lg:col-span-4">
              <div className="rounded-2xl overflow-hidden border border-gray-100 shadow-sm sticky top-24">
                <img
                  src={post.image || "https://via.placeholder.com/400x500?text=No+Image"}
                  alt="Post content"
                  className="w-full h-auto object-cover hover:scale-105 transition-transform duration-500"
                />
              </div>
            </div>

            {/* CỘT GIỮA: THÔNG TIN */}
            <div className="lg:col-span-5 space-y-6">
              <div className="flex gap-2">
                <span className={`text-[11px] font-bold px-3 py-1 rounded-md uppercase ${post.type === "FOUND" ? "bg-[#e6fcf5] text-[#0ca678]" : "bg-red-50 text-red-500"}`}>
                  {post.type === "FOUND" ? "Nhặt được" : "Mất đồ"}
                </span>
                <span className="bg-[#f3f0ff] text-[#5f27cd] text-[11px] font-bold px-3 py-1 rounded-md uppercase">
                  {post.category}
                </span>
              </div>

              <div className="flex items-center gap-3">
                <h2 className="text-3xl font-extrabold text-[#1e293b] leading-tight">
                  {post.title}
                </h2>
                {post.is_resolved && (
                  <span className="bg-green-100 text-green-700 text-xs font-bold px-3 py-1 rounded-full uppercase border border-green-200 shadow-sm flex items-center gap-1">
                    <FaCheckCircle /> Đã giải quyết
                  </span>
                )}
              </div>

              <div className="text-gray-600 text-sm bg-gray-50 p-4 rounded-xl border border-gray-100 whitespace-pre-line">
                {post.description}
              </div>

              <div className="space-y-4 text-sm mt-4">
                <div className="flex items-start gap-4">
                  <MdOutlineLocationOn className="text-gray-400 text-xl mt-0.5" />
                  <div className="flex flex-col">
                    <span className="text-gray-400 font-bold text-xs uppercase">
                      Khu vực
                    </span>
                    <span className="font-semibold text-[#1e293b]">
                      {post.location}
                    </span>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <MdOutlineSchool className="text-gray-400 text-xl mt-0.5" />
                  <div className="flex flex-col">
                    <span className="text-gray-400 font-bold text-xs uppercase">
                      Liên hệ trực tiếp
                    </span>
                    <span className="font-semibold text-[#1e293b]">
                      {post.contact}
                    </span>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <MdOutlineCalendarToday className="text-gray-400 text-xl mt-0.5" />
                  <div className="flex flex-col">
                    <span className="text-gray-400 font-bold text-xs uppercase">
                      Ngày đăng
                    </span>
                    <span className="font-semibold text-[#1e293b]">
                       {new Date(post.created_at).toLocaleDateString("vi-VN")}
                    </span>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <MdOutlineRemoveRedEye className="text-gray-400 text-xl mt-0.5" />
                  <div className="flex flex-col">
                    <span className="text-gray-400 font-bold text-xs uppercase">
                      Lượt xem
                    </span>
                    <span className="font-semibold text-[#1e293b]">
                      {post.views} lượt
                    </span>
                  </div>
                </div>
              </div>

              <div className="pt-6 flex flex-col gap-3">
                <div className="flex gap-2 relative" ref={menuRef}>
                  {user?.id !== post.user_id && (
                  <button onClick={() => openChatWithReceiver({ id: post.user_id, username: post.owner?.username }, `📎 Bài đăng: ${window.location.href}`)} className="flex-1 bg-[#099268] hover:bg-[#087f5b] text-white font-bold py-4 rounded-xl flex items-center justify-center gap-2 transition-all active:scale-95 shadow-lg shadow-red-100">
                    <IoChatbubbleEllipses className="text-xl" /> Liên hệ nhận/trả đồ
                  </button>
                  )}

                  {/* NÚT 3 CHẤM DỌC */}
                  <div className="relative">
                    <button
                      onClick={() => setShowActionMenu(!showActionMenu)}
                      className="w-14 h-full bg-gray-50 border border-gray-100 rounded-xl flex items-center justify-center hover:bg-gray-100 text-gray-600 transition-colors"
                    >
                      <FaEllipsisV />
                    </button>

                    {/* MENU DROPDOWN */}
                    {showActionMenu && (
                      <div className="absolute right-0 bottom-full mb-2 w-52 bg-white rounded-2xl shadow-xl border border-gray-100 py-2 z-50 animate-in fade-in slide-in-from-bottom-2 duration-200">
                        {user?.id === post.user_id && !post.is_resolved && (
                          <button
                            onClick={async () => {
                              try {
                                await resolvePost(post.id);
                                setPost({ ...post, is_resolved: true });
                                setShowActionMenu(false);
                                alert("Đã đánh dấu giải quyết thành công!");
                              } catch (e) {
                                alert("Có lỗi xảy ra khi cập nhật!");
                              }
                            }}
                            className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 text-gray-700 transition-colors"
                          >
                            <FaCheckCircle className="text-gray-400 text-lg" />
                            <span className="text-sm font-medium">
                              Đã giải quyết
                            </span>
                          </button>
                        )}
                        <button
                          onClick={async () => {
                            if (!user) {
                              alert("Vui lòng đăng nhập để báo cáo!");
                              return;
                            }
                            const reason = window.prompt("Nhập lý do báo cáo bài viết/gỡ tin:");
                            if (reason) {
                              try {
                                await reportPost(post.id, reason);
                                alert("Đã gửi yêu cầu gỡ tin/báo cáo thành công. Cảm ơn bạn!");
                                setShowActionMenu(false);
                              } catch (e) {
                                alert("Có lỗi xảy ra khi gửi báo cáo!");
                              }
                            }
                          }}
                          className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 text-red-500 transition-colors"
                        >
                          <FaTrashAlt className="text-red-400 text-lg" />
                          <span className="text-sm font-medium">
                            Yêu cầu gỡ tin
                          </span>
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <button className="bg-[#fff9db] text-[#f08c00] py-3 rounded-xl text-[11px] font-bold flex items-center justify-center gap-2 border border-yellow-100 hover:bg-yellow-100 transition-all">
                    <FaFacebook className="text-lg" /> Facebook
                  </button>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(window.location.href);
                      alert("Đã copy liên kết!");
                    }}
                    className="bg-[#f8f9fa] text-[#495057] py-3 rounded-xl text-[11px] font-bold flex items-center justify-center gap-2 border border-gray-200 hover:bg-gray-200 transition-all"
                  >
                    <FaLink className="text-lg" /> Copy Link
                  </button>
                </div>
              </div>
            </div>

            {/* CỘT PHẢI: TÁC GIẢ */}
            <div className="lg:col-span-3">
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden sticky top-24">
                <div className="bg-[#064e3b] text-white py-3 text-center text-[10px] font-bold uppercase tracking-widest">
                  Người đăng tin
                </div>
                <div className="p-6 flex flex-col items-center">
                  <div
                    onClick={() => navigate(`/user/${post.user_id}`)}
                    className="w-20 h-20 rounded-full bg-red-500 text-white flex items-center justify-center text-3xl font-bold border-4 border-red-50 mb-3 shadow-sm cursor-pointer hover:scale-105 transition-transform"
                  >
                    {post.owner?.username?.charAt(0).toUpperCase() || "?"}
                  </div>
                  <h3
                    onClick={() => navigate(`/user/${post.user_id}`)}
                    className="font-bold text-gray-800 text-lg cursor-pointer hover:text-red-500 transition-colors"
                  >
                    {post.owner?.username || "Ẩn danh"}
                  </h3>
                  <span className="bg-red-50 text-red-500 text-[9px] font-black px-3 py-1 rounded-full border border-red-100 mt-2 uppercase">
                    ● USER
                  </span>

                  {user?.id !== post.user_id && (
                  <button 
                    onClick={() => openChatWithReceiver({ id: post.user_id, username: post.owner?.username }, `📎 Bài đăng: ${window.location.href}`)}
                    className="w-full bg-[#088f81] hover:bg-[#067469] text-white text-[10px] font-bold py-3 rounded-xl mt-6 transition-all uppercase shadow-md shadow-emerald-50 tracking-wide"
                  >
                    Nhắn tin cho người đăng
                  </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* KHỐI 2: BÌNH LUẬN */}
        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 md:p-10 mb-10">
          <div className="flex justify-between items-center border-b border-gray-50 pb-6 mb-8">
            <div className="flex items-center gap-2">
              <FaRegCommentDots className="text-2xl text-gray-700" />
              <h3 className="text-xl font-bold text-gray-800">
                Bình luận <span className="text-red-500">({comments.length})</span>
              </h3>
            </div>
          </div>

          <div className="w-full">
            {/* Input Comment */}
            {user ? (
              <div className="flex gap-4 mb-10">
                <div className="w-10 h-10 rounded-full bg-orange-500 flex-shrink-0 flex items-center justify-center text-white font-bold overflow-hidden shadow-sm">
                  {user.username?.charAt(0).toUpperCase() || "U"}
                </div>
                <div className="flex-1 space-y-3">
                  <textarea
                    value={commentText}
                    onChange={(e) => setCommentText(e.target.value)}
                    placeholder="Viết bình luận của bạn (Hỏi xin nhận đồ, báo rớt)..."
                    className="w-full bg-gray-50 border border-gray-100 rounded-2xl p-4 text-sm outline-none focus:bg-white focus:border-red-500 focus:ring-4 focus:ring-red-50 transition-all resize-none min-h-[100px]"
                  ></textarea>
                  <div className="flex justify-end">
                    <button
                      onClick={handleSendComment}
                      disabled={!commentText.trim()}
                      className="bg-[#5f27cd] hover:bg-[#4834d4] disabled:bg-gray-300 text-white px-6 py-2.5 rounded-xl font-bold text-sm transition-all flex items-center gap-2 shadow-lg shadow-red-500"
                    >
                      <FaPaperPlane className="text-xs" /> Gửi bình luận
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-6 mb-10 bg-gray-50 rounded-2xl border border-gray-100">
                <p className="text-gray-500 font-medium mb-3 text-sm">
                  Vui lòng đăng nhập để có thể bình luận trao đổi.
                </p>
                <button
                  onClick={() => navigate("/login")}
                  className="bg-red-500 text-white font-bold py-2 px-6 rounded-lg shadow-md hover:bg-red-500 transition-colors text-sm"
                >
                  Đăng nhập ngay
                </button>
              </div>
            )}

            {/* Render List Comments */}
            <div className="space-y-6">
              {comments.length === 0 ? (
                <div className="text-center text-gray-400 py-6 text-sm">Chưa có bình luận nào. Hãy là người đầu tiên!</div>
              ) : (
                comments.map((cmt) => (
                  <div key={cmt.id} className="flex gap-4 flex-start">
                    <div className="w-10 h-10 rounded-full bg-gray-200 flex-shrink-0 flex items-center justify-center text-gray-600 font-bold overflow-hidden">
                       {cmt.user?.username?.charAt(0).toUpperCase() || "?"}
                    </div>
                    <div className="flex bg-gray-50 flex-col rounded-2xl rounded-tl-none px-5 py-3 border border-gray-100 max-w-[80%]">
                      <div className="flex items-center gap-3 mb-1">
                        <span className="font-bold text-sm text-gray-800">{cmt.user?.username || "Ẩn danh"}</span>
                        <span className="text-[10px] text-gray-400">{new Date(cmt.created_at).toLocaleString("vi-VN")}</span>
                      </div>
                      <p className="text-sm text-gray-700 whitespace-pre-line">{cmt.content}</p>
                    </div>
                  </div>
                ))
              )}
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default PostDetailCard;
