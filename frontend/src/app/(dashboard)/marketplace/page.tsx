"use client";

import { useState, useMemo } from "react";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import InputAdornment from "@mui/material/InputAdornment";
import SearchIcon from "@mui/icons-material/SearchOutlined";
import PublishIcon from "@mui/icons-material/PublishOutlined";
import {
  useGetMarketplaceListingsQuery,
  useGetMyInstallationsQuery,
} from "@/store/api/marketplaceApi";
import PageHeader from "@/components/common/PageHeader";
import EmptyState from "@/components/common/EmptyState";
import ListingCard from "@/components/marketplace/ListingCard";
import PublishDialog from "@/components/marketplace/PublishDialog";

export default function MarketplacePage() {
  const [search, setSearch] = useState("");
  const [publishOpen, setPublishOpen] = useState(false);

  const { data: listings, isLoading } = useGetMarketplaceListingsQuery(
    search ? { search } : undefined
  );
  const { data: installations } = useGetMyInstallationsQuery();

  const debouncedSearch = useMemo(() => {
    let timer: NodeJS.Timeout;
    return (value: string) => {
      clearTimeout(timer);
      timer = setTimeout(() => setSearch(value), 300);
    };
  }, []);

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
          onChange={(e) => debouncedSearch(e.target.value)}
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
      </Box>

      {isLoading ? (
        <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
          <CircularProgress />
        </Box>
      ) : !listings || listings.length === 0 ? (
        <EmptyState
          message={
            search
              ? "No matching items found"
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
          {listings.map((listing) => (
            <ListingCard
              key={listing.id}
              listing={listing}
              installations={installations || []}
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
