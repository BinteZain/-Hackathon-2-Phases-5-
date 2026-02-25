"use client";

import { motion } from "framer-motion";
import { FlagIcon } from "@heroicons/react/24/solid";

export type Priority = "none" | "low" | "medium" | "high" | "urgent";

interface PriorityBadgeProps {
  priority: Priority;
  onClick?: () => void;
  size?: "sm" | "md" | "lg";
}

const priorityConfig: Record<Priority, { color: string; gradient: string; label: string; icon: string }> = {
  none: {
    color: "text-gray-400",
    gradient: "from-gray-500 to-gray-600",
    label: "None",
    icon: "○",
  },
  low: {
    color: "text-green-400",
    gradient: "from-green-500 to-emerald-600",
    label: "Low",
    icon: "⬇",
  },
  medium: {
    color: "text-blue-400",
    gradient: "from-blue-500 to-cyan-600",
    label: "Medium",
    icon: "➡",
  },
  high: {
    color: "text-orange-400",
    gradient: "from-orange-500 to-yellow-600",
    label: "High",
    icon: "⬆",
  },
  urgent: {
    color: "text-red-400",
    gradient: "from-red-500 to-pink-600",
    label: "Urgent",
    icon: "❗",
  },
};

const sizeClasses = {
  sm: "px-2 py-1 text-xs",
  md: "px-3 py-1.5 text-sm",
  lg: "px-4 py-2 text-base",
};

export default function PriorityBadge({ priority, onClick, size = "md" }: PriorityBadgeProps) {
  const config = priorityConfig[priority];

  return (
    <motion.button
      whileHover={onClick ? { scale: 1.05 } : {}}
      whileTap={onClick ? { scale: 0.95 } : {}}
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 rounded-full font-medium transition-all ${
        sizeClasses[size]
      } bg-gradient-to-r ${config.gradient} text-white shadow-lg ${
        onClick ? "cursor-pointer hover:shadow-xl" : "cursor-default"
      }`}
    >
      <FlagIcon className="w-4 h-4" />
      <span>{config.label}</span>
    </motion.button>
  );
}

export function PrioritySelector({
  value,
  onChange,
}: {
  value: Priority;
  onChange: (priority: Priority) => void;
}) {
  const priorities: Priority[] = ["none", "low", "medium", "high", "urgent"];

  return (
    <div className="flex gap-2 flex-wrap">
      {priorities.map((priority) => {
        const config = priorityConfig[priority];
        const isSelected = value === priority;

        return (
          <motion.button
            key={priority}
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => onChange(priority)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all border ${
              isSelected
                ? `bg-gradient-to-r ${config.gradient} text-white border-transparent shadow-lg`
                : "bg-white/5 text-gray-300 border-white/10 hover:border-white/30"
            }`}
          >
            {config.label}
          </motion.button>
        );
      })}
    </div>
  );
}
