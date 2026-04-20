"use client";

import { useMemo, useState } from "react";

export type AsyncTaskState = "idle" | "running" | "success" | "error";

export function useAsyncTask<TArgs extends unknown[], TResult>(
  taskFn: (...args: TArgs) => Promise<TResult>,
) {
  const [state, setState] = useState<AsyncTaskState>("idle");
  const [error, setError] = useState<string | null>(null);

  const run = async (...args: TArgs) => {
    setState("running");
    setError(null);
    try {
      const result = await taskFn(...args);
      setState("success");
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
      setState("error");
      throw err;
    }
  };

  const isBusy = useMemo(() => state === "running", [state]);

  return { state, error, isBusy, run };
}
