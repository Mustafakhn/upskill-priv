import type { Metadata, Viewport } from "next";
import "./globals.css";
import { ThemeProvider } from "./contexts/ThemeContext";
import { AuthProvider } from "./contexts/AuthContext";
import Header from "./components/layout/Header";
import Footer from "./components/layout/Footer";
import LayoutContent from "./components/layout/LayoutContent";

export const metadata: Metadata = {
  title: "Upskill - Personalized Learning Platform",
  description: "AI-powered learning companion that helps you master any skill. From cooking to coding, guitar to gardening - find the best resources curated just for you.",
  keywords: "learning, education, AI, tutorials, courses, skills",
  manifest: "/manifest.json",
  icons: {
    icon: "/upskill-logo.svg",
    apple: "/upskill-logo.svg",
    shortcut: "/upskill-logo.svg",
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "Upskill",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: "#3b82f6",
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
