import { baseApi } from "./baseApi";
import type {
  MarketplaceListing,
  MarketplacePublishRequest,
  InstallAgentRequest,
  Installation,
} from "@/lib/types";

export const marketplaceApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getMarketplaceListings: builder.query<
      MarketplaceListing[],
      { search?: string; skip?: number; limit?: number } | void
    >({
      query: (params) => {
        const searchParams = new URLSearchParams();
        if (params && params.search) searchParams.set("search", params.search);
        if (params && params.skip !== undefined)
          searchParams.set("skip", String(params.skip));
        if (params && params.limit !== undefined)
          searchParams.set("limit", String(params.limit));
        const qs = searchParams.toString();
        return `/marketplace${qs ? `?${qs}` : ""}`;
      },
      providesTags: ["Marketplace"],
    }),
    getMarketplaceListing: builder.query<MarketplaceListing, string>({
      query: (id) => `/marketplace/${id}`,
    }),
    publishItem: builder.mutation<MarketplaceListing, MarketplacePublishRequest>({
      query: (body) => ({
        url: "/marketplace/publish",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Marketplace"],
    }),
    installAgent: builder.mutation<Installation, InstallAgentRequest>({
      query: (body) => ({
        url: "/marketplace/install",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Installations", "Agents"],
    }),
    getMyInstallations: builder.query<Installation[], void>({
      query: () => "/marketplace/installations/me",
      providesTags: ["Installations"],
    }),
    uninstallAgent: builder.mutation<void, string>({
      query: (id) => ({
        url: `/marketplace/installations/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Installations", "Agents"],
    }),
    removeMarketplaceListing: builder.mutation<void, string>({
      query: (id) => ({
        url: `/marketplace/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Marketplace", "Installations", "Agents", "McpTools"],
    }),
  }),
});

export const {
  useGetMarketplaceListingsQuery,
  useGetMarketplaceListingQuery,
  usePublishItemMutation,
  useInstallAgentMutation,
  useGetMyInstallationsQuery,
  useUninstallAgentMutation,
  useRemoveMarketplaceListingMutation,
} = marketplaceApi;
