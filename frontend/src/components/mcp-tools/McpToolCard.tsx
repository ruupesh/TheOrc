"use client";

import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import EditIcon from "@mui/icons-material/EditOutlined";
import DeleteIcon from "@mui/icons-material/DeleteOutlined";
import type { McpTool } from "@/lib/types";

const connectionColors: Record<string, "success" | "info" | "warning"> = {
  stdio: "success",
  streamable_http: "info",
  sse: "warning",
};

interface McpToolCardProps {
  tool: McpTool;
  onEdit: (tool: McpTool) => void;
  onDelete: (tool: McpTool) => void;
  canManage?: boolean;
}

export default function McpToolCard({
  tool,
  onEdit,
  onDelete,
  canManage = false,
}: McpToolCardProps) {
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
            <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 0.5 }}>
              <Typography variant="subtitle1" fontWeight={600} noWrap>
                {tool.name}
              </Typography>
              {tool.is_system && (
                <Chip label="System" size="small" color="info" variant="outlined" />
              )}
            </Box>
            <Chip
              label={tool.connection_type}
              size="small"
              color={connectionColors[tool.connection_type] || "default"}
              variant="outlined"
            />
          </Box>
          {canManage && !tool.is_system && (
            <Box sx={{ display: "flex", gap: 0.5, ml: 1 }}>
              <IconButton size="small" onClick={() => onEdit(tool)}>
                <EditIcon fontSize="small" />
              </IconButton>
              <IconButton size="small" onClick={() => onDelete(tool)}>
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Box>
          )}
        </Box>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ fontFamily: "monospace", fontSize: 12, mb: 1 }}
          noWrap
        >
          {tool.connection_type === "stdio"
            ? `${tool.command || ""} ${(tool.args || []).join(" ")}`
            : tool.url || "—"}
        </Typography>
        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
          <Chip
            label={`Timeout: ${tool.timeout}s`}
            size="small"
            variant="outlined"
          />
          {tool.authentication_flag && (
            <Chip label="Auth" size="small" color="warning" variant="outlined" />
          )}
          {tool.tool_filter && tool.tool_filter.length > 0 && (
            <Chip
              label={`${tool.tool_filter.length} filters`}
              size="small"
              variant="outlined"
            />
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
