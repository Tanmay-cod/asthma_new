export default async function Home() {
  let health = "unreachable";
  try {
    const res = await fetch("http://localhost:8000/api/v1/health", { cache: "no-store" });
    if (res.ok) health = (await res.json()).status;
  } catch {}

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8">
      <h1 className="text-3xl font-bold">Asthma Risk System</h1>
      <p className="text-lg">
        Backend status:{" "}
        <span className={health === "ok" ? "text-green-600 font-semibold" : "text-red-600 font-semibold"}>
          {health}
        </span>
      </p>
      <p className="text-sm text-gray-500">
        Research prototype — not a diagnostic or treatment system.
      </p>
    </main>
  );
}
