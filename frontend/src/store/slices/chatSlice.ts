import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import type { ChatMessage } from "@/lib/types";
import { v4 as uuidv4 } from "uuid";

interface ChatState {
  sessionId: string;
  messages: ChatMessage[];
  isLoading: boolean;
}

const initialState: ChatState = {
  sessionId: uuidv4(),
  messages: [],
  isLoading: false,
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
    clearMessages(state) {
      state.messages = [];
      state.sessionId = uuidv4();
    },
  },
});

export const { addMessage, setLoading, clearMessages } = chatSlice.actions;
export default chatSlice.reducer;
