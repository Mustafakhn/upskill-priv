import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "./contexts/ThemeContext";
import { AuthProvider } from "./contexts/AuthContext";
import Header from "./components/layout/Header";
import Footer from "./components/layout/Footer";
import LayoutContent from "./components/layout/LayoutContent";

export const metadata: Metadata = {
  title: "Inurek - Master Any Skill",
  description: "AI-powered learning companion that helps you master any skill. From cooking to coding, guitar to gardening - find the best resources curated just for you.",
  keywords: "learning, education, AI, tutorials, courses, skills",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen flex flex-col" suppressHydrationWarning>
        <ThemeProvider>
          <AuthProvider>
            <Header />
            <main className="flex-1">
        {children}
            </main>
            <LayoutContent />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
