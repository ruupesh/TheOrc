"use client";

import { useState } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import AddIcon from "@mui/icons-material/AddOutlined";
import {
  useGetMcpToolsQuery,
  useDeleteMcpToolMutation,
} from "@/store/api/mcpToolsApi";
import { useSnackbar } from "notistack";
import type { McpTool } from "@/lib/types";
import PageHeader from "@/components/common/PageHeader";
import EmptyState from "@/components/common/EmptyState";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import McpToolCard from "@/components/mcp-tools/McpToolCard";
import McpToolForm from "@/components/mcp-tools/McpToolForm";

export default function McpToolsPage() {
  const { data: tools, isLoading } = useGetMcpToolsQuery();
  const [deleteTool] = useDeleteMcpToolMutation();
  const { enqueueSnackbar } = useSnackbar();

  const [formOpen, setFormOpen] = useState(false);
  const [editTool, setEditTool] = useState<McpTool | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<McpTool | null>(null);

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

      {!tools || tools.length === 0 ? (
        <EmptyState message="No MCP tools configured yet" />
      ) : (
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
            gap: 2,
          }}
        >
          {tools.map((tool) => (
            <McpToolCard
              key={tool.id}
              tool={tool}
              onEdit={handleEdit}
              onDelete={setDeleteTarget}
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
