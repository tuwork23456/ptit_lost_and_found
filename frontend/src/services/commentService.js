import api from "./api";

export const getComments = async (postId) => {
  const response = await api.get(`/comments/post/${postId}`);
  return response.data;
};

export const createComment = async (postId, content) => {
  // user_id không cần gửi lên nữa — backend tự lấy từ JWT token (Authorization header)
  const response = await api.post(`/comments/`, {
    content,
    post_id: parseInt(postId),
  });
  return response.data;
};
