import { useEffect, useRef, useState } from "react";

import {
  ArrowUp,
  Bot,
  Check,
  ChefHat,
  Copy,
  Menu,
  Monitor,
  Moon,
  Plus,
  Sun,
  User,
  LogOut,
  Mail,
  Trash2,
} from "lucide-react";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";

import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

import {
  runAgent,
  getConversations,
  getConversation,
  deleteConversation,
} from "./services/api";

import {
  loginWithGoogle,
  getStoredUser,
  logout,
} from "./services/auth";

import "./App.css";


function App() {
  // =========================================================
  // AUTH
  // =========================================================

  const [user, setUser] = useState(() => getStoredUser());
  const [authLoading, setAuthLoading] = useState(true);

  // =========================================================
  // CHAT
  // =========================================================

  const [goal, setGoal] = useState("");
  const [messages, setMessages] = useState([]);
  const [running, setRunning] = useState(false);

  const [conversationId, setConversationId] = useState(null);

  // =========================================================
  // CONVERSATION HISTORY
  // =========================================================

  const [conversations, setConversations] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // =========================================================
  // UI
  // =========================================================

  const [sidebarOpen, setSidebarOpen] = useState(true);

  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("sanji-theme") || "system";
  });

  const [copiedIndex, setCopiedIndex] = useState(null);

  // =========================================================
  // REFS
  // =========================================================

  const textareaRef = useRef(null);
  const messagesEndRef = useRef(null);


  // =========================================================
  // AUTH INITIALIZATION
  // =========================================================

  useEffect(() => {
    let mounted = true;

    const initializeAuth = () => {
      if (mounted) {
        setAuthLoading(false);
      }
    };

    initializeAuth();

    return () => {
      mounted = false;
    };
  }, []);


  // =========================================================
  // THEME
  // =========================================================

  useEffect(() => {
    document.documentElement.setAttribute(
      "data-theme",
      theme
    );

    localStorage.setItem(
      "sanji-theme",
      theme
    );
  }, [theme]);


  // =========================================================
  // AUTO SCROLL
  // =========================================================

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, running]);


  // =========================================================
  // LOAD CONVERSATIONS
  // =========================================================

  const loadConversations = async () => {
    if (!user) {
      return;
    }

    setHistoryLoading(true);

    try {
      const data = await getConversations();

      setConversations(
        Array.isArray(data?.conversations)
          ? data.conversations
          : []
      );
    } catch (error) {
      console.error(
        "Failed to load conversation history:",
        error
      );
    } finally {
      setHistoryLoading(false);
    }
  };


  // =========================================================
  // LOAD HISTORY WHEN USER LOGS IN
  // =========================================================

  useEffect(() => {
    if (!user) {
      setConversations([]);
      return;
    }

    loadConversations();
  }, [user]);


  // =========================================================
  // GOOGLE LOGIN
  // =========================================================

  const handleGoogleLogin = async (credential) => {
    setAuthLoading(true);

    try {
      const data = await loginWithGoogle(
        credential
      );

      setUser(data.user);
    } catch (error) {
      console.error(
        "Google login failed:",
        error
      );

      alert(
        error?.response?.data?.detail ||
        "Google login failed. Please try again."
      );
    } finally {
      setAuthLoading(false);
    }
  };


  // =========================================================
  // LOGOUT
  // =========================================================

  const handleLogout = () => {
    logout();

    setUser(null);
    setMessages([]);
    setGoal("");
    setConversationId(null);
    setConversations([]);
  };


  // =========================================================
  // NEW CHAT
  // =========================================================

  const handleNewChat = () => {
    setMessages([]);
    setGoal("");
    setConversationId(null);

    setTimeout(() => {
      textareaRef.current?.focus();
    }, 100);
  };


  // =========================================================
  // OPEN EXISTING CONVERSATION
  // =========================================================

  const handleOpenConversation = async (
    id
  ) => {
    if (running) {
      return;
    }

    try {
      setHistoryLoading(true);

      const data = await getConversation(id);

      const loadedMessages = Array.isArray(
        data?.messages
      )
        ? data.messages
            .filter(
              (message) =>
                message.role === "user" ||
                message.role === "assistant"
            )
            .map((message) => ({
              role: message.role,
              content: message.content,
            }))
        : [];

      setMessages(loadedMessages);

      setConversationId(
        data?.conversation?.id || id
      );

      setGoal("");

      setTimeout(() => {
        textareaRef.current?.focus();
      }, 100);
    } catch (error) {
      console.error(
        "Failed to open conversation:",
        error
      );

      alert(
        error?.message ||
        "Failed to load conversation."
      );
    } finally {
      setHistoryLoading(false);
    }
  };


  // =========================================================
  // DELETE CONVERSATION
  // =========================================================

  const handleDeleteConversation = async (
    event,
    id
  ) => {
    event.stopPropagation();

    if (running) {
      return;
    }

    const confirmed = window.confirm(
      "Delete this conversation?"
    );

    if (!confirmed) {
      return;
    }

    try {
      await deleteConversation(id);

      setConversations((previous) =>
        previous.filter(
          (conversation) =>
            conversation.id !== id
        )
      );

      if (conversationId === id) {
        setMessages([]);
        setGoal("");
        setConversationId(null);
      }
    } catch (error) {
      console.error(
        "Failed to delete conversation:",
        error
      );

      alert(
        error?.message ||
        "Failed to delete conversation."
      );
    }
  };


  // =========================================================
  // COPY
  // =========================================================

  const handleCopy = async (
    text,
    index
  ) => {
    try {
      await navigator.clipboard.writeText(
        text
      );

      setCopiedIndex(index);

      setTimeout(() => {
        setCopiedIndex(null);
      }, 1500);
    } catch (error) {
      console.error(
        "Clipboard unavailable:",
        error
      );
    }
  };


  // =========================================================
  // RUN AGENT
  // =========================================================

  const handleRunAgent = async () => {
    const trimmedGoal = goal.trim();

    if (!trimmedGoal || running) {
      return;
    }

    const previousConversation =
      messages.map((message) => ({
        role: message.role,
        content: message.content,
      }));

    // Immediately show user message
    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: trimmedGoal,
      },
    ]);

    setGoal("");
    setRunning(true);

    try {
      const data = await runAgent(
        trimmedGoal,
        previousConversation,
        conversationId
      );

      // Save returned conversation ID
      if (data?.conversation_id) {
        setConversationId(
          data.conversation_id
        );
      }

      const finalAnswer =
        data?.final_answer ||
        data?.final_response?.human_summary ||
        data?.answer ||
        "I completed the request, but I couldn't generate a readable response.";

      // Show assistant response
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: finalAnswer,
          verified:
            data?.verification?.verified === true,
        },
      ]);

      // Refresh sidebar history
      await loadConversations();
    } catch (error) {
      console.error(error);

      let errorMessage =
        "Something went wrong while processing your request.";

      if (error?.response?.data?.detail) {
        errorMessage =
          error.response.data.detail;
      } else if (error?.message) {
        errorMessage = error.message;
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "Sorry, I couldn't complete that request.\n\n" +
            errorMessage,
          error: true,
        },
      ]);
    } finally {
      setRunning(false);

      setTimeout(() => {
        textareaRef.current?.focus();
      }, 100);
    }
  };


  // =========================================================
  // KEYBOARD
  // =========================================================

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      handleRunAgent();
    }
  };


  // =========================================================
  // SUGGESTION
  // =========================================================

  const handleSuggestion = (text) => {
    setGoal(text);

    setTimeout(() => {
      textareaRef.current?.focus();
    }, 50);
  };


  // =========================================================
  // AUTH SCREEN
  // =========================================================

  if (authLoading) {
    return <AuthLoading />;
  }

  if (!user) {
    return (
      <LoginScreen
        onLogin={handleGoogleLogin}
      />
    );
  }


  // =========================================================
  // SPLIT HISTORY
  // =========================================================

  const recentConversations =
    conversations.slice(0, 5);

  const oldConversations =
    conversations.slice(5);


  // =========================================================
  // MAIN UI
  // =========================================================

  return (
    <div className="sanji-app">

      {/* =====================================================
          SIDEBAR
      ===================================================== */}

      <aside
        className={`sidebar ${
          sidebarOpen
            ? "sidebar-open"
            : "sidebar-closed"
        }`}
      >

        <div className="sidebar-content">

          {/* NEW CHAT */}

          <button
            className="new-chat"
            onClick={handleNewChat}
          >
            <Plus size={18} />

            <span>
              New chat
            </span>
          </button>


          {/* =================================================
              RECENT
          ================================================= */}

          <div className="sidebar-group">

            <div className="sidebar-title">
              Recent
            </div>

            {historyLoading &&
            conversations.length === 0 ? (

              <div className="empty-history">
                Loading conversations...
              </div>

            ) : recentConversations.length >
              0 ? (

              recentConversations.map(
                (conversation) => (
                  <button
                    key={conversation.id}
                    className={`conversation-item ${
                      conversationId ===
                      conversation.id
                        ? "conversation-active"
                        : ""
                    }`}
                    onClick={() =>
                      handleOpenConversation(
                        conversation.id
                      )
                    }
                    title={
                      conversation.title
                    }
                  >
                    <Bot size={15} />

                    <span>
                      {conversation.title}
                    </span>

                    <button
                      className="conversation-delete"
                      onClick={(event) =>
                        handleDeleteConversation(
                          event,
                          conversation.id
                        )
                      }
                      aria-label="Delete conversation"
                      title="Delete"
                    >
                      <Trash2 size={14} />
                    </button>
                  </button>
                )
              )

            ) : (

              <div className="empty-history">
                No conversations yet
              </div>

            )}

          </div>


          {/* =================================================
              OLD CONVERSATIONS
          ================================================= */}

          {oldConversations.length > 0 && (

            <div className="sidebar-group">

              <div className="sidebar-title">
                Old Conversations
              </div>

              {oldConversations.map(
                (conversation) => (
                  <button
                    key={conversation.id}
                    className={`conversation-item ${
                      conversationId ===
                      conversation.id
                        ? "conversation-active"
                        : ""
                    }`}
                    onClick={() =>
                      handleOpenConversation(
                        conversation.id
                      )
                    }
                    title={
                      conversation.title
                    }
                  >
                    <Bot size={15} />

                    <span>
                      {conversation.title}
                    </span>

                    <button
                      className="conversation-delete"
                      onClick={(event) =>
                        handleDeleteConversation(
                          event,
                          conversation.id
                        )
                      }
                      aria-label="Delete conversation"
                      title="Delete"
                    >
                      <Trash2 size={14} />
                    </button>
                  </button>
                )
              )}

            </div>

          )}

        </div>


        {/* =================================================
            SIDEBAR PROFILE
        ================================================= */}

        <div className="sidebar-footer">

          <div className="profile-section">

            {user?.picture ? (

              <img
                src={user.picture}
                alt={
                  user?.name ||
                  "Profile"
                }
                className="sidebar-profile-picture"
              />

            ) : (

              <div className="sidebar-profile-picture profile-fallback">
                {(
                  user?.name ||
                  user?.email ||
                  "U"
                )
                  .charAt(0)
                  .toUpperCase()}
              </div>

            )}


            <div className="profile-info">

              <strong>
                {user?.name || "User"}
              </strong>

              <span>
                {user?.email || ""}
              </span>

            </div>


            <button
              className="profile-logout"
              onClick={handleLogout}
              aria-label="Logout"
              title="Logout"
            >
              <LogOut size={17} />
            </button>

          </div>

        </div>

      </aside>


      {/* =====================================================
          MAIN
      ===================================================== */}

      <main className="main">

        {/* ===================================================
            HEADER
        =================================================== */}

        <header className="header">

          <div className="header-left">

            <button
              className="header-button menu-button"
              onClick={() =>
                setSidebarOpen(
                  (value) => !value
                )
              }
              aria-label="Toggle sidebar"
            >
              <Menu size={20} />
            </button>


            {/* SANJI BRAND */}

            <div className="brand">

              <div className="brand-icon">

                <ChefHat
                  size={22}
                  strokeWidth={1.8}
                />

              </div>

              <div>

                <strong>
                  SANJI AI
                </strong>

                <span>
                  AI Assistant
                </span>

              </div>

            </div>

          </div>


          {/* =================================================
              HEADER ACTIONS
          ================================================= */}

          <div className="header-actions">

            <button
              className="header-button logout-button"
              onClick={handleLogout}
              aria-label="Logout"
              title="Logout"
            >
              <LogOut size={17} />
            </button>


            <ThemeSelector
              theme={theme}
              setTheme={setTheme}
            />

          </div>

        </header>


        {/* ===================================================
            CHAT
        =================================================== */}

        <div className="chat-container">

          <div className="conversation">

            {messages.length === 0 ? (

              <Welcome
                onSuggestion={
                  handleSuggestion
                }
              />

            ) : (

              messages.map(
                (message, index) => (
                  <Message
                    key={index}
                    message={message}
                    index={index}
                    copiedIndex={
                      copiedIndex
                    }
                    onCopy={
                      handleCopy
                    }
                  />
                )
              )

            )}

            {running && <Typing />}

            <div
              ref={messagesEndRef}
            />

          </div>

        </div>


        {/* ===================================================
            COMPOSER
        =================================================== */}

        <div className="composer-area">

          <div className="composer-wrapper">

            <div className="composer">

              <textarea
                ref={textareaRef}
                value={goal}
                onChange={(event) =>
                  setGoal(
                    event.target.value
                  )
                }
                onKeyDown={
                  handleKeyDown
                }
                placeholder="Message SANJI AI..."
                rows={1}
                disabled={running}
              />

              <button
                className={`send-button ${
                  goal.trim() &&
                  !running
                    ? "active"
                    : ""
                }`}
                onClick={
                  handleRunAgent
                }
                disabled={
                  !goal.trim() ||
                  running
                }
                aria-label="Send message"
              >
                <ArrowUp size={18} />
              </button>

            </div>

            <p className="composer-info">
              SANJI can explain, create,
              calculate, research and code.
            </p>

          </div>

        </div>

      </main>

    </div>
  );
}


