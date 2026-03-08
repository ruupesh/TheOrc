"use client";

import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

interface PageHeaderProps {
  title: string;
  action?: React.ReactNode;
}

export default function PageHeader({ title, action }: PageHeaderProps) {
  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        mb: 3,
      }}
    >
      <Typography variant="h5">{title}</Typography>
      {action}
    </Box>
  );
}
