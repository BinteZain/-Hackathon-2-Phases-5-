"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  signup: (name: string, email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Load user from localStorage on mount
  useEffect(() => {
    const storedUser = localStorage.getItem("auth-user");
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error("Failed to parse stored user");
        localStorage.removeItem("auth-user");
      }
    }
    setLoading(false);
  }, []);

  // Login function
  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      // Get users from localStorage
      const users = JSON.parse(localStorage.getItem("registered-users") || "[]");
      
      // Find user by email
      const foundUser = users.find((u: any) => u.email === email);
      
      if (!foundUser) {
        return { success: false, error: "User not found. Please sign up first." };
      }
      
      // Check password
      if (foundUser.password !== password) {
        return { success: false, error: "Invalid password. Please try again." };
      }
      
      // Create user object (without password)
      const loggedInUser = {
        id: foundUser.id,
        email: foundUser.email,
        name: foundUser.name,
      };
      
      // Save to localStorage
      setUser(loggedInUser);
      localStorage.setItem("auth-user", JSON.stringify(loggedInUser));
      
      return { success: true };
    } catch (error) {
      console.error("Login error:", error);
      return { success: false, error: "An error occurred during login." };
    }
  };

  // Signup function
  const signup = async (name: string, email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      // Get existing users
      const users = JSON.parse(localStorage.getItem("registered-users") || "[]");
      
      // Check if user already exists
      const existingUser = users.find((u: any) => u.email === email);
      
      if (existingUser) {
        return { success: false, error: "User with this email already exists. Please login." };
      }
      
      // Create new user
      const newUser = {
        id: `user-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
        name,
        email,
        password, // In production, this should be hashed
      };
      
      // Save to users array
      users.push(newUser);
      localStorage.setItem("registered-users", JSON.stringify(users));
      
      // Auto login
      const loggedInUser = {
        id: newUser.id,
        email: newUser.email,
        name: newUser.name,
      };
      
      setUser(loggedInUser);
      localStorage.setItem("auth-user", JSON.stringify(loggedInUser));
      
      return { success: true };
    } catch (error) {
      console.error("Signup error:", error);
      return { success: false, error: "An error occurred during signup." };
    }
  };

  // Logout function
  const logout = () => {
    setUser(null);
    localStorage.removeItem("auth-user");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        signup,
        logout,
        isAuthenticated: !!user && !loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