/* =========================================================
   AUTH LOADING
========================================================= */

function AuthLoading() {
  return (
    <div style={authStyles.page}>

      <div style={authStyles.card}>

        <div style={authStyles.icon}>
          <ChefHat
            size={28}
            strokeWidth={1.8}
          />
        </div>

        <strong style={authStyles.title}>
          SANJI AI
        </strong>

        <span style={authStyles.subtitle}>
          Loading your workspace...
        </span>

      </div>

    </div>
  );
}


/* =========================================================
   LOGIN SCREEN
========================================================= */

function LoginScreen({
  onLogin,
}) {

  const googleButtonRef =
    useRef(null);

  const [error, setError] =
    useState("");


  useEffect(() => {

    const clientId =
      import.meta.env
        .VITE_GOOGLE_CLIENT_ID;

    if (!clientId) {

      setError(
        "Google Client ID is missing. Add VITE_GOOGLE_CLIENT_ID to frontend/.env."
      );

      return undefined;
    }


    const renderButton = () => {

      if (
        !window.google ||
        !googleButtonRef.current
      ) {
        return false;
      }


      googleButtonRef.current.innerHTML =
        "";


      window.google.accounts.id.initialize(
        {
          client_id: clientId,

          callback: (response) => {

            if (
              !response?.credential
            ) {

              setError(
                "Google did not return a valid credential."
              );

              return;
            }

            onLogin(
              response.credential
            );
          },
        }
      );


      window.google.accounts.id.renderButton(
        googleButtonRef.current,
        {
          theme: "outline",
          size: "large",
          width: 320,
          text: "continue_with",
          shape: "rectangular",
          logo_alignment: "left",
        }
      );

      return true;
    };


    if (renderButton()) {
      return undefined;
    }


    const existingScript =
      document.querySelector(
        'script[src="https://accounts.google.com/gsi/client"]'
      );


    if (existingScript) {

      existingScript.addEventListener(
        "load",
        renderButton
      );

      return () =>
        existingScript.removeEventListener(
          "load",
          renderButton
        );
    }


    const script =
      document.createElement(
        "script"
      );

    script.src =
      "https://accounts.google.com/gsi/client";

    script.async = true;
    script.defer = true;
    script.onload =
      renderButton;


    script.onerror = () => {

      setError(
        "Unable to load Google Sign-In. Check your internet connection."
      );
    };


    document.head.appendChild(
      script
    );


    return () => {
      script.onload = null;
    };

  }, [onLogin]);


  return (
    <div style={authStyles.page}>

      <div
        style={
          authStyles.backgroundGlow
        }
      />

      <div style={authStyles.card}>

        <div style={authStyles.icon}>

          <ChefHat
            size={30}
            strokeWidth={1.8}
          />

        </div>


        <div style={authStyles.brand}>
          SANJI AI
        </div>


        <h1 style={authStyles.heading}>
          Welcome back
        </h1>


        <p style={authStyles.subtitle}>
          Sign in to continue to your
          private AI workspace.
        </p>


        <div
          style={
            authStyles.googleArea
          }
        >
          <div
            ref={googleButtonRef}
          />
        </div>


        {error && (

          <div style={authStyles.error}>

            <Mail size={15} />

            <span>
              {error}
            </span>

          </div>

        )}


        <p style={authStyles.privacy}>
          Your chats and activity are
          associated with your account.
        </p>

      </div>

    </div>
  );
}


