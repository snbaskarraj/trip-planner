export function StatusMessage({ tone = "info", children, actionLabel, onAction }) {
  return (
    <div className={`status status-${tone}`} role={tone === "error" ? "alert" : "status"}>
      <p>{children}</p>
      {actionLabel && onAction ? (
        <button type="button" className="text-btn" onClick={onAction}>
          {actionLabel}
        </button>
      ) : null}
    </div>
  );
}
