import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  label: string;
  variant?: "success" | "warning" | "destructive" | "secondary";
}

export const StatusBadge = ({ label, variant = "success" }: StatusBadgeProps) => {
  const styles: Record<Required<StatusBadgeProps>["variant"], string> = {
    success: "bg-success/15 border-success/30 text-success-foreground",
    warning: "bg-warning/15 border-warning/30 text-warning-foreground",
    destructive: "bg-destructive/15 border-destructive/30 text-destructive-foreground",
    secondary: "bg-secondary/15 border-secondary/30 text-foreground",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-[0.75rem] uppercase tracking-wide",
        styles[variant]
      )}
      aria-label={label}
    >
      {label}
    </span>
  );
};
