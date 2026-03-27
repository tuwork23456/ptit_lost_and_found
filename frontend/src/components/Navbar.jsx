import React, { useState, useEffect } from "react";
import { useAppContext } from "../context/AppContext";
import icons from "../assets/icons/icon";
import { getNotifications, markNotificationAsRead, markAllAsRead } from "../services/notificationService";

const {
  TbMessageCircleFilled,
  FaBell,
  LuPlus,
  PiNewspaperClippingFill,
  CgProfile,
  CgLogOut,
} = icons;

const Navbar = () => {
  const { user, setUser, navigate, isChatOpen, setIsChatOpen, unreadMessageCount } = useAppContext();
  const [showMenu, setShowMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    if (user) {
      fetchNotifications();
    }
  }, [user]);

  const fetchNotifications = async () => {
    try {
      const data = await getNotifications();
      setNotifications(data);
    } catch (error) {
      console.error("Lỗi lấy thông báo:", error);
    }
  };

  const handleNotificationClick = async (notif) => {
    try {
      if (!notif.is_read) {
        await markNotificationAsRead(notif.id);
        // Update local state immediately — no re-fetch needed
        setNotifications((prev) =>
          prev.map((n) => (n.id === notif.id ? { ...n, is_read: true } : n))
        );
      }
      setShowNotifications(false);
      if (notif.target_id) {
        navigate(`/post/${notif.target_id}`);
      }
    } catch (error) {
      console.error("Không thể đánh dấu đã đọc", error);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllAsRead(); // 1 request thay vì N request
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch (error) {
      console.error("Lỗi đánh dấu tất cả đã đọc", error);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    setShowMenu(false);
    navigate("/");
  };

  const unreadNotifCount = notifications.filter((n) => !n.is_read).length;

  return (
    <div className="w-full bg-white/90 backdrop-blur-xl shadow-sm sticky top-0 z-50 border-b border-gray-100 transition-all duration-300">
      <div className="flex items-center justify-between py-3 xl:px-[250px] px-4 md:px-10 mx-auto">
        {/* LEFT SECTION */}
        <div className="flex items-center gap-4 md:gap-6">
          <div
            onClick={() => navigate("/")}
            className="cursor-pointer flex items-center bg-red-50 text-[#dc2626] p-2.5 rounded-xl hover:bg-red-100 transition-colors"
          >
            <svg className="w-6 h-6 md:w-7 md:h-7" fill="currentColor" viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
            <span className="ml-2 font-black text-xl hidden lg:block tracking-tighter uppercase font-sans">CẦM NHẦM PTIT</span>
          </div>

          <div className="flex items-center gap-2 md:gap-3">
            <button
              onClick={() => navigate("/post")}
              className="bg-[#dc2626] hover:bg-[#b91c1c] text-white px-4 md:px-6 py-2.5 rounded-xl text-xs md:text-sm font-medium transition flex items-center shadow-lg shadow-red-500/30"
            >
              <LuPlus className="text-white mr-1 text-base md:text-lg" /> Đăng tin
            </button>
            <button
              onClick={() => navigate("/search")}
              className="bg-white hover:bg-gray-50 border border-gray-200 text-gray-700 px-4 md:px-6 py-2.5 rounded-xl text-xs md:text-sm font-medium transition flex items-center shadow-sm"
            >
              <span className="mr-1.5 md:mr-2">🔍</span> Tìm kiếm
            </button>

          </div>
        </div>

        {/* RIGHT SECTION */}
        <div className="flex items-center gap-4">
          {!user && (
            <button
              onClick={() => navigate("/login")}
              className="bg-[#dc2626] hover:bg-[#b91c1c] text-white px-5 py-2 rounded-full font-medium transition"
            >
              Đăng nhập
            </button>
          )}

          {user && (
            <>
              {/* Message */}
              <button 
                onClick={() => setIsChatOpen(!isChatOpen)}
                className="relative text-3xl hover:scale-110 transition duration-300 text-gray-500 hover:text-[#dc2626]"
              >
                <TbMessageCircleFilled />
                {unreadMessageCount > 0 && (
                  <span className="absolute top-0 right-0 transform translate-x-1 -translate-y-1 bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full border-2 border-white shadow-sm">
                    {unreadMessageCount > 99 ? '99+' : unreadMessageCount}
                  </span>
                )}
              </button>

              {/* Notification */}
              <div className="relative">
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="relative text-3xl hover:scale-110 transition duration-300 text-gray-500 hover:text-[#dc2626]"
                >
                  <FaBell />
                  {unreadNotifCount > 0 && (
                    <span className="absolute top-0 right-0 transform translate-x-1 -translate-y-1 bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full border-2 border-white shadow-sm">
                      {unreadNotifCount > 99 ? '99+' : unreadNotifCount}
                    </span>
                  )}
                </button>

                {/* Notification Dropdown */}
                {showNotifications && (
                  <>
                    <div
                      className="fixed inset-0 z-10"
                      onClick={() => setShowNotifications(false)}
                    ></div>
                    <div className="absolute right-0 mt-4 w-80 bg-white border border-gray-100 rounded-xl shadow-xl py-2 z-20 max-h-[400px] overflow-y-auto animate-in fade-in zoom-in duration-200">
                      <div className="px-4 py-2 border-b border-gray-50 flex justify-between items-center">
                        <h3 className="font-bold text-gray-800">Thông báo</h3>
                        <button onClick={handleMarkAllRead} className="text-[11px] text-red-500 hover:underline">
                          Đánh dấu đã đọc tất cả
                        </button>
                      </div>
                      {notifications.length === 0 ? (
                        <div className="px-4 py-8 text-center text-sm text-gray-500">
                          Chưa có thông báo nào.
                        </div>
                      ) : (
                        notifications.map((notif) => (
                          <div
                            key={notif.id}
                            onClick={() => handleNotificationClick(notif)}
                            className={`px-4 py-3 border-b border-gray-50 cursor-pointer hover:bg-gray-50 transition-colors ${
                              !notif.is_read ? "bg-red-50/50" : ""
                            }`}
                          >
                            <p className={`text-sm ${!notif.is_read ? 'text-gray-900 font-semibold' : 'text-gray-600'}`}>
                              {notif.message}
                            </p>
                            <span className="text-[10px] text-gray-400 mt-1 block">
                              {new Date(notif.created_at).toLocaleString('vi-VN')}
                            </span>
                          </div>
                        ))
                      )}
                    </div>
                  </>
                )}
              </div>



              {/* PROFILE DROPDOWN */}
              <div className="relative group">
                <div
                  onClick={() => setShowMenu(!showMenu)}
                  className="flex items-center gap-2 p-1 px-3 rounded-lg cursor-pointer hover:bg-gray-100 transition-all duration-200"
                >
                  <div className="w-8 h-8 rounded-full bg-orange-500 flex items-center justify-center text-white font-bold text-xs border border-gray-200 overflow-hidden">
                    {user?.avatar ? (
                      <img
                        src={user.avatar}
                        alt="avatar"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      user?.username?.charAt(0).toUpperCase() || "U"
                    )}
                  </div>
                  <div className="hidden md:flex items-center gap-1">
                    <span className="text-[14px] font-medium text-gray-800 max-w-[150px] truncate">
                      {user?.username || "Sinh viên"}
                    </span>
                    <svg
                      className={`w-4 h-4 text-gray-500 transition-transform duration-200 ${showMenu ? "rotate-180" : ""}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M19 9l-7 7-7-7"
                      />
                    </svg>
                  </div>
                </div>

                {showMenu && (
                  <>
                    <div
                      className="fixed inset-0 z-10"
                      onClick={() => setShowMenu(false)}
                    ></div>
                    <div className="absolute right-0 mt-4 w-56 bg-white border border-gray-100 rounded-xl shadow-xl py-2 z-20 animate-in fade-in zoom-in duration-200">
                      <div
                        onClick={() => {
                          navigate("/profile");
                          setShowMenu(false);
                        }}
                        className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
                      >
                        <div className="text-gray-400">
                          <CgProfile className="text-xl" />
                        </div>
                        <span className="text-sm font-normal text-gray-700">
                          Trang cá nhân
                        </span>
                      </div>
                      <div
                        onClick={() => {
                          navigate("/manage-post");
                          setShowMenu(false);
                        }}
                        className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
                      >
                        <div className="text-gray-400">
                          <PiNewspaperClippingFill className="text-xl" />
                        </div>
                        <span className="text-sm font-normal text-gray-700">
                          Quản lý tin đăng
                        </span>
                      </div>
                      <div className="border-t border-gray-100 my-1 mx-2"></div>
                      <div
                        onClick={logout}
                        className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
                      >
                        <div className="text-red-500">
                          <CgLogOut className="text-xl" />
                        </div>
                        <span className="text-sm font-normal text-gray-700">
                          Đăng xuất
                        </span>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Navbar;
