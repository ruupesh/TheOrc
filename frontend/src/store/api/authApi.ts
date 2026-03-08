import { baseApi } from "./baseApi";
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
} from "@/lib/types";

export const authApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    login: builder.mutation<TokenResponse, LoginRequest>({
      query: (body) => ({
        url: "/auth/login",
        method: "POST",
        body,
      }),
    }),
    register: builder.mutation<User, RegisterRequest>({
      query: (body) => ({
        url: "/auth/register",
        method: "POST",
        body,
      }),
    }),
    getMe: builder.query<User, void>({
      query: () => "/auth/me",
      providesTags: ["User"],
    }),
  }),
});

export const { useLoginMutation, useRegisterMutation, useGetMeQuery } = authApi;
