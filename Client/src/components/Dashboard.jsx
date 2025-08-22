import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "github-markdown-css/github-markdown-light.css";
import {
  AppBar,
  Box,
  IconButton,
  Paper,
  Button,
  TextField,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import ChatIcon from "@mui/icons-material/Chat";
import axios from "axios";

function TypingIndicator() {
  return (
    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
      <Box sx={{
        width: 8, height: 8, bgcolor: "grey.500", borderRadius: "50%",
        animation: "blink 1.4s infinite both"
      }} />
      <Box sx={{
        width: 8, height: 8, bgcolor: "grey.500", borderRadius: "50%",
        animation: "blink 1.4s infinite 0.2s both"
      }} />
      <Box sx={{
        width: 8, height: 8, bgcolor: "grey.500", borderRadius: "50%",
        animation: "blink 1.4s infinite 0.4s both"
      }} />
      <style>
        {`@keyframes blink {
            0%, 80%, 100% { opacity: 0; }
            40% { opacity: 1; }
        }`}
      </style>
    </Box>
  );
}


export default function Dashboard() {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const [chatHistory, setChatHistory] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);

  // Fetch chat sessions when component mounts
  useEffect(() => {
    const fetchChatSessions = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/tutor/sessions/${user.userId}`);
        setChatHistory(response.data);
      } catch (error) {
        console.error('Error fetching chat sessions:', error);
      }
    };
    
    if (user.userId) {
      fetchChatSessions();
    }
  }, [user.userId]);

  const handleNewChat = () => {
    setMessages([
      {
        sender: "bot",
        text: "Hello! I'm your AI assistant. How can I help you today?",
      },
    ]);
    setCurrentChatId(null);
  };

  const handleChatSelect = async (chatId) => {
    setCurrentChatId(chatId);
    try {
      const response = await axios.get(
        `http://localhost:8000/tutor/history/${user.userId}/${chatId}`
      );
      
      // Transform the chat history into our message format
      const formattedMessages = response.data.chats.map(chat => ([
        { sender: "user", text: chat.query },
        { sender: "bot", text: chat.answer }
      ])).flat();
      
      setMessages(formattedMessages);
    } catch (error) {
      console.error('Error fetching chat history:', error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hello! I’m your AI assistant. How can I help you today?",
    },
  ]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message
    setMessages((prev) => [...prev, { sender: "user", text: input }]);
    setMessages((prev) => [...prev, { sender: "bot", isTyping: true }]);

    try {
      const requestBody = {
        query: input,
        user_id: user.userId,
        chat_session_id: currentChatId
      };
      const response = await axios.post(
        "http://localhost:8000/tutor/ask",
        requestBody
      );

      // Add bot response from API
      setMessages((prev) => {
      const newMessages = [...prev];
      const typingIndex = newMessages.findIndex(m => m.isTyping);
      if (typingIndex !== -1) {
        newMessages[typingIndex] = {
          sender: "bot",
          text: response.data.answer || "Sorry, I couldn't process that request."
        };
      } else {
        newMessages.push({
          sender: "bot",
          text: response.data.answer || "Sorry, I couldn't process that request."
        });
      }
      return newMessages;
    });
  } catch (error) {
    console.error("Error:", error);
    setMessages((prev) => [
      ...prev,
      {
        sender: "bot",
        text: "Sorry, there was an error processing your request.",
      },
    ]);
  }

  setInput("");
};

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);
  return (
    <Box sx={{ display: "flex", height: "100vh" }}>
      {/* Sidebar */}
      <Drawer
        variant="permanent"
        sx={{
          width: 240,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: 240,
            boxSizing: "border-box",
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: "auto" }}>
          <List>
            <ListItem button onClick={handleNewChat}>
              <ListItemIcon>
                <AddIcon />
              </ListItemIcon>
              <ListItemText primary="New Chat" />
            </ListItem>
            <Divider />
            {chatHistory.map((chat) => (
              <ListItem
                button
                key={chat.chat_session_id}
                selected={currentChatId === chat.chat_session_id}
                onClick={() => handleChatSelect(chat.chat_session_id)}
              >
                <ListItemIcon>
                  <ChatIcon />
                </ListItemIcon>
                <ListItemText 
                  primary={`Chat ${chat.chat_session_id}`} 
                  secondary={new Date(chat.created_at).toLocaleDateString()}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box sx={{ flexGrow: 1, display: "flex", flexDirection: "column" }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              AI Tutor Home
            </Typography>

            <Typography variant="body1" component="div" sx={{ flexGrow: 1 }}>
              RAG Chatbot
            </Typography>

            <Button color="inherit" onClick={() => handleLogout()}>
              Logout
            </Button>
          </Toolbar>
        </AppBar>
        <div className="flex-grow-1 overflow-auto">
          <Box
            sx={{ height: "100%", display: "flex", flexDirection: "column" }}
          >
            {/* Header */}
            <AppBar position="static" color="default" elevation={1}>
              <Toolbar>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                  Chatbot
                </Typography>
              </Toolbar>
            </AppBar>

            {/* Messages Area */}
            <Box
              sx={{
                flex: 1,
                overflowY: "auto",
                px: 2,
                py: 3,
                bgcolor: "#f5f5f5",
                display: "flex",
                flexDirection: "column",
              }}
            >
              {messages.map((msg, idx) => (
                <Box
                  key={idx}
                  sx={{
                    display: "flex",
                    justifyContent:
                      msg.sender === "user" ? "flex-end" : "flex-start",
                    mb: 2,
                  }}
                >
                  <Paper
                    elevation={1}
                    sx={{
                      p: 2,
                      maxWidth: "80%",
                      whiteSpace: "pre-wrap",
                      bgcolor:
                        msg.sender === "user"
                          ? "primary.main"
                          : "background.paper",
                      color: msg.sender === "user" ? "white" : "text.primary",
                      borderRadius: 3,
                    }}
                  >
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                    >
                      {msg.text}
                    </ReactMarkdown>
                  </Paper>
                </Box>
              ))}
              <div ref={messagesEndRef} />
            </Box>

            {/* Input Area (sticky bottom like ChatGPT) */}
            <Box
              sx={{
                borderTop: "1px solid #ddd",
                p: 2,
                display: "flex",
                alignItems: "center",
                bgcolor: "background.paper",
              }}
            >
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Send a message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
              />
              <IconButton color="primary" onClick={handleSend} sx={{ ml: 1 }}>
                Send
              </IconButton>
            </Box>
          </Box>
        </div>
      </Box>
    </Box>
  );
}
