import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { useAppContext } from "../context/AppContext";
import { IoClose, IoSend, IoArrowBack, IoChatbubbleEllipses } from "react-icons/io5";

const ChatBox = () => {
  const { isChatOpen, setIsChatOpen, currentChatReceiver, setCurrentChatReceiver, user, fetchUnreadCount, setUnreadMessageCount } = useAppContext();
  const [view, setView] = useState("list"); // 'list' | 'chat'
  const [conversations, setConversations] = useState([]);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const [loadingConvs, setLoadingConvs] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });

  useEffect(() => {
    if (messages.length) scrollToBottom();
  }, [messages]);

  // When chat opens, load conversation list
  useEffect(() => {
    if (isChatOpen) {
      if (currentChatReceiver) {
        setView("chat");
        fetchChatHistory(currentChatReceiver.id);
        // Pre-fill input with post link if provided
        if (currentChatReceiver.preFill) {
          setInputText(currentChatReceiver.preFill);
        }
      } else {
        setView("list");
        fetchConversations();
      }
    }
  }, [isChatOpen, currentChatReceiver]);

  // Receive real-time messages via WebSocket — only when chat is open
  useEffect(() => {
    const handleNewMessage = (e) => {
      if (!isChatOpen) return; // Don't do anything if chat is closed
      if (view === "chat" && currentChatReceiver) {
        fetchChatHistory(currentChatReceiver.id);
      } else if (view === "list") {
        fetchConversations();
      }
    };
    window.addEventListener("chat:new_message", handleNewMessage);
    return () => window.removeEventListener("chat:new_message", handleNewMessage);
  }, [isChatOpen, view, currentChatReceiver]);

  // Reset state when chat is closed
  useEffect(() => {
    if (!isChatOpen) {
      setView("list");
      setMessages([]);
    }
  }, [isChatOpen]);

  const fetchConversations = async () => {
    try {
      setLoadingConvs(true);
      const token = localStorage.getItem("token");
      const res = await axios.get("http://localhost:8000/messages/conversations", {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConversations(res.data);
    } catch (error) {
      console.error("Lỗi lấy danh sách hội thoại:", error);
    } finally {
      setLoadingConvs(false);
    }
  };

  const fetchChatHistory = async (receiverId) => {
    try {
      const token = localStorage.getItem("token");
      const res = await axios.get(`http://localhost:8000/messages/history/${receiverId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessages(res.data);
    } catch (error) {
      console.error("Lỗi lấy lịch sử chat:", error);
    }
  };

  const markAsRead = async (senderId) => {
    try {
      const token = localStorage.getItem("token");
      const res = await axios.put(`http://localhost:8000/messages/read/${senderId}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      // Update badge count from server's authoritative response
      setUnreadMessageCount(res.data.unread_count ?? 0);
    } catch (error) {
      console.error("Lỗi đánh dấu đã đọc:", error);
    }
  };

  const openChat = async (partner) => {
    setCurrentChatReceiver({ id: partner.id, name: partner.username, avatar: partner.avatar });
    setView("chat");
    fetchChatHistory(partner.id);
    await markAsRead(partner.id);
    // Refresh list so the bold/unread badge updates immediately
    fetchConversations();
  };

  const backToList = () => {
    setView("list");
    setCurrentChatReceiver(null);
    setMessages([]);
    fetchConversations();
  };



  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputText.trim() || !currentChatReceiver) return;
    try {
      const token = localStorage.getItem("token");
      const res = await axios.post(
        "http://localhost:8000/messages/send",
        { receiver_id: currentChatReceiver.id, content: inputText },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessages((prev) => [...prev, res.data]);
      setInputText("");
    } catch (error) {
      console.error("Lỗi gửi tin nhắn:", error);
    }
  };

  if (!isChatOpen) return null;

  return (
    <div className="fixed bottom-0 right-6 md:right-[250px] w-80 h-[480px] bg-white rounded-t-2xl shadow-2xl flex flex-col border border-gray-200 z-[9999] overflow-hidden animate-in fade-in slide-in-from-bottom-12 duration-300">
      {/* ===== HEADER ===== */}
      <div className="bg-gradient-to-r from-red-600 to-rose-500 text-white p-3 py-4 flex justify-between items-center shadow-sm z-10">
        <div className="flex items-center gap-2">
          {view === "chat" && (
            <button onClick={backToList} className="hover:bg-white/20 p-1.5 rounded-full transition">
              <IoArrowBack className="text-lg" />
            </button>
          )}
          {view === "chat" && currentChatReceiver ? (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-white/30 flex items-center justify-center font-bold text-sm shadow-sm overflow-hidden">
                {currentChatReceiver?.avatar
                  ? <img src={currentChatReceiver.avatar} alt="" className="w-full h-full object-cover" />
                  : currentChatReceiver?.name?.charAt(0).toUpperCase()
                }
              </div>
              <div>
                <span className="font-bold text-sm block">{currentChatReceiver?.name}</span>
                <span className="text-[10px] text-red-100 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-green-300 rounded-full animate-pulse" /> Đang hoạt động
                </span>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <IoChatbubbleEllipses className="text-xl" />
              <span className="font-bold text-sm">Tin nhắn</span>
            </div>
          )}
        </div>
        <button onClick={() => setIsChatOpen(false)} className="hover:bg-white/20 w-8 h-8 rounded-full flex items-center justify-center transition">
          <IoClose className="text-xl" />
        </button>
      </div>

      {/* ===== VIEW: CONVERSATIONS LIST ===== */}
      {view === "list" && (
        <div className="flex-1 overflow-y-auto bg-white">
          {loadingConvs && (
            <div className="flex justify-center py-10">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-red-500" />
            </div>
          )}
          {!loadingConvs && conversations.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-gray-400 gap-3">
              <IoChatbubbleEllipses className="text-5xl text-gray-200" />
              <p className="text-sm text-center px-6">Chưa có tin nhắn nào. Hãy nhắn tin với ai đó từ trang bài đăng!</p>
            </div>
          )}
          {conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => openChat(conv)}
              className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition border-b border-gray-50 text-left"
            >
              <div className="w-11 h-11 rounded-full bg-gradient-to-br from-red-500 to-rose-400 text-white flex items-center justify-center font-bold text-sm flex-shrink-0 shadow-sm overflow-hidden">
                {conv.avatar
                  ? <img src={conv.avatar} alt="" className="w-full h-full object-cover" />
                  : conv.username?.charAt(0).toUpperCase()
                }
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-center">
                  <span className={`text-sm text-gray-800 ${conv.unread_count > 0 ? 'font-extrabold' : 'font-semibold'}`}>{conv.username}</span>
                  <div className="flex items-center gap-1.5">
                    {conv.unread_count > 0 && (
                      <span className="bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">{conv.unread_count}</span>
                    )}
                    <span className="text-[10px] text-gray-400">
                      {conv.last_message_time
                        ? new Date(conv.last_message_time).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
                        : ""}
                    </span>
                  </div>
                </div>
                <p className={`text-xs truncate ${conv.unread_count > 0 ? 'text-gray-800 font-bold' : 'text-gray-500'}`}>
                  {conv.is_mine ? "Bạn: " : ""}{conv.last_message}
                </p>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* ===== VIEW: CHAT THREAD ===== */}
      {view === "chat" && (
        <>
          <div className="flex-1 bg-[#f0f2f5] overflow-y-auto p-4 flex flex-col gap-3">
            {messages.length === 0 ? (
              <div className="m-auto flex flex-col items-center gap-2 text-gray-400">
                <IoChatbubbleEllipses className="text-4xl text-gray-200" />
                <p className="text-xs italic text-center">Click vào tin nhắn để xem lịch sử trò chuyện</p>
              </div>
            ) : (
              messages.map((msg, idx) => {
                const isMe = msg.sender_id === user?.id;
                return (
                  <div
                    key={idx}
                    className={`max-w-[80%] px-4 py-2.5 text-sm break-words ${
                      isMe
                        ? "bg-red-500 text-white self-end rounded-2xl rounded-br-none shadow-sm"
                        : "bg-white border border-gray-200 text-gray-800 self-start rounded-2xl rounded-bl-none shadow-sm"
                    }`}
                  >
                    {msg.content}
                  </div>
                );
              })
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSendMessage} className="p-3 bg-white border-t border-gray-100 flex items-center gap-2">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Nhập tin nhắn..."
              className="flex-1 bg-[#f0f2f5] rounded-full px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-red-500 transition-all font-medium text-gray-700 placeholder-gray-400"
            />
            <button
              type="submit"
              disabled={!inputText.trim()}
              className="text-white bg-red-500 hover:bg-red-600 disabled:bg-gray-200 p-2.5 rounded-full transition-all"
            >
              <IoSend className="text-lg relative left-[1px]" />
            </button>
          </form>
        </>
      )}
    </div>
  );
};

export default ChatBox;
