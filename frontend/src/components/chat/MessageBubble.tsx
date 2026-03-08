"use client";

import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import type { ChatMessage } from "@/lib/types";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";

interface MessageBubbleProps {
  message: ChatMessage;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "human";

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        maxWidth: "100%",
      }}
    >
      <Box
        sx={{
          maxWidth: "75%",
          px: 2,
          py: 1.5,
          borderRadius: 2,
          bgcolor: isUser ? "primary.main" : "background.paper",
          color: isUser ? "white" : "text.primary",
          border: isUser ? "none" : "1px solid rgba(255,255,255,0.08)",
          wordBreak: "break-word",
        }}
      >
        {isUser ? (
          <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
            {message.content}
          </Typography>
        ) : (
          <Box className="markdown-body">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
            >
              {message.content}
            </ReactMarkdown>
          </Box>
        )}
        <Typography
          variant="caption"
          sx={{
            display: "block",
            mt: 0.5,
            opacity: 0.6,
            textAlign: isUser ? "right" : "left",
          }}
        >
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </Typography>
      </Box>
    </Box>
  );
}
