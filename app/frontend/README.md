# Infrastructure Visualization - Frontend

Next.js 14 frontend for real-time infrastructure visualization and management.

## Features

- **Real-time Updates**: WebSocket integration for live deployment tracking
- **Code Editor**: Monaco Editor for editing infrastructure code
- **Stack Management**: View, create, deploy, and destroy Pulumi stacks
- **File Browser**: Navigate and edit infrastructure files
- **Resource Topology**: Visualize infrastructure relationships
- **Deployment Tracking**: Real-time logs and progress indicators

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Monaco Editor** - Code editing
- **Socket.IO Client** - Real-time updates
- **Axios** - HTTP client
- **SWR** - Data fetching and caching
- **React Flow** - Topology visualization
- **xterm.js** - Terminal emulator

## Setup

### Prerequisites

- Node.js 18+
- Backend API running (see `../backend/README.md`)

### Installation

1. **Install dependencies**:
   ```bash
   cd app/frontend
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your configuration
   ```

### Configuration

Create `.env.local` with:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Running the Application

### Development Mode

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
npm run build
npm start
```

### Type Checking

```bash
npm run type-check
```

### Linting

```bash
npm run lint
```

## Project Structure

```
app/frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Homepage
│   │   └── stacks/             # Stack pages (to be created)
│   ├── components/             # React components
│   │   ├── common/             # Shared components
│   │   ├── editor/             # Code editor components
│   │   ├── stack/              # Stack management components
│   │   ├── deployment/         # Deployment tracking
│   │   └── topology/           # Resource visualization
│   ├── hooks/                  # Custom React hooks
│   │   ├── useWebSocket.ts     # WebSocket connection (to be created)
│   │   ├── useStack.ts         # Stack data management
│   │   └── useDeployment.ts    # Deployment tracking
│   ├── lib/                    # Utilities and clients
│   │   └── api-client.ts       # ✅ HTTP API client
│   ├── types/                  # TypeScript types
│   │   ├── stack.ts            # ✅ Stack types
│   │   ├── file.ts             # ✅ File types
│   │   └── websocket.ts        # ✅ WebSocket types
│   └── styles/
│       └── globals.css         # ✅ Global styles
├── public/                     # Static assets
├── package.json                # ✅ Dependencies
├── tsconfig.json               # ✅ TypeScript config
├── next.config.js              # ✅ Next.js config
├── tailwind.config.js          # ✅ Tailwind config
└── README.md                   # This file
```

## Available Components (To Be Built)

### Pages
- [ ] `/stacks` - Stack list page
- [ ] `/stacks/[stackName]` - Stack detail page
- [ ] `/stacks/[stackName]/code` - Code editor
- [ ] `/stacks/[stackName]/topology` - Resource graph
- [ ] `/stacks/[stackName]/deployments` - Deployment history

### Components
- [ ] `components/common/Navbar.tsx` - Navigation bar
- [ ] `components/stack/StackList.tsx` - Stack grid/list
- [ ] `components/stack/StackCard.tsx` - Stack summary card
- [ ] `components/stack/StackControls.tsx` - Deploy/destroy buttons
- [ ] `components/editor/CodeEditor.tsx` - Monaco editor wrapper
- [ ] `components/editor/YamlViewer.tsx` - YAML viewer
- [ ] `components/deployment/LogStreamer.tsx` - Real-time logs
- [ ] `components/deployment/ProgressBar.tsx` - Progress indicator
- [ ] `components/topology/TopologyGraph.tsx` - Resource graph

### Hooks
- [ ] `hooks/useWebSocket.ts` - WebSocket connection
- [ ] `hooks/useStack.ts` - Stack CRUD operations
- [ ] `hooks/useDeployment.ts` - Deployment tracking
- [ ] `hooks/useResource.ts` - Resource data

## API Client Usage

```typescript
import { apiClient } from '@/lib/api-client';

// List stacks
const stacks = await apiClient.listStacks();

// Get stack details
const stack = await apiClient.getStack('dev-test');

// Deploy stack
const result = await apiClient.deployStack('dev-test');

// Read file
const file = await apiClient.readFile('__main__.py');

// Update file
await apiClient.updateFile('__main__.py', {
  content: updatedContent,
  validate: true,
});
```

## WebSocket Events

Connect to backend WebSocket for real-time updates:

```typescript
import { io } from 'socket.io-client';

const socket = io(process.env.NEXT_PUBLIC_WS_URL!);

// Subscribe to stack updates
socket.emit('subscribe_stack', { stackName: 'dev-test' });

// Listen for deployment logs
socket.on('deployment:log', (event) => {
  console.log(event.data.message);
});
```

## Development Roadmap

### Phase 1: Core UI ✅
- [x] Next.js setup with TypeScript
- [x] Tailwind CSS configuration
- [x] API client implementation
- [x] TypeScript types
- [x] Basic layout and homepage

### Phase 2: Stack Management (In Progress)
- [ ] useWebSocket hook
- [ ] Stack list page
- [ ] Stack detail page
- [ ] Stack controls (deploy, destroy)

### Phase 3: Code Editor
- [ ] Monaco Editor integration
- [ ] File tree navigation
- [ ] Syntax highlighting
- [ ] Save/validate functionality

### Phase 4: Real-time Features
- [ ] Deployment log streaming
- [ ] Progress indicators
- [ ] Resource status updates

### Phase 5: Visualization
- [ ] Resource topology graph
- [ ] YAML viewer
- [ ] Resource inspector

## Troubleshooting

### Cannot connect to API

Make sure the backend is running:
```bash
cd ../backend
uvicorn src.main:socket_app --reload
```

### WebSocket connection errors

Check that `NEXT_PUBLIC_WS_URL` in `.env.local` matches your backend WebSocket URL.

### Type errors

Run type check to see all errors:
```bash
npm run type-check
```

## Next Steps

1. Implement `useWebSocket` hook for real-time updates
2. Create stack list page at `/stacks`
3. Build stack detail page with controls
4. Integrate Monaco Editor for code editing
5. Add deployment log streaming

## Contributing

See main repository contributing guidelines.

## License

See main repository LICENSE file.
