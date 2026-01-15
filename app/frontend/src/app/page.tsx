import Link from 'next/link';

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="max-w-5xl w-full">
        <h1 className="text-6xl font-bold text-center mb-8 bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
          Infrastructure Visualization
        </h1>

        <p className="text-xl text-center text-gray-600 mb-12">
          Real-time infrastructure visualization and deployment tracking
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Link
            href="/stacks"
            className="group rounded-lg border border-gray-200 px-8 py-6 hover:border-blue-500 hover:bg-blue-50 transition-all"
          >
            <h2 className="text-2xl font-semibold mb-2">
              Stacks{' '}
              <span className="inline-block transition-transform group-hover:translate-x-1">
                →
              </span>
            </h2>
            <p className="text-gray-600">
              View and manage your Pulumi stacks
            </p>
          </Link>

          <Link
            href="/stacks"
            className="group rounded-lg border border-gray-200 px-8 py-6 hover:border-green-500 hover:bg-green-50 transition-all"
          >
            <h2 className="text-2xl font-semibold mb-2">
              Deploy{' '}
              <span className="inline-block transition-transform group-hover:translate-x-1">
                →
              </span>
            </h2>
            <p className="text-gray-600">
              Deploy and track infrastructure changes
            </p>
          </Link>

          <Link
            href="/stacks"
            className="group rounded-lg border border-gray-200 px-8 py-6 hover:border-purple-500 hover:bg-purple-50 transition-all"
          >
            <h2 className="text-2xl font-semibold mb-2">
              Code{' '}
              <span className="inline-block transition-transform group-hover:translate-x-1">
                →
              </span>
            </h2>
            <p className="text-gray-600">
              Edit infrastructure code in real-time
            </p>
          </Link>

          <Link
            href="/stacks"
            className="group rounded-lg border border-gray-200 px-8 py-6 hover:border-orange-500 hover:bg-orange-50 transition-all"
          >
            <h2 className="text-2xl font-semibold mb-2">
              Topology{' '}
              <span className="inline-block transition-transform group-hover:translate-x-1">
                →
              </span>
            </h2>
            <p className="text-gray-600">
              Visualize resource relationships
            </p>
          </Link>
        </div>

        <div className="mt-12 text-center">
          <p className="text-sm text-gray-500">
            Powered by Pulumi, Next.js, and FastAPI
          </p>
        </div>
      </div>
    </div>
  );
}
