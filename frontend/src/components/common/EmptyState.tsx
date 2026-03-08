"use client";

import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import InboxIcon from "@mui/icons-material/InboxOutlined";

interface EmptyStateProps {
  message: string;
  icon?: React.ReactNode;
}

export default function EmptyState({ message, icon }: EmptyStateProps) {
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        py: 8,
        color: "text.secondary",
      }}
    >
      {icon || <InboxIcon sx={{ fontSize: 48, mb: 1, opacity: 0.5 }} />}
      <Typography variant="body1">{message}</Typography>
    </Box>
  );
}
