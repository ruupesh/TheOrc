"use client";

import { useGetMeQuery } from "@/store/api/authApi";
import { getToken } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const token = getToken();
  const { isLoading, isError } = useGetMeQuery(undefined, {
    skip: !token,
  });

  useEffect(() => {
    if (!token || isError) {
      router.replace("/login");
    }
  }, [token, isError, router]);

  if (!token || isLoading) {
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

  if (isError) return null;

  return <>{children}</>;
}
