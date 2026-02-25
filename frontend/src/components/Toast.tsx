"use client";

import { motion, AnimatePresence } from "framer-motion";
import { XMarkIcon, CheckCircleIcon, ExclamationTriangleIcon, InformationCircleIcon } from "@heroicons/react/24/solid";

interface Toast {
  id: string;
  type: "success" | "error" | "warning" | "info";
  message: string;
  title?: string;
}

interface ToastProps {
  toast: Toast;
  onDismiss: (id: string) => void;
}

function ToastItem({ toast, onDismiss }: ToastProps) {
  const icons = {
    success: CheckCircleIcon,
    error: ExclamationTriangleIcon,
    warning: ExclamationTriangleIcon,
    info: InformationCircleIcon,
  };

  const colors = {
    success: "from-green-500 to-emerald-500",
    error: "from-red-500 to-pink-500",
    warning: "from-yellow-500 to-orange-500",
    info: "from-blue-500 to-cyan-500",
  };

  const bgColors = {
    success: "bg-green-500/10 border-green-500/30",
    error: "bg-red-500/10 border-red-500/30",
    warning: "bg-yellow-500/10 border-yellow-500/30",
    info: "bg-blue-500/10 border-blue-500/30",
  };

  const Icon = icons[toast.type];

  return (
    <motion.div
      initial={{ x: 400, opacity: 0, scale: 0.9 }}
      animate={{ x: 0, opacity: 1, scale: 1 }}
      exit={{ x: 400, opacity: 0, scale: 0.9 }}
      transition={{ type: "spring", stiffness: 500, damping: 30 }}
      className={`relative overflow-hidden rounded-2xl border backdrop-blur-xl ${bgColors[toast.type]} p-4 shadow-2xl`}
    >
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-xl bg-gradient-to-br ${colors[toast.type]}`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          {toast.title && (
            <p className="font-semibold text-white text-sm mb-1">{toast.title}</p>
          )}
          <p className="text-gray-200 text-sm">{toast.message}</p>
        </div>
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => onDismiss(toast.id)}
          className="p-1 hover:bg-white/10 rounded-lg transition-colors"
        >
          <XMarkIcon className="w-5 h-5 text-gray-400" />
        </motion.button>
      </div>
      <motion.div
        className={`absolute bottom-0 left-0 h-1 bg-gradient-to-r ${colors[toast.type]}`}
        initial={{ width: "100%" }}
        animate={{ width: "0%" }}
        transition={{ duration: 4, ease: "linear" }}
        onAnimationComplete={() => onDismiss(toast.id)}
      />
    </motion.div>
  );
}

export default function ToastContainer({ toasts, onDismiss }: { toasts: Toast[]; onDismiss: (id: string) => void }) {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-3 max-w-md">
      <AnimatePresence>
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onDismiss={onDismiss} />
        ))}
      </AnimatePresence>
    </div>
  );
}