/* =========================================================
   AUTH STYLES
========================================================= */

const authStyles = {

  page: {
    minHeight: "100vh",
    width: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#08090d",
    color: "#f5f7fb",
    position: "relative",
    overflow: "hidden",
    fontFamily:
      "Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },

  backgroundGlow: {
    position: "absolute",
    width: 420,
    height: 420,
    borderRadius: "50%",
    background:
      "rgba(255, 255, 255, 0.045)",
    filter: "blur(80px)",
  },

  card: {
    width:
      "min(420px, calc(100% - 32px))",
    boxSizing: "border-box",
    padding: "42px 34px 30px",
    border:
      "1px solid rgba(255,255,255,0.09)",
    borderRadius: 24,
    background:
      "rgba(17,18,24,0.88)",
    backdropFilter: "blur(18px)",
    boxShadow:
      "0 30px 90px rgba(0,0,0,0.42)",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    position: "relative",
    zIndex: 1,
  },

  icon: {
    width: 58,
    height: 58,
    borderRadius: 18,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    border:
      "1px solid rgba(255,255,255,0.11)",
    background:
      "rgba(255,255,255,0.055)",
    marginBottom: 18,
  },

  brand: {
    fontSize: 13,
    fontWeight: 700,
    letterSpacing: "0.16em",
    opacity: 0.7,
    marginBottom: 10,
  },

  heading: {
    fontSize: 30,
    lineHeight: 1.15,
    margin: 0,
    letterSpacing: "-0.03em",
  },

  title: {
    fontSize: 18,
    letterSpacing: "0.08em",
  },

  subtitle: {
    fontSize: 14,
    lineHeight: 1.6,
    opacity: 0.62,
    textAlign: "center",
    marginTop: 10,
    maxWidth: 320,
  },

  googleArea: {
    marginTop: 28,
    minHeight: 44,
    display: "flex",
    justifyContent: "center",
    width: "100%",
  },

  error: {
    marginTop: 18,
    padding: "10px 12px",
    borderRadius: 12,
    background:
      "rgba(255,80,80,0.08)",
    border:
      "1px solid rgba(255,80,80,0.18)",
    color: "#ffb4b4",
    fontSize: 12,
    lineHeight: 1.45,
    display: "flex",
    gap: 8,
    alignItems: "flex-start",
  },

  privacy: {
    margin: "24px 0 0",
    fontSize: 11,
    lineHeight: 1.5,
    textAlign: "center",
    opacity: 0.42,
  },
};


/* =========================================================
   THEME SELECTOR
========================================================= */

function ThemeSelector({
  theme,
  setTheme,
}) {

  const [open, setOpen] =
    useState(false);


  const options = [

    {
      id: "system",
      label: "System",
      icon: Monitor,
    },

    {
      id: "light",
      label: "Light",
      icon: Sun,
    },

    {
      id: "dark",
      label: "Dark",
      icon: Moon,
    },

  ];


  const current =
    options.find(
      (option) =>
        option.id === theme
    ) || options[0];


  const CurrentIcon =
    current.icon;


  return (

    <div className="theme-wrapper">

      <button
        className="theme-button"
        onClick={() =>
          setOpen(
            (value) => !value
          )
        }
      >

        <CurrentIcon size={17} />

        <span>
          {current.label}
        </span>

      </button>


      {open && (

        <>

          <div
            className="theme-overlay"
            onClick={() =>
              setOpen(false)
            }
          />


          <div className="theme-menu">

            {options.map(
              (option) => {

                const Icon =
                  option.icon;

                return (

                  <button
                    key={option.id}
                    className={`theme-option ${
                      theme ===
                      option.id
                        ? "selected"
                        : ""
                    }`}
                    onClick={() => {

                      setTheme(
                        option.id
                      );

                      setOpen(false);
                    }}
                  >

                    <Icon size={16} />

                    <span>
                      {option.label}
                    </span>


                    {theme ===
                      option.id && (

                      <Check
                        size={15}
                        className="theme-check"
                      />

                    )}

                  </button>

                );
              }
            )}

          </div>

        </>

      )}

    </div>
  );
}


/* =========================================================
   WELCOME
========================================================= */

function Welcome({
  onSuggestion,
}) {

  return (

    <div className="welcome">

      <div className="welcome-icon">

        <ChefHat
          size={29}
          strokeWidth={1.8}
        />

      </div>


      <h1>
        How can I help you?
      </h1>


      <p>
        Ask anything. SANJI can
        explain, create, calculate,
        research and code.
      </p>


      <div className="suggestions">

        <button
          onClick={() =>
            onSuggestion(
              "Explain artificial intelligence in simple terms"
            )
          }
        >

          <Bot size={17} />

          <div>

            <strong>
              Explain something
            </strong>

            <span>
              Learn a concept in
              simple terms
            </span>

          </div>

        </button>


        <button
          onClick={() =>
            onSuggestion(
              "Write a Python program to reverse a string"
            )
          }
        >

          <ChefHat size={17} />

          <div>

            <strong>
              Write code
            </strong>

            <span>
              Create code for
              your idea
            </span>

          </div>

        </button>


        <button
          onClick={() =>
            onSuggestion(
              "Calculate 18% of 250 and explain the answer"
            )
          }
        >

          <Bot size={17} />

          <div>

            <strong>
              Solve a problem
            </strong>

            <span>
              Calculate and explain
              the answer
            </span>

          </div>

        </button>


        <button
          onClick={() =>
            onSuggestion(
              "Research artificial intelligence"
            )
          }
        >

          <Bot size={17} />

          <div>

            <strong>
              Research
            </strong>

            <span>
              Find useful information
              about a topic
            </span>

          </div>

        </button>

      </div>

    </div>
  );
}


/* =========================================================
   NORMALIZE MATH
========================================================= */

function normalizeMath(content) {

  if (!content) {
    return content;
  }

  return content
    .replace(
      /\\\[(.*?)\\\]/gs,
      "$$$1$$"
    )
    .replace(
      /\\\((.*?)\\\)/gs,
      "$$$1$"
    );
}


/* =========================================================
   MARKDOWN MESSAGE
========================================================= */

function MarkdownMessage({
  content,
  onCopyCode,
  messageIndex,
}) {

  return (

    <ReactMarkdown
      remarkPlugins={[
        remarkGfm,
        remarkMath,
      ]}
      rehypePlugins={[
        rehypeKatex,
      ]}
      components={{

        code({
          inline,
          className,
          children,
          ...props
        }) {

          const match =
            /language-([\w+#.-]+)/.exec(
              className || ""
            );


          const language =
            normalizeLanguage(
              match?.[1]
            );


          const code =
            String(children)
              .replace(
                /\n$/,
                ""
              );


          if (
            !inline &&
            match
          ) {

            return (

              <div className="code-block">

                <div className="code-header">

                  <span>
                    {getLanguageLabel(
                      language
                    )}
                  </span>


                  <button
                    className="code-copy-button"
                    onClick={() =>
                      onCopyCode(
                        code,
                        messageIndex
                      )
                    }
                  >

                    <Copy size={13} />

                    Copy

                  </button>

                </div>


                <SyntaxHighlighter
                  style={oneDark}
                  language={
                    language ||
                    "text"
                  }
                  PreTag="div"
                  customStyle={{
                    margin: 0,
                  }}
                  {...props}
                >
                  {code}
                </SyntaxHighlighter>

              </div>

            );
          }


          return (

            <code
              className="inline-code"
              {...props}
            >
              {children}
            </code>

          );
        },


        table({
          children,
        }) {

          return (

            <div className="markdown-table-wrapper">

              <table>
                {children}
              </table>

            </div>

          );
        },

      }}
    >

      {normalizeMath(content)}

    </ReactMarkdown>
  );
}


/* =========================================================
   MESSAGE
========================================================= */

function Message({
  message,
  index,
  copiedIndex,
  onCopy,
}) {

  const isUser =
    message.role === "user";


  const copyCode = async (
    text,
    messageIndex
  ) => {

    try {

      await navigator.clipboard.writeText(
        text
      );

      onCopy(
        text,
        messageIndex
      );

    } catch (error) {

      console.error(error);

    }
  };


  return (

    <div
      className={`message ${
        isUser
          ? "user-message"
          : "assistant-message"
      }`}
    >

      <div
        className={`avatar ${
          isUser
            ? "user-avatar"
            : "assistant-avatar"
        }`}
      >

        {isUser ? (
          <User size={16} />
        ) : (
          <ChefHat size={16} />
        )}

      </div>


      <div className="message-body">

        <div className="message-author">

          {isUser
            ? "You"
            : "SANJI AI"}

        </div>


        <div
          className={`message-text ${
            message.error
              ? "error-text"
              : ""
          }`}
        >

          {isUser ? (

            <div className="user-content">
              {message.content}
            </div>

          ) : (

            <MarkdownMessage
              content={
                message.content
              }
              onCopyCode={
                copyCode
              }
              messageIndex={
                index
              }
            />

          )}

        </div>


        {!isUser &&
          !message.error && (

          <div className="message-actions">

            <button
              onClick={() =>
                onCopy(
                  message.content,
                  index
                )
              }
            >

              {copiedIndex ===
                index ? (

                <>
                  <Check size={13} />
                  Copied
                </>

              ) : (

                <>
                  <Copy size={13} />
                  Copy
                </>

              )}

            </button>


            {message.verified && (

              <span className="verified">

                <Check size={13} />

                Verified

              </span>

            )}

          </div>

        )}

      </div>

    </div>
  );
}


/* =========================================================
   TYPING
========================================================= */

function Typing() {

  return (

    <div className="message assistant-message">

      <div className="avatar assistant-avatar">

        <ChefHat size={16} />

      </div>


      <div className="message-body">

        <div className="message-author">
          SANJI AI
        </div>


        <div className="typing">

          <span />
          <span />
          <span />

        </div>

      </div>

    </div>
  );
}


/* =========================================================
   LANGUAGE HELPERS
========================================================= */

function normalizeLanguage(
  language
) {

  if (!language) {
    return "";
  }


  const aliases = {

    py: "python",
    python3: "python",

    js: "javascript",
    jsx: "jsx",

    ts: "typescript",
    tsx: "tsx",

    c: "c",

    "c++": "cpp",
    cpp: "cpp",

    "c#": "csharp",
    cs: "csharp",

    java: "java",

    html: "xml",
    xhtml: "xml",

    css: "css",
    scss: "scss",

    sql: "sql",

    sh: "bash",
    shell: "bash",
    zsh: "bash",

    ps: "powershell",
    ps1: "powershell",
    powershell: "powershell",

    yml: "yaml",
    yaml: "yaml",

    md: "markdown",
    markdown: "markdown",

    rs: "rust",
    rust: "rust",

    go: "go",
    golang: "go",

    kt: "kotlin",
    kotlin: "kotlin",

    rb: "ruby",
    ruby: "ruby",

    php: "php",

    swift: "swift",

    dart: "dart",

    lua: "lua",

    r: "r",

    json: "json",

    xml: "xml",

    graphql: "graphql",
    gql: "graphql",

    dockerfile: "docker",

  };


  return (
    aliases[
      language.toLowerCase()
    ] ||
    language.toLowerCase()
  );
}


/* =========================================================
   LANGUAGE LABEL
========================================================= */

function getLanguageLabel(
  language
) {

  const labels = {

    javascript: "JavaScript",
    jsx: "JSX",

    typescript: "TypeScript",
    tsx: "TSX",

    python: "Python",

    java: "Java",

    cpp: "C++",
    csharp: "C#",
    c: "C",

    html: "HTML",
    xml: "XML",

    css: "CSS",
    scss: "SCSS",

    sql: "SQL",

    bash: "Bash",
    powershell: "PowerShell",

    yaml: "YAML",

    json: "JSON",

    markdown: "Markdown",

    rust: "Rust",

    go: "Go",

    kotlin: "Kotlin",

    ruby: "Ruby",

    php: "PHP",

    swift: "Swift",

    dart: "Dart",

    lua: "Lua",

    r: "R",

    graphql: "GraphQL",

    docker: "Docker",

  };


  return (
    labels[language] ||
    language ||
    "Code"
  );
}


export default App;