"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  CheckCircleIcon,
  TrashIcon,
  PlusIcon,
  SparklesIcon,
  CloudIcon,
  RocketLaunchIcon,
  CpuChipIcon,
  ChatBubbleLeftRightIcon,
  SunIcon,
  MoonIcon,
  ArrowPathIcon,
  ChartBarIcon,
  BoltIcon,
} from "@heroicons/react/24/solid";

interface Todo {
  id: string;
  title: string;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
}

interface ApiResponse {
  success: boolean;
  data?: Todo | Todo[];
  count?: number;
  error?: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";

// Floating bubble component
function FloatingBubble({ delay, size, left }: { delay: number; size: string; left: string }) {
  return (
    <motion.div
      className={`absolute rounded-full glass-light ${size} opacity-20`}
      style={{ left }}
      animate={{
        y: [0, -100, 0],
        x: [0, 30, 0],
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

// Loading skeleton component
function TodoSkeleton() {
  return (
    <div className="glass-light rounded-2xl p-4 mb-3 animate-pulse">
      <div className="flex items-center gap-4">
        <div className="w-6 h-6 rounded-full bg-white/10" />
        <div className="flex-1 h-5 bg-white/10 rounded" />
        <div className="w-16 h-8 bg-white/10 rounded-lg" />
      </div>
    </div>
  );
}

// Stat card component
function StatCard({ icon: Icon, label, value, gradient }: any) {
  return (
    <motion.div
      whileHover={{ scale: 1.05, y: -5 }}
      className={`glass-light rounded-2xl p-4 card-hover`}
    >
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-xl bg-gradient-to-br ${gradient}`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div>
          <p className="text-2xl font-bold text-white">{value}</p>
          <p className="text-xs text-gray-400">{label}</p>
        </div>
      </div>
    </motion.div>
  );
}

export default function Home() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTodo, setNewTodo] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "active" | "completed">("all");
  const [backendStatus, setBackendStatus] = useState<"connected" | "disconnected">("disconnected");
  const [darkMode, setDarkMode] = useState(true);
  const [isAdding, setIsAdding] = useState(false);

  const fetchTodos = async () => {
    try {
      const res = await fetch(`${API_URL}/api/todos`);
      const data: ApiResponse = await res.json();
      if (data.success && Array.isArray(data.data)) {
        setTodos(data.data);
      }
      setError(null);
    } catch (err) {
      setError("Failed to connect to backend");
      setBackendStatus("disconnected");
    } finally {
      setLoading(false);
    }
  };

  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_URL}/health`);
      if (res.ok) {
        setBackendStatus("connected");
      } else {
        setBackendStatus("disconnected");
      }
    } catch (err) {
      setBackendStatus("disconnected");
    }
  };

  useEffect(() => {
    fetchTodos();
    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  const addTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTodo.trim()) return;

    setIsAdding(true);
    try {
      const res = await fetch(`${API_URL}/api/todos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: newTodo }),
      });
      const data: ApiResponse = await res.json();
      if (data.success && data.data) {
        setTodos([...todos, data.data as Todo]);
        setNewTodo("");
      }
    } catch (err) {
      setError("Failed to add todo");
    } finally {
      setIsAdding(false);
    }
  };

  const toggleTodo = async (id: string, currentStatus: boolean) => {
    try {
      const res = await fetch(`${API_URL}/api/todos/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ completed: !currentStatus }),
      });
      const data: ApiResponse = await res.json();
      if (data.success && data.data) {
        setTodos(todos.map(t => t.id === id ? data.data! as Todo : t));
      }
    } catch (err) {
      setError("Failed to update todo");
    }
  };

  const deleteTodo = async (id: string) => {
    try {
      const res = await fetch(`${API_URL}/api/todos/${id}`, {
        method: "DELETE",
      });
      const data: ApiResponse = await res.json();
      if (data.success) {
        setTodos(todos.filter(t => t.id !== id));
      }
    } catch (err) {
      setError("Failed to delete todo");
    }
  };

  const deleteCompleted = async () => {
    try {
      const res = await fetch(`${API_URL}/api/todos/completed/all`, {
        method: "DELETE",
      });
      const data: ApiResponse = await res.json();
      if (data.success) {
        setTodos(todos.filter(t => !t.completed));
      }
    } catch (err) {
      setError("Failed to delete completed todos");
    }
  };

  const filteredTodos = todos.filter(todo => {
    if (filter === "active") return !todo.completed;
    if (filter === "completed") return todo.completed;
    return true;
  });

  const activeCount = todos.filter(t => !t.completed).length;
  const completedCount = todos.filter(t => t.completed).length;
  const totalCount = todos.length;

