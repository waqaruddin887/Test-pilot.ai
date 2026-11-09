export async function api<T>(path: string, body?: unknown): Promise<T> {
  const csrf =
    typeof document === "undefined"
      ? ""
      : document.cookie
          .split("; ")
          .find((v) => v.startsWith("tp_csrf="))
          ?.split("=")[1] || "";
  const response = await fetch("/api" + path, {
    method: body === undefined ? "GET" : "POST",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrf,
      "Idempotency-Key": crypto.randomUUID(),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ message: "Service unavailable" }));
    throw new Error(`${response.status}: ${error.message || "Request failed"}`);
  }
  return response.json() as Promise<T>;
}
