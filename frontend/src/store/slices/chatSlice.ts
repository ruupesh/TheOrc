import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import type { ChatMessage } from "@/lib/types";
import { v4 as uuidv4 } from "uuid";

interface ChatState {
  sessionId: string;
  messages: ChatMessage[];
  isLoading: boolean;
  enabledAgentIds: string[] | null;
  enabledMcpToolIds: string[] | null;
}

const initialState: ChatState = {
  sessionId: uuidv4(),
  messages: [],
  isLoading: false,
  enabledAgentIds: null,
  enabledMcpToolIds: null,
};

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    addMessage(state, action: PayloadAction<ChatMessage>) {
      state.messages.push(action.payload);
    },
    setLoading(state, action: PayloadAction<boolean>) {
      state.isLoading = action.payload;
    },
    setEnabledAgentIds(state, action: PayloadAction<string[] | null>) {
      state.enabledAgentIds = action.payload;
    },
    setEnabledMcpToolIds(state, action: PayloadAction<string[] | null>) {
      state.enabledMcpToolIds = action.payload;
    },
    clearMessages(state) {
      state.messages = [];
      state.sessionId = uuidv4();
    },
  },
});

export const {
  addMessage,
  setLoading,
  setEnabledAgentIds,
  setEnabledMcpToolIds,
  clearMessages,
} = chatSlice.actions;
export default chatSlice.reducer;
