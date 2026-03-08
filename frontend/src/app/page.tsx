"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getToken } from "@/lib/auth";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    if (getToken()) {
      router.replace("/chat");
    } else {
      router.replace("/login");
    }
  }, [router]);

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        height: "100vh",
      }}
    >
      <CircularProgress />
    </Box>
  );
}
