import Image from "next/image";

export default function Home() {
  return (
    <div className="min-h-screen p-8 pb-20 gap-8 sm:p-12 bg-gradient-to-b from-white to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <header className="max-w-6xl mx-auto mb-12">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <h1 className="text-3xl font-bold text-blue-600 dark:text-blue-400">AGI-MCP-Agent</h1>
          </div>
          <div className="flex space-x-4">
            <a href="https://github.com/ot2net/agi-mcp-agent" target="_blank" rel="noopener noreferrer" 
               className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
              GitHub
            </a>
            <a href="https://ot2.net" target="_blank" rel="noopener noreferrer"
               className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
              OT2.net
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto">
        <section className="mb-16">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Overview</h2>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              AGI-MCP-Agent is an open-source intelligent agent framework designed to explore and implement 
              advanced agent capabilities through a Master Control Program (MCP) architecture. This project 
              aims to create a flexible, extensible platform for autonomous agents that can perform complex 
              tasks, learn from interactions, and coordinate multi-agent systems.
            </p>
            <a 
              href="https://ot2.net" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 dark:text-blue-400 hover:underline"
            >
              Visit OT2.net to learn more about our ecosystem and join our community!
            </a>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">Vision</h3>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                Our vision is to build a foundational framework for intelligent agents that can:
              </p>
              <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
                <li>Operate autonomously to solve complex problems</li>
                <li>Learn and adapt through interactions with the environment and other agents</li>
                <li>Integrate with various tools, APIs, and data sources</li>
                <li>Support multi-agent coordination and communication</li>
                <li>Provide researchers and developers with a flexible platform for AI experimentation</li>
              </ul>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">Technical Stack</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-blue-600 dark:text-blue-400 mb-2">Backend</h4>
                  <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-1">
                    <li>Python</li>
                    <li>FastAPI</li>
                    <li>Pydantic</li>
                    <li>SQLAlchemy</li>
                    <li>LangChain</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-blue-600 dark:text-blue-400 mb-2">Frontend</h4>
                  <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-1">
                    <li>React</li>
                    <li>Next.js</li>
                    <li>TypeScript</li>
                    <li>Tailwind CSS</li>
                    <li>Redux</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">Architecture</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-blue-600 dark:text-blue-400 mb-2">Master Control Program (MCP)</h4>
                <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-1">
                  <li>Manages agent lifecycles</li>
                  <li>Schedules and prioritizes tasks</li>
                  <li>Monitors performance and system health</li>
                  <li>Provides orchestration of multi-agent systems</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-blue-600 dark:text-blue-400 mb-2">Agent Framework</h4>
                <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-1">
                  <li>Cognitive processing (planning, reasoning, decision-making)</li>
                  <li>Memory management (short-term and long-term)</li>
                  <li>Tool/API integrations</li>
                  <li>Perception modules</li>
                  <li>Action generation</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Project Roadmap</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4">
              <div className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-lg px-3 py-1 text-sm inline-block mb-2">Phase 1: Foundation</div>
              <ul className="text-gray-700 dark:text-gray-300 text-sm space-y-1">
                <li>Core MCP implementation</li>
                <li>Basic agent capabilities</li>
                <li>Environment interface design</li>
                <li>Initial documentation</li>
              </ul>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4">
              <div className="bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded-lg px-3 py-1 text-sm inline-block mb-2">Phase 2: Expansion</div>
              <ul className="text-gray-700 dark:text-gray-300 text-sm space-y-1">
                <li>Advanced cognitive models</li>
                <li>Memory optimization</li>
                <li>Tool integration framework</li>
                <li>Performance benchmarks</li>
              </ul>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4">
              <div className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-lg px-3 py-1 text-sm inline-block mb-2">Phase 3: Multi-Agent</div>
              <ul className="text-gray-700 dark:text-gray-300 text-sm space-y-1">
                <li>Agent communication protocols</li>
                <li>Collaborative task solving</li>
                <li>Specialization and role assignment</li>
                <li>Swarm intelligence capabilities</li>
              </ul>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4">
              <div className="bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-200 rounded-lg px-3 py-1 text-sm inline-block mb-2">Phase 4: Applications</div>
              <ul className="text-gray-700 dark:text-gray-300 text-sm space-y-1">
                <li>Domain-specific agent templates</li>
                <li>Real-world use case implementations</li>
                <li>User-friendly interfaces</li>
                <li>Enterprise integration options</li>
              </ul>
            </div>
          </div>
        </section>

        <section>
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-6 text-center">
            <h2 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">Get Involved</h2>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              Join our community to discuss ideas, collaborate on development, and help shape the future of intelligent agent systems!
            </p>
            <div className="flex justify-center space-x-4">
              <a 
                href="https://github.com/ot2net/agi-mcp-agent" 
                target="_blank" 
                rel="noopener noreferrer"
                className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition-colors"
              >
                GitHub Repository
              </a>
              <a 
                href="https://ot2.net" 
                target="_blank" 
                rel="noopener noreferrer"
                className="bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded transition-colors"
              >
                Join OT2.net
              </a>
            </div>
          </div>
        </section>
      </main>

      <footer className="max-w-6xl mx-auto mt-16 pt-8 border-t border-gray-200 dark:border-gray-700">
        <div className="text-center text-gray-500 dark:text-gray-400 text-sm">
          <p>© 2024 OT2.net - AGI-MCP-Agent is licensed under the MIT License</p>
        </div>
      </footer>
    </div>
  );
}
