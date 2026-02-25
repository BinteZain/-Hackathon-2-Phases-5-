"use client";

import { useState, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  CheckCircleIcon,
  PlusIcon,
  SparklesIcon,
  CloudIcon,
  CpuChipIcon,
  SunIcon,
  MoonIcon,
  RocketLaunchIcon,
  BoltIcon,
  ChartBarIcon,
  CalendarIcon,
  ClockIcon,
  TagIcon,
  FunnelIcon,
  ArrowRightOnRectangleIcon,
  UserCircleIcon,
} from "@heroicons/react/24/solid";
import TaskCard from "../components/TaskCard";
import TaskModal from "../components/TaskModal";
import SearchBar from "../components/SearchBar";
import StatsCard from "../components/StatsCard";
import ToastContainer from "../components/Toast";
import PriorityBadge, { Priority } from "../components/PriorityBadge";
import { Tag } from "../components/TagBadge";
import AuthGuard from "../components/AuthGuard";
import { useAuth } from "./context/AuthContext";

// Generate unique ID
const generateId = () => Math.random().toString(36).substring(2, 15);

// Floating bubble component
function FloatingBubble({ delay, size, left }: { delay: number; size: string; left: string }) {
  return (
    <motion.div
      className={`absolute rounded-full glass-light ${size} opacity-20`}
      style={{ left }}
      animate={{
        y: [0, -100, 0],
        x: [0, 30, 0],
        rotate: [0, 180, 360],
      }}
      transition={{
        duration: 8,
        delay,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    />
  );
}

// Main Home Component
export default function Home() {
  const { user, logout } = useAuth();
  
  // State
  const [tasks, setTasks] = useState<Array<{
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
  }>>([]);
  const [loading, setLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState<{
    status?: "all" | "active" | "completed";
    priority?: Priority | "all";
    tags?: string[];
    sortBy?: "created" | "dueDate" | "priority" | "title";
    sortOrder?: "asc" | "desc";
  }>({
    status: "all",
    priority: "all",
    sortBy: "created",
    sortOrder: "desc",
  });
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<any>(null);
  const [toasts, setToasts] = useState<Array<{ id: string; type: "success" | "error" | "warning" | "info"; message: string; title?: string }>>([]);

  // Load tasks from localStorage
  useEffect(() => {
    const storedTasks = localStorage.getItem("phase5-tasks");
    if (storedTasks) {
      try {
        setTasks(JSON.parse(storedTasks));
      } catch (e) {
        console.error("Failed to parse tasks");
        addToast("error", "Failed to load tasks", "Data corrupted");
      }
    } else {
      // Add sample tasks for demo
      const sampleTasks = [
        {
          id: generateId(),
          title: "Welcome to Todo Chatbot! 🎉",
          description: "This is your first task. Click to edit or complete it.",
          completed: false,
          priority: "high" as Priority,
          dueDate: new Date(Date.now() + 86400000).toISOString(),
          tags: [{ id: "tag-1", name: "Getting Started", color: "indigo" }],
          isRecurring: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
        {
          id: generateId(),
          title: "Try the recurring tasks feature",
          description: "Create a task that repeats daily, weekly, or monthly",
          completed: false,
          priority: "medium" as Priority,
          dueDate: new Date(Date.now() + 172800000).toISOString(),
          tags: [{ id: "tag-2", name: "Features", color: "purple" }],
          isRecurring: true,
          recurrenceRule: "FREQ=WEEKLY",
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
        {
          id: generateId(),
          title: "Explore the beautiful UI ✨",
          description: "Enjoy glassmorphism, animations, and modern design",
          completed: true,
          priority: "low" as Priority,
          tags: [{ id: "tag-3", name: "Design", color: "pink" }],
          isRecurring: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ];
      setTasks(sampleTasks);
    }
    setLoading(false);
  }, []);

  // Save tasks to localStorage
  useEffect(() => {
    if (!loading) {
      localStorage.setItem("phase5-tasks", JSON.stringify(tasks));
    }
  }, [tasks, loading]);

  // Toast helpers
  const addToast = (type: "success" | "error" | "warning" | "info", message: string, title?: string) => {
    const id = generateId();
    setToasts((prev) => [...prev, { id, type, message, title }]);
  };

  const dismissToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // Task handlers
  const addTask = (taskData: {
    title: string;
    description?: string;
    priority: Priority;
    dueDate?: string;
    tags: Tag[];
    isRecurring: boolean;
    recurrenceRule?: string;
  }) => {
    const newTask = {
      ...taskData,
      id: generateId(),
      completed: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setTasks([newTask, ...tasks]);
    addToast("success", "Task created successfully", "🎉 New task added");
  };

  const updateTask = (taskData: {
    title: string;
    description?: string;
    priority: Priority;
    dueDate?: string;
    tags: Tag[];
    isRecurring: boolean;
    recurrenceRule?: string;
  }) => {
    if (!editingTask) return;
    setTasks(
      tasks.map((t) =>
        t.id === editingTask.id
          ? { ...t, ...taskData, updatedAt: new Date().toISOString() }
          : t
      )
    );
    addToast("success", "Task updated successfully", "✓ Changes saved");
    setEditingTask(null);
  };

  const toggleTask = (id: string) => {
    setTasks(
      tasks.map((t) =>
        t.id === id
          ? { ...t, completed: !t.completed, updatedAt: new Date().toISOString() }
          : t
      )
    );
    const task = tasks.find((t) => t.id === id);
    if (task) {
      addToast(
        task.completed ? "info" : "success",
        task.completed ? "Task marked as active" : "🎉 Task completed!",
        task.completed ? "Reactivated" : "Great job!"
      );
    }
  };

  const deleteTask = (id: string) => {
    setTasks(tasks.filter((t) => t.id !== id));
    addToast("warning", "Task deleted", "Trash");
  };

  const updateTaskPriority = (id: string, priority: Priority) => {
    setTasks(
      tasks.map((t) =>
        t.id === id ? { ...t, priority, updatedAt: new Date().toISOString() } : t
      )
    );
  };

  // Filter and sort tasks
  const filteredTasks = useMemo(() => {
    let result = [...tasks];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (task) =>
          task.title.toLowerCase().includes(query) ||
          task.description?.toLowerCase().includes(query) ||
          task.tags.some((tag) => tag.name.toLowerCase().includes(query))
      );
    }

    // Status filter
    if (filters.status === "active") {
      result = result.filter((task) => !task.completed);
    } else if (filters.status === "completed") {
      result = result.filter((task) => task.completed);
    }

    // Priority filter
    if (filters.priority && filters.priority !== "all") {
      result = result.filter((task) => task.priority === filters.priority);
    }

    // Tag filter
    if (filters.tags && filters.tags.length > 0) {
      result = result.filter((task) =>
        task.tags.some((tag) => filters.tags?.includes(tag.id))
      );
    }

    // Sort
    result.sort((a, b) => {
      let comparison = 0;
      switch (filters.sortBy) {
        case "created":
          comparison = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
          break;
        case "dueDate":
          if (!a.dueDate && !b.dueDate) return 0;
          if (!a.dueDate) return 1;
          if (!b.dueDate) return -1;
          comparison = new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
          break;
        case "priority":
          const priorityOrder = { urgent: 4, high: 3, medium: 2, low: 1, none: 0 };
          comparison = priorityOrder[a.priority] - priorityOrder[b.priority];
          break;
        case "title":
          comparison = a.title.localeCompare(b.title);
          break;
      }
      return filters.sortOrder === "desc" ? -comparison : comparison;
    });

    return result;
  }, [tasks, searchQuery, filters]);

  // Get all unique tags
  const allTags = useMemo(() => {
    const tagMap = new Map<string, Tag>();
    tasks.forEach((task) => {
      task.tags.forEach((tag) => {
        tagMap.set(tag.id, tag);
      });
    });
    return Array.from(tagMap.values());
  }, [tasks]);

  // Stats
  const stats = {
    total: tasks.length,
    active: tasks.filter((t) => !t.completed).length,
    completed: tasks.filter((t) => t.completed).length,
    urgent: tasks.filter((t) => t.priority === "urgent" && !t.completed).length,
    overdue: tasks.filter(
      (t) => t.dueDate && new Date(t.dueDate) < new Date() && !t.completed
    ).length,
  };

  return (
    <AuthGuard>
      <div className={`min-h-screen gradient-bg relative overflow-hidden ${darkMode ? "dark" : ""}`}>
        {/* Animated background */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(15)].map((_, i) => (
            <FloatingBubble
              key={i}
              delay={i * 0.4}
              size={i % 3 === 0 ? "w-24 h-24" : i % 3 === 1 ? "w-16 h-16" : "w-10 h-10"}
              left={`${Math.random() * 100}%`}
            />
          ))}
        </div>

        {/* Gradient orbs */}
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-purple-500/20 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-cyan-500/20 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: "2s" }} />
        <div className="absolute top-1/2 left-1/2 w-[400px] h-[400px] bg-pink-500/15 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: "4s" }} />

        {/* Toast notifications */}
        <ToastContainer toasts={toasts} onDismiss={dismissToast} />

        {/* Main content */}
        <div className="relative z-10 container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <motion.header
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between flex-wrap gap-4">
            {/* Logo and title */}
            <div className="flex items-center gap-4">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                className="relative"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-2xl blur-lg opacity-50" />
                <div className="relative glass-light p-3 rounded-2xl">
                  <CpuChipIcon className="w-10 h-10 text-cyan-400" />
                </div>
              </motion.div>
              <div>
                <h1 className="text-4xl md:text-5xl font-black gradient-text neon-glow">
                  Todo Chatbot
                </h1>
                <p className="text-gray-300 flex items-center gap-2 mt-1">
                  <SparklesIcon className="w-4 h-4 text-yellow-400" />
                  AI-Powered Task Management
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-3">
              {/* User Profile */}
              {user && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="glass-light px-4 py-2 rounded-xl flex items-center gap-2"
                >
                  <UserCircleIcon className="w-6 h-6 text-purple-400" />
                  <span className="text-sm font-semibold text-gray-200 hidden sm:inline">
                    {user.name}
                  </span>
                </motion.div>
              )}

              {/* Theme toggle */}
              <motion.button
                whileHover={{ scale: 1.1, rotate: 15 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => setDarkMode(!darkMode)}
                className="glass-light p-3 rounded-xl btn-glow"
              >
                {darkMode ? (
                  <SunIcon className="w-6 h-6 text-yellow-400" />
                ) : (
                  <MoonIcon className="w-6 h-6 text-indigo-400" />
                )}
              </motion.button>

              {/* Logout button */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={logout}
                className="glass-light p-3 rounded-xl btn-glow hover:bg-red-500/20 transition-colors"
                title="Logout"
              >
                <ArrowRightOnRectangleIcon className="w-6 h-6 text-red-400" />
              </motion.button>

              {/* Add task button */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  setEditingTask(null);
                  setIsModalOpen(true);
                }}
                className="px-6 py-3 bg-gradient-to-r from-purple-500 via-pink-500 to-cyan-500 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
              >
                <PlusIcon className="w-5 h-5" />
                <span className="hidden sm:inline">New Task</span>
              </motion.button>
            </div>
          </div>

          {/* Feature badges */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="flex flex-wrap gap-3 mt-6"
          >
            <div className="glass-light px-4 py-2 rounded-full flex items-center gap-2">
              <RocketLaunchIcon className="w-4 h-4 text-purple-400" />
              <span className="text-sm text-gray-300">Kubernetes</span>
            </div>
            <div className="glass-light px-4 py-2 rounded-full flex items-center gap-2">
              <BoltIcon className="w-4 h-4 text-yellow-400" />
              <span className="text-sm text-gray-300">Event-Driven</span>
            </div>
            <div className="glass-light px-4 py-2 rounded-full flex items-center gap-2">
              <ChartBarIcon className="w-4 h-4 text-cyan-400" />
              <span className="text-sm text-gray-300">Real-time</span>
            </div>
            <div className="glass-light px-4 py-2 rounded-full flex items-center gap-2">
              <CloudIcon className="w-4 h-4 text-pink-400" />
              <span className="text-sm text-gray-300">Cloud-Native</span>
            </div>
          </motion.div>
        </motion.header>

        {/* Stats */}
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
        >
          <StatsCard
            icon={ChartBarIcon}
            label="Total Tasks"
            value={stats.total}
            gradient="from-purple-500 to-pink-500"
            delay={0.7}
          />
          <StatsCard
            icon={ClockIcon}
            label="Active"
            value={stats.active}
            gradient="from-cyan-500 to-blue-500"
            delay={0.8}
          />
          <StatsCard
            icon={CheckCircleIcon}
            label="Completed"
            value={stats.completed}
            gradient="from-green-500 to-emerald-500"
            delay={0.9}
          />
          <StatsCard
            icon={BoltIcon}
            label="Urgent"
            value={stats.urgent}
            gradient="from-orange-500 to-red-500"
            delay={1.0}
          />
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1 }}
          className="mb-6"
        >
          <SearchBar
            value={searchQuery}
            onChange={setSearchQuery}
            onFilterChange={setFilters}
            tags={allTags}
            totalTasks={filteredTasks.length}
          />
        </motion.div>

        {/* Task List */}
        <motion.div
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1.2 }}
        >
          {loading ? (
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="glass-light rounded-2xl p-6 animate-pulse">
                  <div className="flex items-center gap-4">
                    <div className="w-6 h-6 rounded-full bg-white/10" />
                    <div className="flex-1 h-6 bg-white/10 rounded" />
                    <div className="w-20 h-8 bg-white/10 rounded-xl" />
                  </div>
                </div>
              ))}
            </div>
          ) : filteredTasks.length === 0 ? (
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="glass-dark rounded-3xl p-16 text-center"
            >
              <div className="glass-light w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-6">
                <CalendarIcon className="w-12 h-12 text-gray-500" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">
                {searchQuery || hasActiveFilters(filters) ? "No matching tasks" : "No tasks yet"}
              </h3>
              <p className="text-gray-400 mb-6">
                {searchQuery || hasActiveFilters(filters)
                  ? "Try adjusting your search or filters"
                  : "Add your first task to get started!"}
              </p>
              {!searchQuery && !hasActiveFilters(filters) && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => {
                    setEditingTask(null);
                    setIsModalOpen(true);
                  }}
                  className="px-8 py-4 bg-gradient-to-r from-purple-500 via-pink-500 to-cyan-500 text-white rounded-xl font-semibold shadow-lg"
                >
                  <PlusIcon className="w-5 h-5 inline mr-2" />
                  Create Your First Task
                </motion.button>
              )}
            </motion.div>
          ) : (
            <div className="space-y-4">
              <AnimatePresence mode="popLayout">
                {filteredTasks.map((task, index) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onToggle={toggleTask}
                    onDelete={deleteTask}
                    onEdit={(t) => {
                      setEditingTask(t);
                      setIsModalOpen(true);
                    }}
                    onPriorityChange={updateTaskPriority}
                  />
                ))}
              </AnimatePresence>
            </div>
          )}
        </motion.div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="mt-12 text-center"
        >
          <div className="glass-light inline-block px-8 py-5 rounded-2xl">
            <div className="flex items-center justify-center gap-3 mb-2">
              <CloudIcon className="w-5 h-5 text-purple-400" />
              <span className="text-gray-300 font-semibold">Data saved locally</span>
            </div>
            <p className="text-gray-500 text-sm">
              Your tasks are stored in your browser and persist across sessions
            </p>
          </div>
        </motion.footer>
      </div>

      {/* Task Modal */}
      <TaskModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingTask(null);
        }}
        onSubmit={editingTask ? updateTask : addTask}
        initialTask={editingTask}
        mode={editingTask ? "edit" : "create"}
      />
      </div>
    </AuthGuard>
  );
}

// Helper function
function hasActiveFilters(filters: any) {
  return (
    filters.status !== "all" ||
    filters.priority !== "all" ||
    (filters.tags && filters.tags.length > 0)
  );
}
