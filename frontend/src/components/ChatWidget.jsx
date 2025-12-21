import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  IconButton,
  Paper,
  Typography,
  TextField,
  Avatar,
  CircularProgress,
  Tooltip,
  Fade,
  Chip,
  Divider,
} from '@mui/material';
import {
  Chat as ChatIcon,
  Close as CloseIcon,
  Send as SendIcon,
  AutoAwesome as AIIcon,
  SmartToy as BotIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { toast } from 'react-toastify';
import ReactMarkdown from 'react-markdown';
import { useAuth } from '../context/AuthContext';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ChatWidget = () => {
  const { token } = useAuth(); // Get token from AuthContext
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Example questions for quick start
  const exampleQuestions = [
    "What skills should I look for in a full-stack developer?",
    "How do I evaluate Python experience?",
    "What makes a good candidate resume?",
  ];

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current.focus(), 300);
    }
  }, [isOpen]);

  const handleToggle = () => {
    setIsOpen(!isOpen);
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message to chat
    const newMessages = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      // Build context from conversation history
      const context = messages.slice(-4).map(msg => ({
        type: msg.role === 'user' ? 'User Query' : 'AI Response',
        data: { content: msg.content }
      }));

      const response = await axios.post(
        `${API_BASE_URL}/api/chat`,
        {
          message: userMessage,
          context: context.length > 0 ? context : null,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      // Add AI response to chat
      setMessages([
        ...newMessages,
        { role: 'assistant', content: response.data.response }
      ]);
    } catch (error) {
      console.error('Chat error:', error);
      toast.error(error.response?.data?.detail || 'Failed to get response');
      
      // Add error message
      setMessages([
        ...newMessages,
        { role: 'assistant', content: '⚠️ Sorry, I encountered an error. Please try again.' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExampleClick = (question) => {
    setInput(question);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Floating Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ duration: 0.3, type: 'spring', stiffness: 200 }}
            style={{
              position: 'fixed',
              bottom: 24,
              right: 24,
              zIndex: 1000,
            }}
          >
            <Tooltip title="AI Assistant" placement="left">
              <IconButton
                onClick={handleToggle}
                sx={{
                  width: 64,
                  height: 64,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  boxShadow: '0 4px 20px rgba(102, 126, 234, 0.4)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                    boxShadow: '0 6px 30px rgba(102, 126, 234, 0.6)',
                    transform: 'scale(1.05)',
                  },
                  transition: 'all 0.3s ease',
                  animation: 'pulse 2s infinite',
                  '@keyframes pulse': {
                    '0%, 100%': {
                      boxShadow: '0 4px 20px rgba(102, 126, 234, 0.4)',
                    },
                    '50%': {
                      boxShadow: '0 4px 30px rgba(102, 126, 234, 0.6)',
                    },
                  },
                }}
              >
                <AIIcon sx={{ fontSize: 32 }} />
              </IconButton>
            </Tooltip>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ scale: 0.8, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.8, opacity: 0, y: 20 }}
            transition={{ duration: 0.3, type: 'spring', stiffness: 200 }}
            style={{
              position: 'fixed',
              bottom: 24,
              right: 24,
              zIndex: 1000,
              width: '400px',
              maxWidth: 'calc(100vw - 48px)',
            }}
          >
            <Paper
              elevation={24}
              sx={{
                height: '600px',
                maxHeight: 'calc(100vh - 100px)',
                display: 'flex',
                flexDirection: 'column',
                borderRadius: 3,
                overflow: 'hidden',
                background: (theme) =>
                  theme.palette.mode === 'dark'
                    ? 'linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%)'
                    : 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
              }}
            >
              {/* Header */}
              <Box
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  p: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <Avatar
                    sx={{
                      bgcolor: 'rgba(255, 255, 255, 0.2)',
                      width: 40,
                      height: 40,
                    }}
                  >
                    <BotIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h6" fontWeight="bold">
                      AI Assistant
                    </Typography>
                    <Typography variant="caption" sx={{ opacity: 0.9 }}>
                      Powered by Groq Llama 3.3
                    </Typography>
                  </Box>
                </Box>
                <IconButton
                  onClick={handleToggle}
                  size="small"
                  sx={{ color: 'white' }}
                >
                  <CloseIcon />
                </IconButton>
              </Box>

              {/* Messages Area */}
              <Box
                sx={{
                  flex: 1,
                  overflowY: 'auto',
                  p: 2,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 2,
                  '&::-webkit-scrollbar': {
                    width: '6px',
                  },
                  '&::-webkit-scrollbar-track': {
                    background: 'transparent',
                  },
                  '&::-webkit-scrollbar-thumb': {
                    background: (theme) =>
                      theme.palette.mode === 'dark'
                        ? 'rgba(255, 255, 255, 0.2)'
                        : 'rgba(0, 0, 0, 0.2)',
                    borderRadius: '10px',
                  },
                }}
              >
                {messages.length === 0 ? (
                  // Welcome Screen
                  <Box
                    sx={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      height: '100%',
                      gap: 3,
                      textAlign: 'center',
                      px: 2,
                    }}
                  >
                    <Avatar
                      sx={{
                        width: 80,
                        height: 80,
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        mb: 2,
                      }}
                    >
                      <AIIcon sx={{ fontSize: 48 }} />
                    </Avatar>
                    <Typography variant="h6" fontWeight="bold">
                      Welcome to AI Assistant!
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      I can help you with recruitment questions, candidate analysis, and more.
                    </Typography>
                    <Divider sx={{ width: '100%', my: 1 }} />
                    <Typography variant="caption" color="text.secondary" fontWeight="bold">
                      Try asking:
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, width: '100%' }}>
                      {exampleQuestions.map((question, index) => (
                        <Chip
                          key={index}
                          label={question}
                          onClick={() => handleExampleClick(question)}
                          sx={{
                            cursor: 'pointer',
                            '&:hover': {
                              bgcolor: 'primary.main',
                              color: 'white',
                            },
                          }}
                        />
                      ))}
                    </Box>
                  </Box>
                ) : (
                  // Chat Messages
                  <>
                    {messages.map((message, index) => (
                      <Fade key={index} in timeout={300}>
                        <Box
                          sx={{
                            display: 'flex',
                            justifyContent:
                              message.role === 'user' ? 'flex-end' : 'flex-start',
                            gap: 1,
                          }}
                        >
                          {message.role === 'assistant' && (
                            <Avatar
                              sx={{
                                width: 32,
                                height: 32,
                                bgcolor: 'primary.main',
                                mt: 0.5,
                              }}
                            >
                              <BotIcon fontSize="small" />
                            </Avatar>
                          )}
                          <Paper
                            elevation={1}
                            sx={{
                              p: 1.5,
                              maxWidth: '80%',
                              bgcolor:
                                message.role === 'user'
                                  ? 'primary.main'
                                  : (theme) =>
                                      theme.palette.mode === 'dark'
                                        ? 'grey.800'
                                        : 'grey.100',
                              color:
                                message.role === 'user'
                                  ? 'white'
                                  : 'text.primary',
                              borderRadius: 2,
                            }}
                          >
                            {message.role === 'assistant' ? (
                              <ReactMarkdown
                                components={{
                                  p: ({ children }) => (
                                    <Typography variant="body2" sx={{ mb: 1, '&:last-child': { mb: 0 } }}>
                                      {children}
                                    </Typography>
                                  ),
                                  strong: ({ children }) => (
                                    <Box component="span" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                                      {children}
                                    </Box>
                                  ),
                                  code: ({ children }) => (
                                    <Box
                                      component="code"
                                      sx={{
                                        bgcolor: (theme) =>
                                          theme.palette.mode === 'dark'
                                            ? 'rgba(255, 255, 255, 0.1)'
                                            : 'rgba(0, 0, 0, 0.1)',
                                        px: 0.5,
                                        py: 0.25,
                                        borderRadius: 0.5,
                                        fontSize: '0.9em',
                                        fontFamily: 'monospace',
                                      }}
                                    >
                                      {children}
                                    </Box>
                                  ),
                                  ul: ({ children }) => (
                                    <Box component="ul" sx={{ pl: 2, my: 1 }}>
                                      {children}
                                    </Box>
                                  ),
                                  li: ({ children }) => (
                                    <Typography component="li" variant="body2" sx={{ mb: 0.5 }}>
                                      {children}
                                    </Typography>
                                  ),
                                  table: ({ children }) => (
                                    <Box sx={{ overflowX: 'auto', my: 1 }}>
                                      <Box component="table" sx={{ width: '100%', fontSize: '0.85em' }}>
                                        {children}
                                      </Box>
                                    </Box>
                                  ),
                                }}
                              >
                                {message.content}
                              </ReactMarkdown>
                            ) : (
                              <Typography variant="body2">{message.content}</Typography>
                            )}
                          </Paper>
                        </Box>
                      </Fade>
                    ))}
                    {isLoading && (
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Avatar
                          sx={{
                            width: 32,
                            height: 32,
                            bgcolor: 'primary.main',
                            mt: 0.5,
                          }}
                        >
                          <BotIcon fontSize="small" />
                        </Avatar>
                        <Paper
                          elevation={1}
                          sx={{
                            p: 1.5,
                            bgcolor: (theme) =>
                              theme.palette.mode === 'dark' ? 'grey.800' : 'grey.100',
                            borderRadius: 2,
                          }}
                        >
                          <CircularProgress size={20} />
                        </Paper>
                      </Box>
                    )}
                    <div ref={messagesEndRef} />
                  </>
                )}
              </Box>

              {/* Input Area */}
              <Box
                sx={{
                  p: 2,
                  borderTop: 1,
                  borderColor: 'divider',
                  bgcolor: (theme) =>
                    theme.palette.mode === 'dark' ? 'background.paper' : 'background.default',
                }}
              >
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <TextField
                    inputRef={inputRef}
                    fullWidth
                    multiline
                    maxRows={3}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask me anything..."
                    variant="outlined"
                    size="small"
                    disabled={isLoading}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: 2,
                      },
                    }}
                  />
                  <IconButton
                    onClick={handleSend}
                    disabled={!input.trim() || isLoading}
                    sx={{
                      bgcolor: 'primary.main',
                      color: 'white',
                      '&:hover': {
                        bgcolor: 'primary.dark',
                      },
                      '&.Mui-disabled': {
                        bgcolor: 'action.disabledBackground',
                      },
                    }}
                  >
                    <SendIcon />
                  </IconButton>
                </Box>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ display: 'block', mt: 1, textAlign: 'center' }}
                >
                  Press Enter to send • Shift+Enter for new line
                </Typography>
              </Box>
            </Paper>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default ChatWidget;
