"use client";

import { motion } from "framer-motion";
import type { ComponentType } from "react";

interface StatsCardProps {
  icon: ComponentType<{ className?: string }>;
  label: string;
  value: number | string;
  gradient: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  delay?: number;
}

export default function StatsCard({
  icon: Icon,
  label,
  value,
  gradient,
  trend,
  delay = 0,
}: StatsCardProps) {
  return (
    <motion.div
      initial={{ y: 50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay, duration: 0.5, type: "spring" }}
      whileHover={{ scale: 1.05, y: -5 }}
      className="relative group"
    >
      {/* Glow effect */}
      <div
        className={`absolute inset-0 bg-gradient-to-r ${gradient} rounded-2xl blur-xl opacity-30 group-hover:opacity-50 transition-opacity`}
      />

      {/* Card */}
      <div className="relative glass-light rounded-2xl p-5 border border-white/10 backdrop-blur-xl">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-400 mb-1">{label}</p>
            <motion.p
              className="text-3xl font-bold text-white"
              initial={{ scale: 0.5 }}
              animate={{ scale: 1 }}
              transition={{ delay: delay + 0.2, type: "spring" }}
            >
              {value}
            </motion.p>
            {trend && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: delay + 0.3 }}
                className={`flex items-center gap-1 mt-2 text-xs ${
                  trend.isPositive ? "text-green-400" : "text-red-400"
                }`}
              >
                <span>{trend.isPositive ? "↑" : "↓"}</span>
                <span>{Math.abs(trend.value)}% from last week</span>
              </motion.div>
            )}
          </div>
          <motion.div
            whileHover={{ rotate: 360 }}
            transition={{ duration: 0.6 }}
            className={`p-3 rounded-xl bg-gradient-to-br ${gradient}`}
          >
            <Icon className="w-6 h-6 text-white" />
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}
