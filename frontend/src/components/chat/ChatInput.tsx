"use client";

import { useState, useCallback } from "react";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import IconButton from "@mui/material/IconButton";
import SendIcon from "@mui/icons-material/SendOutlined";
import { useAppSelector, useAppDispatch } from "@/store/hooks";
import { addMessage, setLoading } from "@/store/slices/chatSlice";
import { useSendMessageMutation } from "@/store/api/chatApi";
import { useGetMeQuery } from "@/store/api/authApi";
import { v4 as uuidv4 } from "uuid";
import type { ChatMessage } from "@/lib/types";

export default function ChatInput() {
  const [text, setText] = useState("");
  const dispatch = useAppDispatch();
  const { sessionId, isLoading } = useAppSelector((state) => state.chat);
  const [sendMessage] = useSendMessageMutation();
  const { data: user } = useGetMeQuery();

  const handleSend = useCallback(async () => {
    const trimmed = text.trim();
    if (!trimmed || isLoading || !user) return;

    const userMsg: ChatMessage = {
      id: uuidv4(),
      role: "human",
      content: trimmed,
      timestamp: new Date().toISOString(),
    };

    dispatch(addMessage(userMsg));
    setText("");
    dispatch(setLoading(true));

    try {
      const response = await sendMessage({
        user_id: user.id,
        session_id: sessionId,
        content: { message: trimmed },
      }).unwrap();

      const assistantMsg: ChatMessage = {
        id: response.message_id,
        role: "assistant",
        content: response.content.message || "",
        timestamp: response.timestamp,
        hitl_requested: response.content.hitl_requested,
      };

      dispatch(addMessage(assistantMsg));
    } catch {
      const errorMsg: ChatMessage = {
        id: uuidv4(),
        role: "assistant",
        content: "Sorry, something went wrong. Please try again.",
        timestamp: new Date().toISOString(),
      };
      dispatch(addMessage(errorMsg));
    } finally {
      dispatch(setLoading(false));
    }
  }, [text, isLoading, user, dispatch, sendMessage, sessionId]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box
      sx={{
        p: 2,
        borderTop: "1px solid rgba(255,255,255,0.08)",
        display: "flex",
        gap: 1,
        alignItems: "flex-end",
      }}
    >
      <TextField
        fullWidth
        multiline
        maxRows={6}
        placeholder="Type your message..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isLoading}
        size="small"
        sx={{
          "& .MuiOutlinedInput-root": {
            borderRadius: 2,
          },
        }}
      />
      <IconButton
        onClick={handleSend}
        disabled={!text.trim() || isLoading}
        color="primary"
        sx={{
          bgcolor: "primary.main",
          color: "white",
          "&:hover": { bgcolor: "primary.dark" },
          "&.Mui-disabled": { bgcolor: "action.disabledBackground" },
          width: 40,
          height: 40,
        }}
      >
        <SendIcon fontSize="small" />
      </IconButton>
    </Box>
  );
}
