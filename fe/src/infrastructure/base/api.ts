import { getToken, saveTokens } from "@store/localStorage";
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = getToken("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const originalRequest = err.config;
    if (err.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = getToken("refresh_token");
      try {
        const res = await axios.post("http://localhost:8000/api/v1/auth/refresh", { token: refreshToken });
        const newAccessToken = res.data.access_token;
        saveTokens(newAccessToken, refreshToken);

        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return axios(originalRequest);
      } catch (refreshError) {
        localStorage.clear();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(err);
  }
);

export default api;
