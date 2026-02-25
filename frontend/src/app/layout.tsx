import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "./context/AuthContext";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Todo Chatbot - AI-Powered Task Management",
  description: "Cloud-native AI-powered todo chatbot deployed on Kubernetes with Helm",
  keywords: ["todo", "chatbot", "AI", "Kubernetes", "Cloud-Native", "Task Management"],
  authors: [{ name: "Hackathon Team" }],
  openGraph: {
    title: "Todo Chatbot - AI-Powered Task Management",
    description: "Cloud-native AI-powered todo chatbot deployed on Kubernetes with Helm",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
