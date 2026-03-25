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
  useGetAgentsQuery,
  useDeleteAgentMutation,
} from "@/store/api/agentsApi";
import { useGetMeQuery } from "@/store/api/authApi";
import { useSnackbar } from "notistack";
import type { Agent } from "@/lib/types";
import PageHeader from "@/components/common/PageHeader";
import EmptyState from "@/components/common/EmptyState";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import AgentCard from "@/components/agents/AgentCard";
import AgentForm from "@/components/agents/AgentForm";

export default function AgentsPage() {
  const { data: agents, isLoading } = useGetAgentsQuery();
  const { data: user } = useGetMeQuery();
  const [deleteAgent] = useDeleteAgentMutation();
  const { enqueueSnackbar } = useSnackbar();
  const currentUserId = user?.id ? String(user.id) : "";

  const [searchInput, setSearchInput] = useState("");
  const [ownershipFilter, setOwnershipFilter] = useState<
    "all" | "owned" | "installed"
  >("all");
  const [systemFilter, setSystemFilter] = useState<
    "all" | "system" | "custom"
  >("all");
  const [authFilter, setAuthFilter] = useState<
    "all" | "auth" | "no_auth"
  >("all");
  const [sortBy, setSortBy] = useState<
    "newest" | "oldest" | "name_asc" | "name_desc"
  >("newest");

  const [formOpen, setFormOpen] = useState(false);
  const [editAgent, setEditAgent] = useState<Agent | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Agent | null>(null);

  const filteredAgents = useMemo(() => {
    const normalizedSearch = searchInput.trim().toLowerCase();
    const rows = (agents || []).filter((agent) => {
      const isOwn = !!currentUserId && String(agent.owner_id) === currentUserId;

      if (ownershipFilter === "owned" && !isOwn) return false;
      if (ownershipFilter === "installed" && isOwn) return false;

      if (systemFilter === "system" && !agent.is_system) return false;
      if (systemFilter === "custom" && agent.is_system) return false;

      if (authFilter === "auth" && !agent.authentication_flag) return false;
      if (authFilter === "no_auth" && agent.authentication_flag) return false;

      if (!normalizedSearch) return true;

      const haystack = `${agent.name} ${agent.description} ${agent.host}:${agent.port}`.toLowerCase();
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
    agents,
    authFilter,
    currentUserId,
    ownershipFilter,
    searchInput,
    sortBy,
    systemFilter,
  ]);

  const handleResetFilters = () => {
    setSearchInput("");
    setOwnershipFilter("all");
    setSystemFilter("all");
    setAuthFilter("all");
    setSortBy("newest");
  };

  const handleEdit = (agent: Agent) => {
    setEditAgent(agent);
    setFormOpen(true);
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteAgent(deleteTarget.id).unwrap();
      enqueueSnackbar("Agent deleted", { variant: "success" });
    } catch {
      enqueueSnackbar("Failed to delete agent", { variant: "error" });
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
        title="Agents"
        action={
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => {
              setEditAgent(null);
              setFormOpen(true);
            }}
          >
            Add Agent
          </Button>
        }
      />

      <Stack
        direction={{ xs: "column", md: "row" }}
        spacing={1.5}
        sx={{ mb: 2.5 }}
      >
        <TextField
          placeholder="Search agents..."
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
          <InputLabel id="agents-ownership-label">Ownership</InputLabel>
          <Select
            labelId="agents-ownership-label"
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

        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel id="agents-system-label">Type</InputLabel>
          <Select
            labelId="agents-system-label"
            value={systemFilter}
            label="Type"
            onChange={(e) =>
              setSystemFilter(e.target.value as "all" | "system" | "custom")
            }
          >
            <MenuItem value="all">All Types</MenuItem>
            <MenuItem value="custom">Custom</MenuItem>
            <MenuItem value="system">System</MenuItem>
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel id="agents-auth-label">Auth</InputLabel>
          <Select
            labelId="agents-auth-label"
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
          <InputLabel id="agents-sort-label">Sort By</InputLabel>
          <Select
            labelId="agents-sort-label"
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

      {!filteredAgents || filteredAgents.length === 0 ? (
        <EmptyState
          message={
            searchInput ||
            ownershipFilter !== "all" ||
            systemFilter !== "all" ||
            authFilter !== "all"
              ? "No agents match your filters"
              : "No agents configured yet"
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
          {filteredAgents.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onEdit={handleEdit}
              onDelete={setDeleteTarget}
              canManage={!!currentUserId && String(agent.owner_id) === currentUserId}
            />
          ))}
        </Box>
      )}

      <AgentForm
        open={formOpen}
        agent={editAgent}
        onClose={() => setFormOpen(false)}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Agent"
        message={`Delete agent "${deleteTarget?.name}"? This cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </Box>
  );
}
