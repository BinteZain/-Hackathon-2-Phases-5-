"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  MagnifyingGlassIcon,
  XMarkIcon,
  FunnelIcon,
  ChevronDownIcon,
} from "@heroicons/react/24/solid";
import { Priority } from "./PriorityBadge";
import { Tag } from "./TagBadge";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onFilterChange?: (filters: FilterOptions) => void;
  tags?: Tag[];
  totalTasks?: number;
}

interface FilterOptions {
  status?: "all" | "active" | "completed";
  priority?: Priority | "all";
  tags?: string[];
  sortBy?: "created" | "dueDate" | "priority" | "title";
  sortOrder?: "asc" | "desc";
}

export default function SearchBar({ value, onChange, onFilterChange, tags, totalTasks }: SearchBarProps) {
  const [isFocused, setIsFocused] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<FilterOptions>({
    status: "all",
    priority: "all",
    sortBy: "created",
    sortOrder: "desc",
  });

  const inputRef = useRef<HTMLInputElement>(null);

  const handleFilterChange = (key: keyof FilterOptions, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange?.(newFilters);
  };

  const clearFilters = () => {
    const defaultFilters: FilterOptions = {
      status: "all",
      priority: "all",
      sortBy: "created",
      sortOrder: "desc",
    };
    setFilters(defaultFilters);
    onFilterChange?.(defaultFilters);
  };

  const hasActiveFilters =
    filters.status !== "all" ||
    filters.priority !== "all" ||
    (filters.tags && filters.tags.length > 0);

  return (
    <div className="space-y-3">
      {/* Search and Filter Bar */}
      <div className="flex gap-3">
        {/* Search Input */}
        <motion.div
          className="flex-1 relative"
          initial={false}
          animate={{ scale: isFocused ? 1.02 : 1 }}
        >
          <div
            className={`relative rounded-2xl border backdrop-blur-xl transition-all ${
              isFocused
                ? "border-purple-500/50 shadow-lg shadow-purple-500/20"
                : "border-white/10"
            } bg-gradient-to-r from-white/10 to-white/5`}
          >
            <MagnifyingGlassIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              ref={inputRef}
              type="text"
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder="🔍 Search tasks..."
              className="w-full pl-12 pr-12 py-4 bg-transparent text-white placeholder-gray-400 focus:outline-none text-lg"
            />
            {value && (
              <motion.button
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                exit={{ scale: 0 }}
                onClick={() => {
                  onChange("");
                  inputRef.current?.focus();
                }}
                className="absolute right-4 top-1/2 -translate-y-1/2 p-1 hover:bg-white/10 rounded-lg transition-colors"
              >
                <XMarkIcon className="w-5 h-5 text-gray-400" />
              </motion.button>
            )}
          </div>
        </motion.div>

        {/* Filter Button */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowFilters(!showFilters)}
          className={`relative px-5 py-4 rounded-2xl font-medium transition-all border ${
            showFilters || hasActiveFilters
              ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white border-transparent shadow-lg"
              : "glass-light text-gray-300 border-white/10 hover:border-white/30"
          }`}
        >
          <FunnelIcon className="w-5 h-5" />
          {hasActiveFilters && (
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-xs flex items-center justify-center">
              !
            </span>
          )}
        </motion.button>
      </div>

      {/* Filter Panel */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="glass-dark rounded-2xl border border-white/10 overflow-hidden"
          >
            <div className="p-5 space-y-4">
              {/* Header */}
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">Filters</h3>
                {hasActiveFilters && (
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={clearFilters}
                    className="text-sm text-red-400 hover:text-red-300 transition-colors"
                  >
                    Clear all
                  </motion.button>
                )}
              </div>

              {/* Filter Options */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Status Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Status</label>
                  <div className="relative">
                    <select
                      value={filters.status}
                      onChange={(e) => handleFilterChange("status", e.target.value)}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white appearance-none focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent transition-all cursor-pointer"
                    >
                      <option value="all" className="bg-gray-800">All Tasks</option>
                      <option value="active" className="bg-gray-800">Active</option>
                      <option value="completed" className="bg-gray-800">Completed</option>
                    </select>
                    <ChevronDownIcon className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
                  </div>
                </div>

                {/* Priority Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Priority</label>
                  <div className="relative">
                    <select
                      value={filters.priority}
                      onChange={(e) => handleFilterChange("priority", e.target.value)}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white appearance-none focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent transition-all cursor-pointer"
                    >
                      <option value="all" className="bg-gray-800">All Priorities</option>
                      <option value="urgent" className="bg-gray-800">🔴 Urgent</option>
                      <option value="high" className="bg-gray-800">🟠 High</option>
                      <option value="medium" className="bg-gray-800">🔵 Medium</option>
                      <option value="low" className="bg-gray-800">🟢 Low</option>
                      <option value="none" className="bg-gray-800">⚪ None</option>
                    </select>
                    <ChevronDownIcon className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
                  </div>
                </div>

                {/* Sort By */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Sort By</label>
                  <div className="grid grid-cols-2 gap-2">
                    <select
                      value={filters.sortBy}
                      onChange={(e) => handleFilterChange("sortBy", e.target.value)}
                      className="px-3 py-3 bg-white/5 border border-white/10 rounded-xl text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent transition-all cursor-pointer"
                    >
                      <option value="created" className="bg-gray-800">Created</option>
                      <option value="dueDate" className="bg-gray-800">Due Date</option>
                      <option value="priority" className="bg-gray-800">Priority</option>
                      <option value="title" className="bg-gray-800">Title</option>
                    </select>
                    <select
                      value={filters.sortOrder}
                      onChange={(e) => handleFilterChange("sortOrder", e.target.value)}
                      className="px-3 py-3 bg-white/5 border border-white/10 rounded-xl text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent transition-all cursor-pointer"
                    >
                      <option value="desc" className="bg-gray-800">↓ Desc</option>
                      <option value="asc" className="bg-gray-800">↑ Asc</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Tag Filters */}
              {tags && tags.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Tags</label>
                  <div className="flex flex-wrap gap-2">
                    {tags.map((tag) => {
                      const isSelected = filters.tags?.includes(tag.id);
                      return (
                        <motion.button
                          key={tag.id}
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => {
                            const currentTags = filters.tags || [];
                            const newTags = isSelected
                              ? currentTags.filter((id) => id !== tag.id)
                              : [...currentTags, tag.id];
                            handleFilterChange("tags", newTags);
                          }}
                          className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-all ${
                            isSelected
                              ? `bg-${tag.color}-500/30 border-${tag.color}-500/50 text-white`
                              : `bg-${tag.color}-500/10 border-${tag.color}-500/30 text-${tag.color}-300`
                          }`}
                        >
                          {tag.name}
                        </motion.button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Results count */}
              {totalTasks !== undefined && (
                <div className="pt-3 border-t border-white/10">
                  <p className="text-sm text-gray-400">
                    Showing <span className="text-white font-medium">{totalTasks}</span> tasks
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
