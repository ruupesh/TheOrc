"use client";

import { useState, useEffect, useMemo } from "react";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import InputAdornment from "@mui/material/InputAdornment";
import Stack from "@mui/material/Stack";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import SearchIcon from "@mui/icons-material/SearchOutlined";
import PublishIcon from "@mui/icons-material/PublishOutlined";
import {
  useGetMarketplaceListingsQuery,
  useGetMyInstallationsQuery,
} from "@/store/api/marketplaceApi";
import { useGetMeQuery } from "@/store/api/authApi";
import PageHeader from "@/components/common/PageHeader";
import EmptyState from "@/components/common/EmptyState";
import ListingCard from "@/components/marketplace/ListingCard";
import PublishDialog from "@/components/marketplace/PublishDialog";

export default function MarketplacePage() {
  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [publishOpen, setPublishOpen] = useState(false);
  const [itemTypeFilter, setItemTypeFilter] = useState<
    "all" | "agent" | "mcp_tool"
  >("all");
  const [visibilityFilter, setVisibilityFilter] = useState<
    "all" | "public" | "private"
  >("all");
  const [ownershipFilter, setOwnershipFilter] = useState<
    "all" | "owned" | "installed" | "not_installed"
  >("all");
  const [sortBy, setSortBy] = useState<
    "newest" | "oldest" | "title_asc" | "title_desc"
  >("newest");

  useEffect(() => {
    const timer = setTimeout(() => {
      setSearch(searchInput);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchInput]);

  const { data: listings, isLoading } = useGetMarketplaceListingsQuery(
    search ? { search } : undefined
  );
  const { data: installations } = useGetMyInstallationsQuery();
  const { data: user } = useGetMeQuery();
  const currentUserId = user?.id ? String(user.id) : "";

  const filteredListings = useMemo(() => {
    const installedListingIds = new Set(
      (installations || []).map((inst) => String(inst.listing_id))
    );

    const rows = (listings || []).filter((listing) => {
      if (itemTypeFilter !== "all" && listing.item_type !== itemTypeFilter) {
        return false;
      }

      if (visibilityFilter !== "all" && listing.visibility !== visibilityFilter) {
        return false;
      }

      const isOwn = !!currentUserId && String(listing.publisher_id) === currentUserId;
      const isInstalled = installedListingIds.has(String(listing.id));

      if (ownershipFilter === "owned" && !isOwn) return false;
      if (ownershipFilter === "installed" && !isInstalled) return false;
      if (ownershipFilter === "not_installed" && (isInstalled || isOwn)) {
        return false;
      }

      return true;
    });

    rows.sort((a, b) => {
      switch (sortBy) {
        case "oldest":
          return (
            new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
          );
        case "title_asc":
          return a.title.localeCompare(b.title);
        case "title_desc":
          return b.title.localeCompare(a.title);
        case "newest":
        default:
          return (
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          );
      }
    });

    return rows;
  }, [
    installations,
    listings,
    itemTypeFilter,
    ownershipFilter,
    sortBy,
    currentUserId,
    visibilityFilter,
  ]);

  const handleResetFilters = () => {
    setItemTypeFilter("all");
    setVisibilityFilter("all");
    setOwnershipFilter("all");
    setSortBy("newest");
    setSearchInput("");
    setSearch("");
  };

  return (
    <Box sx={{ p: 3 }}>
      <PageHeader
        title="Marketplace"
        action={
          <Button
            variant="contained"
            startIcon={<PublishIcon />}
            onClick={() => setPublishOpen(true)}
          >
            Publish
          </Button>
        }
      />

      <Box sx={{ mb: 3 }}>
        <TextField
          placeholder="Search marketplace..."
          fullWidth
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          slotProps={{
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            },
          }}
        />

        <Stack
          direction={{ xs: "column", md: "row" }}
          spacing={1.5}
          sx={{ mt: 1.5 }}
        >
          <FormControl size="small" sx={{ minWidth: 160 }}>
            <InputLabel id="marketplace-item-type-label">Item Type</InputLabel>
            <Select
              labelId="marketplace-item-type-label"
              value={itemTypeFilter}
              label="Item Type"
              onChange={(e) =>
                setItemTypeFilter(e.target.value as "all" | "agent" | "mcp_tool")
              }
            >
              <MenuItem value="all">All Types</MenuItem>
              <MenuItem value="agent">Agents</MenuItem>
              <MenuItem value="mcp_tool">MCP Tools</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 160 }}>
            <InputLabel id="marketplace-visibility-label">Visibility</InputLabel>
            <Select
              labelId="marketplace-visibility-label"
              value={visibilityFilter}
              label="Visibility"
              onChange={(e) =>
                setVisibilityFilter(e.target.value as "all" | "public" | "private")
              }
            >
              <MenuItem value="all">All Visibility</MenuItem>
              <MenuItem value="public">Public</MenuItem>
              <MenuItem value="private">Private</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 180 }}>
            <InputLabel id="marketplace-ownership-label">Ownership</InputLabel>
            <Select
              labelId="marketplace-ownership-label"
              value={ownershipFilter}
              label="Ownership"
              onChange={(e) =>
                setOwnershipFilter(
                  e.target.value as "all" | "owned" | "installed" | "not_installed"
                )
              }
            >
              <MenuItem value="all">All Listings</MenuItem>
              <MenuItem value="owned">Owned By Me</MenuItem>
              <MenuItem value="installed">Already Installed</MenuItem>
              <MenuItem value="not_installed">Not Installed</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 170 }}>
            <InputLabel id="marketplace-sort-label">Sort By</InputLabel>
            <Select
              labelId="marketplace-sort-label"
              value={sortBy}
              label="Sort By"
              onChange={(e) =>
                setSortBy(
                  e.target.value as
                    | "newest"
                    | "oldest"
                    | "title_asc"
                    | "title_desc"
                )
              }
            >
              <MenuItem value="newest">Newest First</MenuItem>
              <MenuItem value="oldest">Oldest First</MenuItem>
              <MenuItem value="title_asc">Title A–Z</MenuItem>
              <MenuItem value="title_desc">Title Z–A</MenuItem>
            </Select>
          </FormControl>

          <Button variant="outlined" onClick={handleResetFilters}>
            Reset
          </Button>
        </Stack>
      </Box>

      {isLoading ? (
        <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
          <CircularProgress />
        </Box>
      ) : !filteredListings || filteredListings.length === 0 ? (
        <EmptyState
          message={
            search || itemTypeFilter !== "all" || visibilityFilter !== "all" || ownershipFilter !== "all"
              ? "No listings match your filters"
              : "No items published yet"
          }
        />
      ) : (
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
            gap: 2,
          }}
        >
          {filteredListings.map((listing) => (
            <ListingCard
              key={listing.id}
              listing={listing}
              installations={installations || []}
              currentUserId={user?.id}
            />
          ))}
        </Box>
      )}

      <PublishDialog
        open={publishOpen}
        onClose={() => setPublishOpen(false)}
      />
    </Box>
  );
}
