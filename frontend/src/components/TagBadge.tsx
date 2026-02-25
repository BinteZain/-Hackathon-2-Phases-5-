"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { XMarkIcon } from "@heroicons/react/24/solid";

export interface Tag {
  id: string;
  name: string;
  color: string;
}

interface TagBadgeProps {
  tag: Tag;
  onRemove?: () => void;
  clickable?: boolean;
  selected?: boolean;
  onClick?: () => void;
  size?: "sm" | "md" | "lg";
}

const colorVariants: Record<string, string> = {
  red: "bg-red-500/20 border-red-500/50 text-red-300 hover:bg-red-500/30",
  orange: "bg-orange-500/20 border-orange-500/50 text-orange-300 hover:bg-orange-500/30",
  yellow: "bg-yellow-500/20 border-yellow-500/50 text-yellow-300 hover:bg-yellow-500/30",
  green: "bg-green-500/20 border-green-500/50 text-green-300 hover:bg-green-500/30",
  emerald: "bg-emerald-500/20 border-emerald-500/50 text-emerald-300 hover:bg-emerald-500/30",
  teal: "bg-teal-500/20 border-teal-500/50 text-teal-300 hover:bg-teal-500/30",
  cyan: "bg-cyan-500/20 border-cyan-500/50 text-cyan-300 hover:bg-cyan-500/30",
  blue: "bg-blue-500/20 border-blue-500/50 text-blue-300 hover:bg-blue-500/30",
  indigo: "bg-indigo-500/20 border-indigo-500/50 text-indigo-300 hover:bg-indigo-500/30",
  purple: "bg-purple-500/20 border-purple-500/50 text-purple-300 hover:bg-purple-500/30",
  pink: "bg-pink-500/20 border-pink-500/50 text-pink-300 hover:bg-pink-500/30",
  rose: "bg-rose-500/20 border-rose-500/50 text-rose-300 hover:bg-rose-500/30",
};

export default function TagBadge({ tag, onRemove, clickable, selected, onClick, size = "md" }: TagBadgeProps) {
  const sizeClasses = {
    sm: "px-2 py-1 text-xs",
    md: "px-3 py-1.5 text-sm",
    lg: "px-4 py-2 text-base",
  };

  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0.8, opacity: 0 }}
      whileHover={clickable || onRemove ? { scale: 1.05, y: -2 } : {}}
      whileTap={clickable || onRemove ? { scale: 0.95 } : {}}
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border backdrop-blur-sm transition-all cursor-pointer ${
        colorVariants[tag.color] || colorVariants.indigo
      } ${selected ? "ring-2 ring-white/50" : ""} ${sizeClasses[size]}`}
    >
      <span>{tag.name}</span>
      {onRemove && (
        <motion.button
          whileHover={{ scale: 1.2 }}
          whileTap={{ scale: 0.8 }}
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="p-0.5 hover:bg-white/20 rounded-full transition-colors"
        >
          <XMarkIcon className="w-3.5 h-3.5" />
        </motion.button>
      )}
    </motion.div>
  );
}

export function TagInput({
  tags,
  onAddTag,
  onRemoveTag,
  availableColors,
}: {
  tags: Tag[];
  onAddTag: (name: string, color: string) => void;
  onRemoveTag: (tagId: string) => void;
  availableColors?: string[];
}) {
  const defaultColors = ["indigo", "purple", "pink", "blue", "cyan", "green", "yellow", "orange", "red"];
  const colors = availableColors || defaultColors;
  const [newTag, setNewTag] = useState("");
  const [selectedColor, setSelectedColor] = useState(colors[0]);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newTag.trim()) {
      onAddTag(newTag.trim(), selectedColor);
      setNewTag("");
      setSelectedColor(colors[(colors.indexOf(selectedColor) + 1) % colors.length]);
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <TagBadge key={tag.id} tag={tag} onRemove={() => onRemoveTag(tag.id)} />
        ))}
      </div>
      <motion.form
        onSubmit={handleSubmit}
        className="flex gap-2"
        initial={false}
        animate={{ height: "auto" }}
      >
        <input
          type="text"
          value={newTag}
          onChange={(e) => setNewTag(e.target.value)}
          onFocus={() => setIsExpanded(true)}
          onBlur={() => setIsExpanded(false)}
          placeholder="Add a tag..."
          className="flex-1 px-3 py-2 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent text-sm"
        />
        <div className="flex items-center gap-1">
          <div className="flex gap-1">
            {colors.slice(0, isExpanded ? colors.length : 5).map((color) => (
              <button
                key={color}
                type="button"
                onClick={() => setSelectedColor(color)}
                className={`w-6 h-6 rounded-full border-2 transition-all ${
                  selectedColor === color ? "border-white scale-110" : "border-transparent hover:scale-105"
                }`}
                style={{ backgroundColor: `var(--color-${color}-500)` }}
              >
                <span className={`w-full h-full rounded-full bg-${color}-500`} />
              </button>
            ))}
          </div>
          <motion.button
            type="submit"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={!newTag.trim()}
            className="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Add
          </motion.button>
        </div>
      </motion.form>
    </div>
  );
}
