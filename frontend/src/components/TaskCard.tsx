"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  CheckCircleIcon,
  TrashIcon,
  PencilIcon,
  CalendarIcon,
  ClockIcon,
  TagIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from "@heroicons/react/24/solid";
import TagBadge, { Tag } from "./TagBadge";
import PriorityBadge, { Priority } from "./PriorityBadge";

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: Priority;
  dueDate?: string;
  tags: Tag[];
  isRecurring: boolean;
  recurrenceRule?: string;
  createdAt: string;
  updatedAt: string;
}

interface TaskCardProps {
  task: Task;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (task: Task) => void;
  onPriorityChange?: (id: string, priority: Priority) => void;
}

const priorityBorderColors: Record<Priority, string> = {
  none: "border-gray-500/30",
  low: "border-green-500/30",
  medium: "border-blue-500/30",
  high: "border-orange-500/30",
  urgent: "border-red-500/30",
};

const priorityGlowColors: Record<Priority, string> = {
  none: "hover:shadow-gray-500/20",
  low: "hover:shadow-green-500/20",
  medium: "hover:shadow-blue-500/20",
  high: "hover:shadow-orange-500/20",
  urgent: "hover:shadow-red-500/20",
};

export default function TaskCard({ task, onToggle, onDelete, onEdit, onPriorityChange }: TaskCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showPrioritySelector, setShowPrioritySelector] = useState(false);

  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    const now = new Date();
    const isOverdue = date < now && !task.completed;
    const isToday = date.toDateString() === now.toDateString();
    const isTomorrow = new Date(now.getTime() + 86400000).toDateString() === date.toDateString();

    if (isOverdue) {
      return { text: "Overdue", color: "text-red-400" };
    } else if (isToday) {
      return { text: "Today", color: "text-yellow-400" };
    } else if (isTomorrow) {
      return { text: "Tomorrow", color: "text-blue-400" };
    } else {
      return {
        text: date.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
        color: "text-gray-300",
      };
    }
  };

  const formatRecurrence = (rule?: string) => {
    if (!rule) return "";
    const rules: Record<string, string> = {
      "FREQ=DAILY": "Daily",
      "FREQ=WEEKLY": "Weekly",
      "FREQ=MONTHLY": "Monthly",
      "FREQ=YEARLY": "Yearly",
    };
    return rules[rule] || "Recurring";
  };

  const dueDateInfo = formatDate(task.dueDate);

  return (
    <motion.div
      layout
      initial={{ x: -50, opacity: 0, scale: 0.9 }}
      animate={{ x: 0, opacity: 1, scale: 1 }}
      exit={{ x: 50, opacity: 0, scale: 0.9 }}
      transition={{ type: "spring", stiffness: 400, damping: 30 }}
      className={`group relative rounded-2xl border backdrop-blur-xl transition-all duration-300 hover:shadow-2xl ${
        priorityBorderColors[task.priority]
      } ${priorityGlowColors[task.priority]} ${
        task.completed ? "opacity-60" : "opacity-100"
      } bg-gradient-to-br from-white/10 to-white/5 hover:from-white/15 hover:to-white/10`}
    >
      {/* Priority indicator bar */}
      <div
        className={`absolute left-0 top-0 bottom-0 w-1.5 rounded-l-2xl bg-gradient-to-b ${
          task.completed
            ? "from-gray-500 to-gray-600"
            : `from-${task.priority === "none" ? "gray" : task.priority}-500 to-${task.priority === "none" ? "gray" : task.priority}-600`
        }`}
      />

      <div className="p-4 pl-6">
        {/* Main row */}
        <div className="flex items-start gap-4">
          {/* Checkbox */}
          <motion.button
            whileHover={{ scale: 1.15 }}
            whileTap={{ scale: 0.85 }}
            onClick={() => onToggle(task.id)}
            className={`mt-1 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all flex-shrink-0 ${
              task.completed
                ? "bg-gradient-to-br from-green-500 to-emerald-500 border-transparent"
                : "border-white/30 hover:border-white/60"
            }`}
          >
            {task.completed && <CheckCircleIcon className="w-5 h-5 text-white" />}
          </motion.button>

          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Title and priority */}
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <h3
                  className={`text-lg font-semibold transition-all ${
                    task.completed ? "line-through text-gray-400" : "text-white"
                  }`}
                >
                  {task.title}
                </h3>
                {task.description && (
                  <p className={`text-sm mt-1 ${task.completed ? "text-gray-500" : "text-gray-400"}`}>
                    {task.description}
                  </p>
                )}
              </div>

              {/* Priority badge */}
              <div className="relative">
                <PriorityBadge
                  priority={task.priority}
                  onClick={() => onPriorityChange && setShowPrioritySelector(!showPrioritySelector)}
                  size="sm"
                />

                {/* Priority selector popup */}
                <AnimatePresence>
                  {showPrioritySelector && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="absolute right-0 top-full mt-2 z-20"
                    >
                      <div className="glass-dark rounded-xl p-3 shadow-2xl border border-white/10">
                        <PrioritySelectorWrapper
                          value={task.priority}
                          onChange={(priority) => {
                            onPriorityChange?.(task.id, priority);
                            setShowPrioritySelector(false);
                          }}
                        />
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>

            {/* Meta info */}
            <div className="flex flex-wrap items-center gap-3 mt-3">
              {/* Due date */}
              {task.dueDate && dueDateInfo && (
                <div className={`flex items-center gap-1.5 text-xs ${dueDateInfo.color}`}>
                  <CalendarIcon className="w-4 h-4" />
                  <span className="font-medium">{dueDateInfo.text}</span>
                </div>
              )}

              {/* Recurring indicator */}
              {task.isRecurring && (
                <div className="flex items-center gap-1.5 text-xs text-purple-400">
                  <ClockIcon className="w-4 h-4" />
                  <span className="font-medium">{formatRecurrence(task.recurrenceRule)}</span>
                </div>
              )}

              {/* Tags */}
              {task.tags.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {task.tags.slice(0, 3).map((tag) => (
                    <TagBadge key={tag.id} tag={tag} size="sm" />
                  ))}
                  {task.tags.length > 3 && (
                    <span className="text-xs text-gray-400">+{task.tags.length - 3}</span>
                  )}
                </div>
              )}
            </div>

            {/* Tags preview if many */}
            {task.tags.length > 0 && isExpanded && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="flex flex-wrap gap-1.5 mt-2"
              >
                {task.tags.map((tag) => (
                  <TagBadge key={tag.id} tag={tag} size="sm" />
                ))}
              </motion.div>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <motion.button
              whileHover={{ scale: 1.1, rotate: 5 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => onEdit(task)}
              className="p-2 text-blue-400 hover:bg-blue-500/20 rounded-xl transition-colors"
              title="Edit task"
            >
              <PencilIcon className="w-5 h-5" />
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.1, rotate: -5 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => onDelete(task.id)}
              className="p-2 text-red-400 hover:bg-red-500/20 rounded-xl transition-colors"
              title="Delete task"
            >
              <TrashIcon className="w-5 h-5" />
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 text-gray-400 hover:bg-white/10 rounded-xl transition-colors"
              title={isExpanded ? "Collapse" : "Expand"}
            >
              {isExpanded ? (
                <ChevronUpIcon className="w-5 h-5" />
              ) : (
                <ChevronDownIcon className="w-5 h-5" />
              )}
            </motion.button>
          </div>
        </div>

        {/* Expanded content */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 pt-4 border-t border-white/10"
            >
              {/* Full tag list */}
              {task.tags.length > 0 && (
                <div className="mb-4">
                  <div className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                    <TagIcon className="w-4 h-4" />
                    <span>Tags</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {task.tags.map((tag) => (
                      <TagBadge key={tag.id} tag={tag} />
                    ))}
                  </div>
                </div>
              )}

              {/* Created/Updated dates */}
              <div className="flex gap-4 text-xs text-gray-500">
                <span>Created: {new Date(task.createdAt).toLocaleString()}</span>
                <span>Updated: {new Date(task.updatedAt).toLocaleString()}</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}

// Wrapper component for priority selector to avoid forward ref issues
function PrioritySelectorWrapper({
  value,
  onChange,
}: {
  value: Priority;
  onChange: (priority: Priority) => void;
}) {
  const priorities: Priority[] = ["none", "low", "medium", "high", "urgent"];
  const priorityConfig: Record<Priority, { gradient: string; label: string }> = {
    none: { gradient: "from-gray-500 to-gray-600", label: "None" },
    low: { gradient: "from-green-500 to-emerald-600", label: "Low" },
    medium: { gradient: "from-blue-500 to-cyan-600", label: "Medium" },
    high: { gradient: "from-orange-500 to-yellow-600", label: "High" },
    urgent: { gradient: "from-red-500 to-pink-600", label: "Urgent" },
  };

  return (
    <div className="flex flex-col gap-1">
      {priorities.map((priority) => (
        <motion.button
          key={priority}
          whileHover={{ scale: 1.02, x: 4 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => onChange(priority)}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all text-left ${
            value === priority
              ? `bg-gradient-to-r ${priorityConfig[priority].gradient} text-white`
              : "text-gray-300 hover:bg-white/10"
          }`}
        >
          {priorityConfig[priority].label}
        </motion.button>
      ))}
    </div>
  );
}
