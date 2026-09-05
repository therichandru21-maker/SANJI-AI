import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

const GOOGLE_CLIENT_ID =
  import.meta.env.VITE_GOOGLE_CLIENT_ID;


/* =========================================================
   GOOGLE LOGIN
========================================================= */

export const loginWithGoogle = async (credential) => {
  if (!credential) {
    throw new Error("Google credential is missing.");
  }

  const response = await axios.post(
    `${API_URL}/auth/google`,
    {
      credential,
    }
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


/* =========================================================
   GET STORED USER
========================================================= */

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


/* =========================================================
   GET ACCESS TOKEN
========================================================= */

export const getAccessToken = () => {
  return localStorage.getItem(
    "sanji_access_token"
  );
};


/* =========================================================
   AUTH HEADERS
========================================================= */

export const getAuthHeaders = () => {
  const token = getAccessToken();

  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
};


/* =========================================================
   CHECK LOGIN
========================================================= */

export const isAuthenticated = () => {
  return Boolean(getAccessToken());
};


/* =========================================================
   VERIFY SESSION
========================================================= */

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


/* =========================================================
   LOGOUT
========================================================= */

export const logout = () => {
  localStorage.removeItem(
    "sanji_access_token"
  );

  localStorage.removeItem(
    "sanji_user"
  );
};


/* =========================================================
   GOOGLE CLIENT ID
========================================================= */

export const getGoogleClientId = () => {
  return GOOGLE_CLIENT_ID;
};