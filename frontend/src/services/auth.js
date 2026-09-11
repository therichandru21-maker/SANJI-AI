import axios from "axios";

const API_URL = "https://sanji-ai-g2um.onrender.com";

export const loginWithGoogle = async (credential) => {
  if (!credential) {
    throw new Error("Google credential is missing.");
  }

  const response = await axios.post(
    `${API_URL}/auth/google`,
    { credential }
  );

  const data = response.data;

  if (!data?.access_token) {
    throw new Error(
      "Authentication failed. No access token received."
    );
  }

  localStorage.setItem(
    "sanji_access_token",
    data.access_token
  );

  if (data.user) {
    localStorage.setItem(
      "sanji_user",
      JSON.stringify(data.user)
    );
  }

  return data;
};

export const getStoredUser = () => {
  try {
    const user = localStorage.getItem("sanji_user");

    if (!user) {
      return null;
    }

    return JSON.parse(user);
  } catch (error) {
    console.error(
      "Failed to read stored user:",
      error
    );

    localStorage.removeItem("sanji_user");

    return null;
  }
};

export const getAccessToken = () => {
  return localStorage.getItem(
    "sanji_access_token"
  );
};

export const getAuthHeaders = () => {
  const token = getAccessToken();

  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
};

export const isAuthenticated = () => {
  return Boolean(getAccessToken());
};

export const verifySession = async () => {
  const token = getAccessToken();

  if (!token) {
    return null;
  }

  try {
    const response = await axios.get(
      `${API_URL}/auth/me`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    const user = response.data?.user;

    if (user) {
      localStorage.setItem(
        "sanji_user",
        JSON.stringify(user)
      );
    }

    return user || null;
  } catch (error) {
    console.error(
      "Session verification failed:",
      error
    );

    logout();

    return null;
  }
};

export const logout = () => {
  localStorage.removeItem(
    "sanji_access_token"
  );

  localStorage.removeItem(
    "sanji_user"
  );
};

export const getGoogleClientId = () => {
  return import.meta.env.VITE_GOOGLE_CLIENT_ID;
};