import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AGI-MCP-Agent",
  description: "Autonomous agent framework with Master Control Program architecture",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex flex-col min-h-screen">
          <nav className="bg-white dark:bg-gray-900 shadow-md">
            <div className="max-w-6xl mx-auto px-4">
              <div className="flex justify-between h-16">
                <div className="flex">
                  <div className="flex-shrink-0 flex items-center">
                    <Link href="/" className="text-xl font-bold text-blue-600 dark:text-blue-400">
                      AGI-MCP-Agent
                    </Link>
                  </div>
                  <div className="hidden sm:ml-6 sm:flex">
                    <Link href="/" className="inline-flex items-center px-3 py-2 mx-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
                      Home
                    </Link>
                    <Link href="/environments" className="inline-flex items-center px-3 py-2 mx-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
                      Environments
                    </Link>
                  </div>
                </div>
                <div className="hidden sm:flex sm:items-center">
                  <a 
                    href="https://github.com/ot2net/agi-mcp-agent" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white px-3 py-2"
                  >
                    GitHub
                  </a>
                </div>
              </div>
            </div>
          </nav>
          <main className="flex-grow">{children}</main>
          <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
            <div className="max-w-6xl mx-auto px-4 py-6">
              <div className="text-center text-gray-500 dark:text-gray-400 text-sm">
                <p>© 2025 OT2.net - AGI-MCP-Agent is licensed under the MIT License</p>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
