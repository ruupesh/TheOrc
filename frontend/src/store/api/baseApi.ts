import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { getToken } from "@/lib/auth";

export const baseApi = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
    prepareHeaders: (headers) => {
      const token = getToken();
      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ["Agents", "McpTools", "Marketplace", "Installations", "User"],
  endpoints: () => ({}),
});
