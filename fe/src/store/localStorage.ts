// localStorage.ts
export const STATE_KEY = "APP_STATE";

export const getToken = (key: "access_token" | "refresh_token") => {
  try {
    const state = JSON.parse(localStorage.getItem(STATE_KEY) || "{}");
    return state?.user?.[key] || "";
  } catch {
    return "";
  }
};

export const saveTokens = (access_token: string, refresh_token: string) => {
  const state = JSON.parse(localStorage.getItem(STATE_KEY) || "{}");
  state.user = { access_token, refresh_token };
  localStorage.setItem(STATE_KEY, JSON.stringify(state));
};
