"use client";

import { useEffect } from "react";

import { logError } from "@/lib/logger";

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function Error({ error, reset }: ErrorProps) {
  useEffect(() => {
    logError(error, { digest: error.digest });
  }, [error]);

  return (
    <div className="hero">
      <h1 className="hero__title">Something went wrong</h1>
      <p className="hero__subtitle">
        An unexpected error occurred. You can try again or return to the home page.
      </p>
      <button type="button" className="button button--primary" onClick={reset}>
        Try again
      </button>
    </div>
  );
}
