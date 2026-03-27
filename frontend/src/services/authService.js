import api from "./api";

export const register = async (userData) => {
  // userData bao gồm { username, email, password }
  const response = await api.post("/auth/register", userData);
  return response.data;
};

export const login = async (loginData) => {
  // loginData bao gồm { email, password }
  const response = await api.post("/auth/login", loginData);

  // Nếu thành công, Backend của bạn trả về { access_token, user }
  if (response.data.access_token) {
    localStorage.setItem("token", response.data.access_token);
    localStorage.setItem("user", JSON.stringify(response.data.user));
  }

  return response.data;
};

export const logout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
};
