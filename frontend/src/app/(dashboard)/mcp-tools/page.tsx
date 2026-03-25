"use client";

import { useState, useMemo } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import TextField from "@mui/material/TextField";
import Stack from "@mui/material/Stack";
import InputAdornment from "@mui/material/InputAdornment";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import AddIcon from "@mui/icons-material/AddOutlined";
import SearchIcon from "@mui/icons-material/SearchOutlined";
import {
  useGetMcpToolsQuery,
  useDeleteMcpToolMutation,
} from "@/store/api/mcpToolsApi";
import { useGetMeQuery } from "@/store/api/authApi";
import { useSnackbar } from "notistack";
import type { McpTool } from "@/lib/types";
import PageHeader from "@/components/common/PageHeader";
import EmptyState from "@/components/common/EmptyState";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import McpToolCard from "@/components/mcp-tools/McpToolCard";
import McpToolForm from "@/components/mcp-tools/McpToolForm";

export default function McpToolsPage() {
  const { data: tools, isLoading } = useGetMcpToolsQuery();
  const { data: user } = useGetMeQuery();
  const [deleteTool] = useDeleteMcpToolMutation();
  const { enqueueSnackbar } = useSnackbar();
  const currentUserId = user?.id ? String(user.id) : "";

  const [searchInput, setSearchInput] = useState("");
  const [ownershipFilter, setOwnershipFilter] = useState<
    "all" | "owned" | "installed"
  >("all");
  const [connectionFilter, setConnectionFilter] = useState<
    "all" | "stdio" | "streamable_http" | "sse"
  >("all");
  const [authFilter, setAuthFilter] = useState<
    "all" | "auth" | "no_auth"
  >("all");
  const [sortBy, setSortBy] = useState<
    "newest" | "oldest" | "name_asc" | "name_desc"
  >("newest");

  const [formOpen, setFormOpen] = useState(false);
  const [editTool, setEditTool] = useState<McpTool | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<McpTool | null>(null);

  const filteredTools = useMemo(() => {
    const normalizedSearch = searchInput.trim().toLowerCase();
    const rows = (tools || []).filter((tool) => {
      const isInstalled = !!tool.installed_from_listing_id;

      if (ownershipFilter === "owned" && isInstalled) return false;
      if (ownershipFilter === "installed" && !isInstalled) return false;

      if (connectionFilter !== "all" && tool.connection_type !== connectionFilter) {
        return false;
      }

      if (authFilter === "auth" && !tool.authentication_flag) return false;
      if (authFilter === "no_auth" && tool.authentication_flag) return false;

      if (!normalizedSearch) return true;

      const haystack = `${tool.name} ${tool.connection_type} ${tool.url || ""} ${tool.command || ""}`.toLowerCase();
      return haystack.includes(normalizedSearch);
    });

    rows.sort((a, b) => {
      switch (sortBy) {
        case "oldest":
          return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        case "name_asc":
          return a.name.localeCompare(b.name);
        case "name_desc":
          return b.name.localeCompare(a.name);
        case "newest":
        default:
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      }
    });

    return rows;
  }, [
    tools,
    authFilter,
    connectionFilter,
    currentUserId,
    ownershipFilter,
    searchInput,
    sortBy,
  ]);

  const handleResetFilters = () => {
    setSearchInput("");
    setOwnershipFilter("all");
    setConnectionFilter("all");
    setAuthFilter("all");
    setSortBy("newest");
  };

  const handleEdit = (tool: McpTool) => {
    setEditTool(tool);
    setFormOpen(true);
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteTool(deleteTarget.id).unwrap();
      enqueueSnackbar("MCP tool deleted", { variant: "success" });
    } catch {
      enqueueSnackbar("Failed to delete tool", { variant: "error" });
    }
    setDeleteTarget(null);
  };

  if (isLoading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          flex: 1,
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <PageHeader
        title="MCP Tools"
        action={
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => {
              setEditTool(null);
              setFormOpen(true);
            }}
          >
            Add Tool
          </Button>
        }
      />

      <Stack
        direction={{ xs: "column", md: "row" }}
        spacing={1.5}
        sx={{ mb: 2.5 }}
      >
        <TextField
          placeholder="Search MCP tools..."
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          fullWidth
          size="small"
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

        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel id="mcp-ownership-label">Ownership</InputLabel>
          <Select
            labelId="mcp-ownership-label"
            value={ownershipFilter}
            label="Ownership"
            onChange={(e) =>
              setOwnershipFilter(e.target.value as "all" | "owned" | "installed")
            }
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="owned">Owned</MenuItem>
            <MenuItem value="installed">Installed</MenuItem>
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 170 }}>
          <InputLabel id="mcp-connection-label">Connection</InputLabel>
          <Select
            labelId="mcp-connection-label"
            value={connectionFilter}
            label="Connection"
            onChange={(e) =>
              setConnectionFilter(
                e.target.value as "all" | "stdio" | "streamable_http" | "sse"
              )
            }
          >
            <MenuItem value="all">All Connections</MenuItem>
            <MenuItem value="stdio">stdio</MenuItem>
            <MenuItem value="streamable_http">streamable_http</MenuItem>
            <MenuItem value="sse">sse</MenuItem>
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel id="mcp-auth-label">Auth</InputLabel>
          <Select
            labelId="mcp-auth-label"
            value={authFilter}
            label="Auth"
            onChange={(e) =>
              setAuthFilter(e.target.value as "all" | "auth" | "no_auth")
            }
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="auth">Auth Required</MenuItem>
            <MenuItem value="no_auth">No Auth</MenuItem>
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel id="mcp-sort-label">Sort By</InputLabel>
          <Select
            labelId="mcp-sort-label"
            value={sortBy}
            label="Sort By"
            onChange={(e) =>
              setSortBy(
                e.target.value as "newest" | "oldest" | "name_asc" | "name_desc"
              )
            }
          >
            <MenuItem value="newest">Newest First</MenuItem>
            <MenuItem value="oldest">Oldest First</MenuItem>
            <MenuItem value="name_asc">Name A–Z</MenuItem>
            <MenuItem value="name_desc">Name Z–A</MenuItem>
          </Select>
        </FormControl>

        <Button variant="outlined" onClick={handleResetFilters}>
          Reset
        </Button>
      </Stack>

      {!filteredTools || filteredTools.length === 0 ? (
        <EmptyState
          message={
            searchInput ||
            ownershipFilter !== "all" ||
            connectionFilter !== "all" ||
            authFilter !== "all"
              ? "No MCP tools match your filters"
              : "No MCP tools configured yet"
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
          {filteredTools.map((tool) => (
            <McpToolCard
              key={tool.id}
              tool={tool}
              onEdit={handleEdit}
              onDelete={setDeleteTarget}
              canManage={!!currentUserId && String(tool.owner_id) === currentUserId}
            />
          ))}
        </Box>
      )}

      <McpToolForm
        open={formOpen}
        tool={editTool}
        onClose={() => setFormOpen(false)}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete MCP Tool"
        message={`Delete tool "${deleteTarget?.name}"? This cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </Box>
  );
}
