"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { XMarkIcon, CalendarIcon, ClockIcon, TagIcon, ArrowPathIcon } from "@heroicons/react/24/solid";
import TagBadge, { Tag } from "./TagBadge";
import PriorityBadge, { Priority, PrioritySelector } from "./PriorityBadge";

interface TaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (task: {
    title: string;
    description?: string;
    priority: Priority;
    dueDate?: string;
    tags: Tag[];
    isRecurring: boolean;
    recurrenceRule?: string;
  }) => void;
  initialTask?: {
    id: string;
    title: string;
    description?: string;
    priority: Priority;
    dueDate?: string;
    tags: Tag[];
    isRecurring: boolean;
    recurrenceRule?: string;
  };
  mode: "create" | "edit";
}

const recurrenceOptions = [
  { value: "", label: "Does not repeat" },
  { value: "FREQ=DAILY", label: "Daily" },
  { value: "FREQ=WEEKLY", label: "Weekly" },
  { value: "FREQ=MONTHLY", label: "Monthly" },
  { value: "FREQ=YEARLY", label: "Yearly" },
];

const tagColors = ["indigo", "purple", "pink", "blue", "cyan", "green", "yellow", "orange", "red", "rose", "teal", "emerald"];

export default function TaskModal({ isOpen, onClose, onSubmit, initialTask, mode }: TaskModalProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<Priority>("none");
  const [dueDate, setDueDate] = useState("");
  const [dueTime, setDueTime] = useState("");
  const [tags, setTags] = useState<Tag[]>([]);
  const [newTagName, setNewTagName] = useState("");
  const [selectedTagColor, setSelectedTagColor] = useState(tagColors[0]);
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurrenceRule, setRecurrenceRule] = useState("");

  useEffect(() => {
    if (initialTask && mode === "edit") {
      setTitle(initialTask.title);
      setDescription(initialTask.description || "");
      setPriority(initialTask.priority);
      setDueDate(initialTask.dueDate ? initialTask.dueDate.split("T")[0] : "");
      setTags(initialTask.tags || []);
      setIsRecurring(initialTask.isRecurring);
      setRecurrenceRule(initialTask.recurrenceRule || "");
    } else {
      resetForm();
    }
  }, [initialTask, mode, isOpen]);

  const resetForm = () => {
    setTitle("");
    setDescription("");
    setPriority("none");
    setDueDate("");
    setDueTime("");
    setTags([]);
    setNewTagName("");
    setIsRecurring(false);
    setRecurrenceRule("");
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) return;

    let fullDueDate: string | undefined;
    if (dueDate) {
      fullDueDate = dueTime ? `${dueDate}T${dueTime}` : dueDate;
    }

    onSubmit({
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
      dueDate: fullDueDate,
      tags,
      isRecurring,
      recurrenceRule: isRecurring ? recurrenceRule : undefined,
    });

    handleClose();
  };

  const addTag = () => {
    if (newTagName.trim()) {
      const newTag: Tag = {
        id: `tag-${Date.now()}`,
        name: newTagName.trim(),
        color: selectedTagColor,
      };
      setTags([...tags, newTag]);
      setNewTagName("");
      setSelectedTagColor(tagColors[(tagColors.indexOf(selectedTagColor) + 1) % tagColors.length]);
    }
  };

  const removeTag = (tagId: string) => {
    setTags(tags.filter((t) => t.id !== tagId));
  };

  const handleKeyDown = (e: React.KeyboardEvent, action: () => void) => {
    if (e.key === "Enter") {
      e.preventDefault();
      action();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: "spring", stiffness: 400, damping: 30 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
          >
            <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto pointer-events-auto">
              <div className="glass-dark rounded-3xl border border-white/10 shadow-2xl overflow-hidden">
                {/* Header */}
                <div className="relative bg-gradient-to-r from-purple-500/20 via-pink-500/20 to-cyan-500/20 p-6 border-b border-white/10">
                  <motion.button
                    whileHover={{ scale: 1.1, rotate: 90 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={handleClose}
                    className="absolute top-4 right-4 p-2 hover:bg-white/10 rounded-xl transition-colors"
                  >
                    <XMarkIcon className="w-6 h-6 text-gray-400" />
                  </motion.button>
                  <h2 className="text-2xl font-bold text-white">
                    {mode === "create" ? "✨ Create New Task" : "✏️ Edit Task"}
                  </h2>
                  <p className="text-gray-400 text-sm mt-1">
                    {mode === "create" ? "Add a new task to your list" : "Update task details"}
                  </p>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                  {/* Title */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Title <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="text"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      placeholder="What needs to be done?"
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent transition-all"
                      autoFocus
                    />
                  </div>

                  {/* Description */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Description
                    </label>
                    <textarea
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder="Add more details..."
                      rows={3}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent transition-all resize-none"
                    />
                  </div>

                  {/* Priority */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-3">
                      Priority
                    </label>
                    <PrioritySelector value={priority} onChange={setPriority} />
                  </div>

                  {/* Due Date & Time */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        <CalendarIcon className="w-4 h-4 inline mr-1" />
                        Due Date
                      </label>
                      <input
                        type="date"
                        value={dueDate}
                        onChange={(e) => setDueDate(e.target.value)}
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent transition-all"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        <ClockIcon className="w-4 h-4 inline mr-1" />
                        Due Time
                      </label>
                      <input
                        type="time"
                        value={dueTime}
                        onChange={(e) => setDueTime(e.target.value)}
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent transition-all"
                      />
                    </div>
                  </div>

                  {/* Tags */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      <TagIcon className="w-4 h-4 inline mr-1" />
                      Tags
                    </label>
                    <div className="flex flex-wrap gap-2 mb-3">
                      {tags.map((tag) => (
                        <TagBadge key={tag.id} tag={tag} onRemove={() => removeTag(tag.id)} />
                      ))}
                    </div>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={newTagName}
                        onChange={(e) => setNewTagName(e.target.value)}
                        onKeyDown={(e) => handleKeyDown(e, addTag)}
                        placeholder="Add a tag..."
                        className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent transition-all text-sm"
                      />
                      <div className="flex gap-1 items-center">
                        {tagColors.slice(0, 6).map((color) => (
                          <button
                            key={color}
                            type="button"
                            onClick={() => setSelectedTagColor(color)}
                            className={`w-6 h-6 rounded-full border-2 transition-all ${
                              selectedTagColor === color ? "border-white scale-110" : "border-transparent"
                            } bg-${color}-500`}
                          />
                        ))}
                      </div>
                      <motion.button
                        type="button"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={addTag}
                        className="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl text-sm font-medium"
                      >
                        Add
                      </motion.button>
                    </div>
                  </div>

                  {/* Recurring Toggle */}
                  <div className="glass-light rounded-xl p-4 border border-white/10">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <ArrowPathIcon className="w-5 h-5 text-purple-400" />
                        <span className="text-white font-medium">Recurring Task</span>
                      </div>
                      <motion.button
                        type="button"
                        onClick={() => setIsRecurring(!isRecurring)}
                        className={`relative w-14 h-7 rounded-full transition-colors ${
                          isRecurring ? "bg-gradient-to-r from-purple-500 to-pink-500" : "bg-white/10"
                        }`}
                      >
                        <motion.div
                          animate={{ x: isRecurring ? 28 : 4 }}
                          className="absolute top-1 w-5 h-5 bg-white rounded-full shadow-lg"
                        />
                      </motion.button>
                    </div>
                    {isRecurring && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        className="space-y-2"
                      >
                        <label className="block text-sm text-gray-300">Repeat</label>
                        <select
                          value={recurrenceRule}
                          onChange={(e) => setRecurrenceRule(e.target.value)}
                          className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent transition-all"
                        >
                          {recurrenceOptions.map((option) => (
                            <option key={option.value} value={option.value} className="bg-gray-800">
                              {option.label}
                            </option>
                          ))}
                        </select>
                      </motion.div>
                    )}
                  </div>

                  {/* Submit Button */}
                  <div className="flex gap-3 pt-4">
                    <motion.button
                      type="button"
                      onClick={handleClose}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="flex-1 px-6 py-3 bg-white/10 text-white rounded-xl font-medium hover:bg-white/20 transition-all"
                    >
                      Cancel
                    </motion.button>
                    <motion.button
                      type="submit"
                      whileHover={{ scale: 1.02, boxShadow: "0 0 30px rgba(168, 85, 247, 0.5)" }}
                      whileTap={{ scale: 0.98 }}
                      disabled={!title.trim()}
                      className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-500 via-pink-500 to-cyan-500 text-white rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                    >
                      {mode === "create" ? "🚀 Create Task" : "💾 Save Changes"}
                    </motion.button>
                  </div>
                </form>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
