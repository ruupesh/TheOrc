"use client";

import { useRef, useEffect } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import CircularProgress from "@mui/material/CircularProgress";
import { useAppSelector } from "@/store/hooks";
import MessageBubble from "./MessageBubble";
import HITLApproval from "./HITLApproval";

export default function ChatWindow() {
  const { messages, isLoading } = useAppSelector((state) => state.chat);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <Box
      sx={{
        flex: 1,
        overflow: "auto",
        px: 3,
        py: 2,
        display: "flex",
        flexDirection: "column",
        gap: 2,
      }}
    >
      {messages.length === 0 && !isLoading && (
        <Box
          sx={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            gap: 1,
            color: "text.secondary",
          }}
        >
          <Typography variant="h6" sx={{ opacity: 0.5 }}>
            Start a conversation
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.4 }}>
            Ask TheOrchestrator anything — it will route to the right agent.
          </Typography>
        </Box>
      )}

      {messages.map((msg) => (
        <Box key={msg.id}>
          <MessageBubble message={msg} />
          {msg.hitl_requested && msg.hitl_requested.length > 0 && (
            <HITLApproval items={msg.hitl_requested} />
          )}
        </Box>
      ))}

      {isLoading && (
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, pl: 1 }}>
          <CircularProgress size={18} />
          <Typography variant="body2" color="text.secondary">
            Thinking...
          </Typography>
        </Box>
      )}

      <div ref={bottomRef} />
    </Box>
  );
}
