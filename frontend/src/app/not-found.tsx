"use client";

import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import { useRouter } from "next/navigation";

export default function NotFound() {
  const router = useRouter();

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "100vh",
        gap: 2,
      }}
    >
      <Typography variant="h2" fontWeight={700} color="text.secondary">
        404
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Page not found
      </Typography>
      <Button variant="contained" onClick={() => router.replace("/chat")}>
        Go to Chat
      </Button>
    </Box>
  );
}
