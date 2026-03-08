"use client";

import { useState } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import AddIcon from "@mui/icons-material/AddOutlined";
import {
  useGetAgentsQuery,
  useDeleteAgentMutation,
} from "@/store/api/agentsApi";
import { useSnackbar } from "notistack";
import type { Agent } from "@/lib/types";
import PageHeader from "@/components/common/PageHeader";
import EmptyState from "@/components/common/EmptyState";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import AgentCard from "@/components/agents/AgentCard";
import AgentForm from "@/components/agents/AgentForm";

export default function AgentsPage() {
  const { data: agents, isLoading } = useGetAgentsQuery();
  const [deleteAgent] = useDeleteAgentMutation();
  const { enqueueSnackbar } = useSnackbar();

  const [formOpen, setFormOpen] = useState(false);
  const [editAgent, setEditAgent] = useState<Agent | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Agent | null>(null);

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

      {!agents || agents.length === 0 ? (
        <EmptyState message="No agents configured yet" />
      ) : (
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
            gap: 2,
          }}
        >
          {agents.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onEdit={handleEdit}
              onDelete={setDeleteTarget}
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
