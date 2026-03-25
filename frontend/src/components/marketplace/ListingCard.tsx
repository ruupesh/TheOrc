"use client";

import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import LockIcon from "@mui/icons-material/LockOutlined";
import PublicIcon from "@mui/icons-material/PublicOutlined";
import type { MarketplaceListing, Installation } from "@/lib/types";
import {
  useInstallAgentMutation,
  useRemoveMarketplaceListingMutation,
  useUninstallAgentMutation,
} from "@/store/api/marketplaceApi";
import { useSnackbar } from "notistack";

interface ListingCardProps {
  listing: MarketplaceListing;
  installations: Installation[];
  currentUserId?: string;
}

export default function ListingCard({
  listing,
  installations,
  currentUserId,
}: ListingCardProps) {
  const { enqueueSnackbar } = useSnackbar();
  const [installAgent, { isLoading: isInstalling }] = useInstallAgentMutation();
  const [removeListing, { isLoading: isRemoving }] =
    useRemoveMarketplaceListingMutation();
  const [uninstallAgent, { isLoading: isUninstalling }] = useUninstallAgentMutation();

  const isOwnListing =
    !!currentUserId && String(listing.publisher_id) === String(currentUserId);
  const installation = installations.find(
    (i) => String(i.listing_id) === String(listing.id)
  );
  const isInstalled = !!installation;
  const isBusy = isInstalling || isUninstalling || isRemoving;
  const isAgent = listing.item_type === "agent";
  const itemName = isAgent ? listing.agent_name : listing.mcp_tool_name;

  const handleRemove = async () => {
    try {
      await removeListing(listing.id).unwrap();
      enqueueSnackbar("Removed from marketplace", { variant: "success" });
    } catch {
      enqueueSnackbar("Failed to remove listing", { variant: "error" });
    }
  };

  const handleToggle = async () => {
    if (isOwnListing) {
      enqueueSnackbar("You cannot install your own listing", { variant: "info" });
      return;
    }

    try {
      if (isInstalled && installation) {
        await uninstallAgent(installation.id).unwrap();
        enqueueSnackbar("Uninstalled", { variant: "success" });
      } else {
        await installAgent({ listing_id: listing.id }).unwrap();
        enqueueSnackbar("Installed", { variant: "success" });
      }
    } catch {
      enqueueSnackbar("Operation failed", { variant: "error" });
    }
  };

  return (
    <Card>
      <CardContent sx={{ p: 2, "&:last-child": { pb: 2 } }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            mb: 1,
          }}
        >
          <Box sx={{ minWidth: 0, flex: 1 }}>
            <Typography variant="subtitle1" fontWeight={600}>
              {listing.title}
            </Typography>
            {itemName && (
              <Typography variant="caption" color="text.secondary">
                {isAgent ? "Agent" : "MCP Tool"}: {itemName}
              </Typography>
            )}
          </Box>
          <Button
            size="small"
            variant={isOwnListing || isInstalled ? "outlined" : "contained"}
            color={isOwnListing ? "warning" : isInstalled ? "error" : "primary"}
            onClick={isOwnListing ? handleRemove : handleToggle}
            disabled={isBusy}
            sx={{ minWidth: 90, ml: 1 }}
          >
            {isBusy ? (
              <CircularProgress size={18} />
            ) : isOwnListing ? (
              "Remove"
            ) : isInstalled ? (
              "Uninstall"
            ) : (
              "Install"
            )}
          </Button>
        </Box>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            display: "-webkit-box",
            WebkitLineClamp: 3,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
            mb: 1,
          }}
        >
          {listing.description}
        </Typography>
        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
          <Chip
            label={isAgent ? "Agent" : "MCP Tool"}
            size="small"
            color={isAgent ? "primary" : "secondary"}
            variant="outlined"
          />
          <Chip
            icon={listing.visibility === "public" ? <PublicIcon sx={{ fontSize: 14 }} /> : <LockIcon sx={{ fontSize: 14 }} />}
            label={listing.visibility}
            size="small"
            variant="outlined"
          />
          {listing.publisher_username && (
            <Chip
              label={`by ${listing.publisher_username}`}
              size="small"
              variant="outlined"
            />
          )}
          {isAgent && listing.agent_host && listing.agent_port && (
            <Chip
              label={`${listing.agent_host}:${listing.agent_port}`}
              size="small"
              variant="outlined"
              sx={{ fontFamily: "monospace", fontSize: 11 }}
            />
          )}
          {!isAgent && listing.mcp_tool_connection_type && (
            <Chip
              label={listing.mcp_tool_connection_type}
              size="small"
              variant="outlined"
              sx={{ fontFamily: "monospace", fontSize: 11 }}
            />
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
