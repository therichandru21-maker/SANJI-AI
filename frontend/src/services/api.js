import axios from "axios";


const API_URL = "http://127.0.0.1:8000";


// ---------------------------------------------------------
// Authentication Header
// ---------------------------------------------------------

const getAuthHeaders = () => {

  const token = localStorage.getItem(
    "sanji_access_token"
  );

  if (!token) {
    throw new Error("Not authenticated");
  }

  return {
    Authorization: `Bearer ${token}`,
  };
};


// ---------------------------------------------------------
// Run SANJI Agent
// ---------------------------------------------------------

export const runAgent = async (
  goal,
  conversation = [],
  conversationId = null
) => {

  try {

    const response = await axios.post(
      `${API_URL}/agent/run`,
      {
        goal,
        conversation,
        conversation_id: conversationId,
      },
      {
        headers: getAuthHeaders(),
      }
    );

    return response.data;

  } catch (error) {

    console.error(
      "SANJI AI request failed:",
      error
    );

    if (
      error.response?.status === 401
    ) {

      throw new Error(
        "Session expired. Please login again."
      );
    }

    throw new Error(
      error.response?.data?.detail ||
      error.response?.data?.error ||
      error.message ||
      "Failed to communicate with SANJI AI."
    );
  }
};


// ---------------------------------------------------------
// Get All Conversations
// ---------------------------------------------------------

export const getConversations = async () => {

  try {

    const response = await axios.get(
      `${API_URL}/conversations`,
      {
        headers: getAuthHeaders(),
      }
    );

    return response.data;

  } catch (error) {

    console.error(
      "Failed to load conversations:",
      error
    );

    throw new Error(
      error.response?.data?.detail ||
      error.message ||
      "Failed to load conversations."
    );
  }
};


// ---------------------------------------------------------
// Get One Conversation
// ---------------------------------------------------------

export const getConversation = async (
  conversationId
) => {

  try {

    const response = await axios.get(
      `${API_URL}/conversations/${conversationId}`,
      {
        headers: getAuthHeaders(),
      }
    );

    return response.data;

  } catch (error) {

    console.error(
      "Failed to load conversation:",
      error
    );

    throw new Error(
      error.response?.data?.detail ||
      error.message ||
      "Failed to load conversation."
    );
  }
};


// ---------------------------------------------------------
// Delete Conversation
// ---------------------------------------------------------

export const deleteConversation = async (
  conversationId
) => {

  try {

    const response = await axios.delete(
      `${API_URL}/conversations/${conversationId}`,
      {
        headers: getAuthHeaders(),
      }
    );

    return response.data;

  } catch (error) {

    console.error(
      "Failed to delete conversation:",
      error
    );

    throw new Error(
      error.response?.data?.detail ||
      error.message ||
      "Failed to delete conversation."
    );
  }
};