  return (
    <div className={`min-h-screen gradient-bg relative overflow-hidden ${darkMode ? 'dark' : ''}`}>
      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <FloatingBubble
            key={i}
            delay={i * 0.5}
            size={i % 3 === 0 ? 'w-20 h-20' : i % 3 === 1 ? 'w-12 h-12' : 'w-8 h-8'}
            left={`${Math.random() * 100}%`}
          />
        ))}
      </div>

      {/* Gradient orbs */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-500/30 rounded-full blur-3xl animate-pulse-slow" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-cyan-500/30 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '2s' }} />
      <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-pink-500/20 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '4s' }} />

      {/* Main content */}
      <div className="relative z-10 container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <motion.header
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-center mb-8"
        >
          {/* Theme toggle */}
          <div className="absolute top-4 right-4">
            <motion.button
              whileHover={{ scale: 1.1, rotate: 15 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setDarkMode(!darkMode)}
              className="glass-light p-3 rounded-full btn-glow"
            >
              {darkMode ? (
                <SunIcon className="w-6 h-6 text-yellow-400" />
              ) : (
                <MoonIcon className="w-6 h-6 text-indigo-400" />
              )}
            </motion.button>
          </div>

          {/* Logo and title */}
          <div className="flex items-center justify-center gap-3 mb-4">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
              <CpuChipIcon className="w-12 h-12 text-cyan-400 neon-glow-cyan" />
            </motion.div>
            <motion.h1
              className="text-5xl md:text-6xl font-black gradient-text neon-glow"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              Todo Chatbot
            </motion.h1>
            <motion.div
              animate={{ rotate: -360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
              <CloudIcon className="w-12 h-12 text-purple-400 neon-glow" />
            </motion.div>
          </div>

          {/* Subtitle */}
          <motion.p
            className="text-gray-300 text-lg mb-6 flex items-center justify-center gap-2"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <SparklesIcon className="w-5 h-5 text-yellow-400" />
            AI-Powered Cloud-Native Task Management
            <SparklesIcon className="w-5 h-5 text-yellow-400" />
          </motion.p>

          {/* Backend status */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.6, type: "spring" }}
            className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-semibold glass-light ${
              backendStatus === "connected"
                ? "border-green-500/50 shadow-[0_0_20px_rgba(34,197,94,0.4)]"
                : "border-red-500/50 shadow-[0_0_20px_rgba(239,68,68,0.4)]"
            }`}
          >
            <motion.span
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className={`w-3 h-3 rounded-full ${
                backendStatus === "connected" ? "bg-green-500" : "bg-red-500"
              }`}
            />
            <span className={backendStatus === "connected" ? "text-green-400" : "text-red-400"}>
              {backendStatus === "connected" ? "● Online" : "● Offline"}
            </span>
          </motion.div>

          {/* Feature badges */}
          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="flex flex-wrap justify-center gap-3 mt-6"
          >
            <div className="glass-light px-4 py-2 rounded-full flex items-center gap-2">
              <RocketLaunchIcon className="w-4 h-4 text-orange-400" />
              <span className="text-sm text-gray-300">Kubernetes Deployed</span>
            </div>
            <div className="glass-light px-4 py-2 rounded-full flex items-center gap-2">
              <BoltIcon className="w-4 h-4 text-yellow-400" />
              <span className="text-sm text-gray-300">AI-Driven</span>
            </div>
            <div className="glass-light px-4 py-2 rounded-full flex items-center gap-2">
              <ChartBarIcon className="w-4 h-4 text-cyan-400" />
              <span className="text-sm text-gray-300">Auto-Scaling</span>
            </div>
          </motion.div>
        </motion.header>

        {/* Stats cards */}
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1, duration: 0.8 }}
          className="grid grid-cols-3 gap-4 mb-8"
        >
          <StatCard
            icon={ChartBarIcon}
            label="Total Tasks"
            value={totalCount}
            gradient="from-purple-500 to-pink-500"
          />
          <StatCard
            icon={BoltIcon}
            label="Active"
            value={activeCount}
            gradient="from-cyan-500 to-blue-500"
          />
          <StatCard
            icon={CheckCircleIcon}
            label="Completed"
            value={completedCount}
            gradient="from-green-500 to-emerald-500"
          />
        </motion.div>

        {/* Error Message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ y: -20, opacity: 0, scale: 0.9 }}
              animate={{ y: 0, opacity: 1, scale: 1 }}
              exit={{ y: -20, opacity: 0, scale: 0.9 }}
              className="glass-light border-red-500/50 rounded-2xl p-4 mb-6 flex items-center justify-between shadow-[0_0_30px_rgba(239,68,68,0.3)]"
            >
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                <span className="text-red-400">{error}</span>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-red-400 hover:text-red-300 transition-colors text-xl"
              >
                ×
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main card */}
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1.2, duration: 0.8 }}
          className="glass-dark rounded-3xl p-6 md:p-8 shadow-glass"
        >
          {/* Add Todo Form */}
          <form onSubmit={addTodo} className="mb-6">
            <div className="relative">
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-purple-500 via-pink-500 to-cyan-500 rounded-2xl blur opacity-30"
                animate={{ opacity: [0.3, 0.5, 0.3] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
              <div className="relative glass-light rounded-2xl p-2 flex gap-2">
                <input
                  type="text"
                  value={newTodo}
                  onChange={(e) => setNewTodo(e.target.value)}
                  placeholder="✨ What needs to be done?"
                  className="flex-1 px-4 py-3 bg-transparent text-white placeholder-gray-400 focus:outline-none"
                />
                <motion.button
                  type="submit"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  disabled={isAdding || !newTodo.trim()}
                  className="px-6 py-3 bg-gradient-to-r from-purple-500 via-pink-500 to-cyan-500 text-white rounded-xl font-semibold btn-glow disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {isAdding ? (
                    <ArrowPathIcon className="w-5 h-5 animate-spin" />
                  ) : (
                    <PlusIcon className="w-5 h-5" />
                  )}
                  <span className="hidden sm:inline">Add</span>
                </motion.button>
              </div>
            </div>
          </form>

          {/* Filter Buttons */}
          <div className="flex flex-wrap gap-2 mb-6">
            {(["all", "active", "completed"] as const).map((f) => (
              <motion.button
                key={f}
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setFilter(f)}
                className={`px-5 py-2.5 rounded-xl font-semibold transition-all ${
                  filter === f
                    ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-neon"
                    : "glass-light text-gray-300 hover:bg-white/20"
                }`}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
                {f === "all" && ` (${totalCount})`}
                {f === "active" && ` (${activeCount})`}
                {f === "completed" && ` (${completedCount})`}
              </motion.button>
            ))}
          </div>

          {/* Clear completed button */}
          {completedCount > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-end mb-4"
            >
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={deleteCompleted}
                className="px-4 py-2 text-sm text-red-400 glass-light rounded-xl hover:bg-red-500/20 transition-all flex items-center gap-2"
              >
                <TrashIcon className="w-4 h-4" />
                Clear Completed
              </motion.button>
            </motion.div>
          )}

          {/* Todo List */}
          <div className="space-y-3">
            {loading ? (
              <>
                <TodoSkeleton />
                <TodoSkeleton />
                <TodoSkeleton />
              </>
            ) : filteredTodos.length === 0 ? (
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="text-center py-16"
              >
                <div className="glass-light w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-4">
                  <ChatBubbleLeftRightIcon className="w-12 h-12 text-gray-500" />
                </div>
                <p className="text-gray-400 text-lg">
                  {filter === "all"
                    ? "No tasks yet. Add your first one!"
                    : `No ${filter} tasks.`}
                </p>
              </motion.div>
            ) : (
              <AnimatePresence mode="popLayout">
                {filteredTodos.map((todo, index) => (
                  <motion.div
                    key={todo.id}
                    initial={{ x: -50, opacity: 0, scale: 0.8 }}
                    animate={{ x: 0, opacity: 1, scale: 1 }}
                    exit={{ x: 50, opacity: 0, scale: 0.8 }}
                    transition={{ delay: index * 0.05 }}
                    layout
                    className={`glass-light rounded-2xl p-4 card-hover group ${
                      todo.completed
                        ? "border-green-500/30 opacity-70"
                        : "border-purple-500/30"
                    }`}
                  >
                    <div className="flex items-center gap-4">
                      <motion.button
                        whileHover={{ scale: 1.2 }}
                        whileTap={{ scale: 0.8 }}
                        onClick={() => toggleTodo(todo.id, todo.completed)}
                        className={`w-7 h-7 rounded-full border-2 flex items-center justify-center transition-all ${
                          todo.completed
                            ? "bg-gradient-to-r from-green-500 to-emerald-500 border-transparent"
                            : "border-purple-500/50 hover:border-purple-400"
                        }`}
                      >
                        {todo.completed && (
                          <CheckCircleIcon className="w-5 h-5 text-white" />
                        )}
                      </motion.button>
                      <div className="flex-1 min-w-0 max-w-md">
                        <span
                          className={`text-lg block truncate ${
                            todo.completed
                              ? "line-through text-gray-500"
                              : "text-white"
                          }`}
                          title={todo.title}
                        >
                          {todo.title}
                        </span>
                      </div>
                      <motion.button
                        whileHover={{ scale: 1.1, rotate: 5 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={() => deleteTodo(todo.id)}
                        className="opacity-0 group-hover:opacity-100 px-4 py-2 text-red-400 hover:bg-red-500/20 rounded-xl transition-all flex-shrink-0"
                      >
                        <TrashIcon className="w-5 h-5" />
                      </motion.button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            )}
          </div>
        </motion.div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="mt-8 text-center"
        >
          <div className="glass-light inline-block px-6 py-4 rounded-2xl">
            <div className="flex items-center justify-center gap-2 mb-2">
              <RocketLaunchIcon className="w-5 h-5 text-purple-400" />
              <span className="text-gray-300 font-semibold">Deployed with Helm on Kubernetes</span>
            </div>
            <p className="text-gray-500 text-sm">
              Scale with: <code className="glass-dark px-2 py-1 rounded text-cyan-400">kubectl-ai "scale backend to 5 replicas"</code>
            </p>
          </div>
        </motion.footer>
      </div>
    </div>
  );
}
