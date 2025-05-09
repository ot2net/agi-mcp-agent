import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AGI-MCP-Agent",
  description: "An intelligent agent framework based on Master Control Program architecture",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-b from-white to-gray-100 dark:from-gray-900 dark:to-gray-800">
          {/* Navigation Bar */}
          <nav className="bg-white shadow-sm dark:bg-gray-800">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex">
                  <div className="flex-shrink-0 flex items-center">
                    <Link href="/" className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                      AGI-MCP-Agent
                    </Link>
                  </div>
                  <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                    <Link href="/tasks" 
                          className="inline-flex items-center px-1 pt-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
                      Tasks
                    </Link>
                    <Link href="/agents"
                          className="inline-flex items-center px-1 pt-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
                      Agents
                    </Link>
                    <Link href="/environments"
                          className="inline-flex items-center px-1 pt-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
                      Environments
                    </Link>
                  </div>
                </div>
                <div className="flex items-center">
                  <a href="https://github.com/ot2net/agi-mcp-agent"
                     target="_blank"
                     rel="noopener noreferrer"
                     className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
                    GitHub
                  </a>
                </div>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>

          {/* Footer */}
          <footer className="bg-white shadow-sm dark:bg-gray-800 mt-auto">
            <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
              <div className="text-center text-gray-500 dark:text-gray-400">
                <p>© 2024 AGI-MCP-Agent. All rights reserved.</p>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
