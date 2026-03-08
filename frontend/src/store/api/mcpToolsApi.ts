import { baseApi } from "./baseApi";
import type { McpTool, McpToolCreate, McpToolUpdate } from "@/lib/types";

export const mcpToolsApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getMcpTools: builder.query<McpTool[], void>({
      query: () => "/mcp-tools",
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: "McpTools" as const, id })),
              { type: "McpTools", id: "LIST" },
            ]
          : [{ type: "McpTools", id: "LIST" }],
    }),
    getMcpTool: builder.query<McpTool, string>({
      query: (id) => `/mcp-tools/${id}`,
      providesTags: (_result, _error, id) => [{ type: "McpTools", id }],
    }),
    createMcpTool: builder.mutation<McpTool, McpToolCreate>({
      query: (body) => ({
        url: "/mcp-tools",
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "McpTools", id: "LIST" }],
    }),
    updateMcpTool: builder.mutation<
      McpTool,
      { id: string; data: McpToolUpdate }
    >({
      query: ({ id, data }) => ({
        url: `/mcp-tools/${id}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (_result, _error, { id }) => [
        { type: "McpTools", id },
        { type: "McpTools", id: "LIST" },
      ],
    }),
    deleteMcpTool: builder.mutation<void, string>({
      query: (id) => ({
        url: `/mcp-tools/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: [{ type: "McpTools", id: "LIST" }],
    }),
  }),
});

export const {
  useGetMcpToolsQuery,
  useGetMcpToolQuery,
  useCreateMcpToolMutation,
  useUpdateMcpToolMutation,
  useDeleteMcpToolMutation,
} = mcpToolsApi;
