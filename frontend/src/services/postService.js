import api from "./api";

export const getAllPosts = async () => {
  const response = await api.get("/posts");
  return response.data;
};

export const getPostById = async (id) => {
  const response = await api.get(`/posts/${id}`);
  return response.data;
};

export const getMyPosts = async () => {
  const response = await api.get("/posts/my");
  return response.data;
};

export const createPost = async (formData) => {
  // formData là FormData object (có chứa file ảnh)
  // Không set Content-Type thủ công — axios tự thêm boundary cho multipart
  const response = await api.post("/posts", formData);
  return response.data;
};

export const deletePost = async (postId) => {
  const response = await api.delete(`/posts/${postId}`);
  return response.data;
};

export const resolvePost = async (postId) => {
  const response = await api.put(`/posts/${postId}/resolve`);
  return response.data;
};

export const reportPost = async (postId, reason) => {
  const response = await api.post(`/reports`, { post_id: postId, reason });
  return response.data;
};

