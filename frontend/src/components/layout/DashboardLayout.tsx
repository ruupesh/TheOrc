"use client";

import Box from "@mui/material/Box";
import Sidebar from "./Sidebar";

const DRAWER_WIDTH = 240;

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <Sidebar />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: `calc(100% - ${DRAWER_WIDTH}px)`,
          bgcolor: "background.default",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {children}
      </Box>
    </Box>
  );
}
