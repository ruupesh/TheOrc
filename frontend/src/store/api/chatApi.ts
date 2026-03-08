import { baseApi } from "./baseApi";
import type { ChatRequest, ChatResponse } from "@/lib/types";

export const chatApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    sendMessage: builder.mutation<ChatResponse, ChatRequest>({
      query: (body) => ({
        url: "/chat",
        method: "POST",
        body,
      }),
    }),
  }),
});

export const { useSendMessageMutation } = chatApi;
