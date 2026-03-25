"use client";

import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import EditIcon from "@mui/icons-material/EditOutlined";
import DeleteIcon from "@mui/icons-material/DeleteOutlined";
import type { Agent } from "@/lib/types";

interface AgentCardProps {
  agent: Agent;
  onEdit: (agent: Agent) => void;
  onDelete: (agent: Agent) => void;
  canManage?: boolean;
}

export default function AgentCard({
  agent,
  onEdit,
  onDelete,
  canManage = false,
}: AgentCardProps) {
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
                {agent.name}
              </Typography>
              {agent.is_system && (
                <Chip label="System" size="small" color="info" variant="outlined" />
              )}
            </Box>
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{
                display: "block",
                fontFamily: "monospace",
              }}
            >
              {agent.host}:{agent.port}
            </Typography>
          </Box>
          {canManage && !agent.is_system && (
            <Box sx={{ display: "flex", gap: 0.5, ml: 1 }}>
              <IconButton size="small" onClick={() => onEdit(agent)}>
                <EditIcon fontSize="small" />
              </IconButton>
              <IconButton size="small" onClick={() => onDelete(agent)}>
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Box>
          )}
        </Box>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
            mb: 1,
          }}
        >
          {agent.description}
        </Typography>
        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
          <Chip
            label={`Timeout: ${agent.timeout}s`}
            size="small"
            variant="outlined"
          />
          {agent.authentication_flag && (
            <Chip label="Auth" size="small" color="warning" variant="outlined" />
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
