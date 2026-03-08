import { baseApi } from "./baseApi";
import type { Agent, AgentCreate, AgentUpdate } from "@/lib/types";

export const agentsApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getAgents: builder.query<Agent[], void>({
      query: () => "/agents",
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: "Agents" as const, id })),
              { type: "Agents", id: "LIST" },
            ]
          : [{ type: "Agents", id: "LIST" }],
    }),
    getAgent: builder.query<Agent, string>({
      query: (id) => `/agents/${id}`,
      providesTags: (_result, _error, id) => [{ type: "Agents", id }],
    }),
    createAgent: builder.mutation<Agent, AgentCreate>({
      query: (body) => ({
        url: "/agents",
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "Agents", id: "LIST" }],
    }),
    updateAgent: builder.mutation<Agent, { id: string; data: AgentUpdate }>({
      query: ({ id, data }) => ({
        url: `/agents/${id}`,
        method: "PUT",
        body: data,
      }),
      invalidatesTags: (_result, _error, { id }) => [
        { type: "Agents", id },
        { type: "Agents", id: "LIST" },
      ],
    }),
    deleteAgent: builder.mutation<void, string>({
      query: (id) => ({
        url: `/agents/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: [{ type: "Agents", id: "LIST" }],
    }),
  }),
});

export const {
  useGetAgentsQuery,
  useGetAgentQuery,
  useCreateAgentMutation,
  useUpdateAgentMutation,
  useDeleteAgentMutation,
} = agentsApi;
