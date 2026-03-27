import { createContext, useContext, useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export const AppContext = createContext();

export const AppContextProvider = ({ children }) => {
  const navigate = useNavigate();

  // Khởi tạo user từ localStorage nếu có, nếu không thì để null
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem("user");
    return savedUser ? JSON.parse(savedUser) : null;
  });

  const [showUserLogin, setShowUserLogin] = useState(false);

  // ===== TRẠNG THÁI CHO HỆ THỐNG MESSAGING =====
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [currentChatReceiver, setCurrentChatReceiver] = useState(null);
  const [unreadMessageCount, setUnreadMessageCount] = useState(0);
  
  // Ref giữ WebSocket instance (để close khi logout)
  const wsRef = useRef(null);

  // Theo dõi sự thay đổi của user
  useEffect(() => {
    // Luôn đóng chat khi user thay đổi (login/logout)
    setIsChatOpen(false);
    setCurrentChatReceiver(null);

    if (!user) {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      return;
    }

    // Khi có user, Fetch số đếm thông báo đỏ
    fetchUnreadCount();

    // Mở kết nối WebSocket ngay lập tức
    const ws = new WebSocket(`ws://localhost:8000/ws/${user.id}`);
    
    ws.onopen = () => console.log("WebSocket Chat System Connected!");
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "new_message") {
          // Tin nhắn đến -> Render lại số đỏ
          fetchUnreadCount();
          // Bắn ra event báo hệ thống có tin (ChatBox tự bắt lấy để load UI)
          window.dispatchEvent(new CustomEvent("chat:new_message", { detail: data }));
        }
      } catch (error) {
        console.error("Lỗi phân tích WebSocket Message", error);
      }
    };
    
    ws.onclose = () => console.log("WebSocket Disconnected");
    
    wsRef.current = ws;

    return () => {
      if (ws) ws.close();
    };
  }, [user]);

  const fetchUnreadCount = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;
      const res = await axios.get("http://localhost:8000/messages/unread-count", {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUnreadMessageCount(res.data.unread_count || 0);
    } catch (error) {
      console.log("Không thể fetch unread count", error);
    }
  };

  const openChatWithReceiver = (receiverObj, preFillMessage = "") => {
    if (!user) {
      navigate('/login');
      return;
    }
    const receiverId = receiverObj.id;
    // Chặn nhắn tin với chính mình
    if (!receiverId || receiverId === user.id) {
      alert("Đây là bài đăng của bạn!");
      return;
    }
    const receiver = {
      id: receiverId,
      name: receiverObj.name || receiverObj.username,
      avatar: receiverObj.avatar,
      preFill: preFillMessage
    };
    setCurrentChatReceiver(receiver);
    setIsChatOpen(true);
  };

  const value = {
    navigate,
    user,
    setUser,
    showUserLogin,
    setShowUserLogin,
    
    // Xuất state liên quan Chat
    isChatOpen, setIsChatOpen,
    currentChatReceiver, setCurrentChatReceiver,
    unreadMessageCount, setUnreadMessageCount,
    fetchUnreadCount, openChatWithReceiver
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export const useAppContext = () => {
  return useContext(AppContext);
};
