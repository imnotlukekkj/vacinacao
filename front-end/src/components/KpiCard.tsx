import { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: "primary" | "success" | "warning" | "accent";
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

export function KpiCard({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = "primary",
  trend,
}: KpiCardProps) {
  const variantStyles = {
    primary: "bg-gradient-primary",
    success: "bg-gradient-success",
    warning: "bg-gradient-to-br from-warning/20 to-warning/10",
    accent: "bg-gradient-to-br from-accent/20 to-accent/10",
  };

  const iconColors = {
    primary: "text-primary-foreground",
    success: "text-secondary-foreground",
    warning: "text-warning",
    accent: "text-accent",
  };

  return (
    <Card className="overflow-hidden border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
      <CardContent className="p-0">
        <div className={`${variantStyles[variant]} p-4`}>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-white/90 mb-1">{title}</p>
              <p className="text-3xl font-bold text-white mb-1">{value}</p>
              {subtitle && (
                <p className="text-xs text-white/80">{subtitle}</p>
              )}
              {trend && (
                <div className="flex items-center gap-1 mt-2">
                  <span
                    className={`text-xs font-medium ${
                      trend.isPositive ? "text-white" : "text-white/70"
                    }`}
                  >
                    {trend.isPositive ? "↑" : "↓"} {Math.abs(trend.value)}%
                  </span>
                  <span className="text-xs text-white/70">vs período anterior</span>
                </div>
              )}
            </div>
            <div className={`${iconColors[variant]} bg-white/20 backdrop-blur-sm p-3 rounded-lg`}>
              <Icon className="h-6 w-6" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
