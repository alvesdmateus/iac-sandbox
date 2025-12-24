# Infrastructure Visualization API - Backend

FastAPI backend for real-time infrastructure visualization and management.

## Features

- **Stack Management**: Create, list, deploy, destroy Pulumi stacks
- **File Operations**: Read, write, validate infrastructure code files
- **Real-time Updates**: WebSocket support for deployment streaming
- **Pulumi Integration**: Complete Pulumi Automation API wrapper

## Setup

### Prerequisites

- Python 3.11+
- Pulumi CLI installed
- GCP credentials configured

### Installation

1. **Create virtual environment**:
   ```bash
   cd app/backend
   python -m venv venv
   ```

2. **Activate virtual environment**:
   ```bash
   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Configuration

Required environment variables in `.env`:

```env
# Pulumi
PULUMI_ACCESS_TOKEN=your_token_here

# GCP
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1

# Optional
DEBUG=true
LOG_LEVEL=INFO
```

## Running the Server

### Development Mode

```bash
cd app/backend
source venv/Scripts/activate  # or venv\Scripts\activate on Windows
uvicorn src.main:socket_app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn src.main:socket_app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- HTTP API: `http://localhost:8000`
- WebSocket: `ws://localhost:8000/ws/socket.io`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

## API Endpoints

### Stack Management

- `GET /api/v1/stacks` - List all stacks
- `GET /api/v1/stacks/{name}` - Get stack details
- `POST /api/v1/stacks` - Create new stack
- `DELETE /api/v1/stacks/{name}` - Delete stack
- `PUT /api/v1/stacks/{name}/config` - Update configuration
- `GET /api/v1/stacks/{name}/outputs` - Get stack outputs
- `GET /api/v1/stacks/{name}/resources` - List resources
- `POST /api/v1/stacks/{name}/preview` - Preview changes
- `POST /api/v1/stacks/{name}/up` - Deploy stack
- `POST /api/v1/stacks/{name}/destroy` - Destroy resources
- `POST /api/v1/stacks/{name}/refresh` - Refresh state

### File Management

- `GET /api/v1/files/infra` - List files
- `GET /api/v1/files/infra/tree` - Get directory tree
- `GET /api/v1/files/infra/{path}` - Read file
- `PUT /api/v1/files/infra/{path}` - Update file
- `POST /api/v1/files/infra` - Create file
- `DELETE /api/v1/files/infra/{path}` - Delete file
- `POST /api/v1/files/infra/validate` - Validate Python code

### WebSocket Events

Connect to `/ws/socket.io` and emit:

- `subscribe_stack` - Subscribe to stack updates
- `subscribe_deployment` - Subscribe to deployment updates

Receive events:
- `connection:confirmed` - Connection established
- `subscription:confirmed` - Subscription confirmed
- `deployment:started` - Deployment began
- `deployment:progress` - Progress update
- `deployment:log` - Log message
- `deployment:resource_change` - Resource changed
- `deployment:completed` - Deployment finished
- `deployment:failed` - Deployment failed

## Project Structure

```
app/backend/
├── src/
│   ├── api/               # API endpoints
│   │   ├── stacks.py      # Stack operations
│   │   └── files.py       # File operations
│   ├── services/          # Business logic
│   │   ├── pulumi_service.py   # Pulumi Automation API wrapper
│   │   └── file_service.py     # File management
│   ├── models/            # Pydantic models
│   │   ├── stack.py       # Stack models
│   │   └── file.py        # File models
│   ├── websocket/         # WebSocket handlers
│   ├── config.py          # Configuration
│   └── main.py            # FastAPI app
├── tests/                 # Tests
├── requirements.txt       # Dependencies
├── .env.example          # Example environment
└── README.md             # This file
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src tests/
```

## Development

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/
```

### Adding New Endpoints

1. Create route in `src/api/`
2. Add service logic in `src/services/`
3. Define models in `src/models/`
4. Include router in `src/main.py`

## Troubleshooting

### Pulumi Access Token Error

Make sure `PULUMI_ACCESS_TOKEN` is set in `.env`:
```bash
pulumi login
# Copy token from output
```

### GCP Credentials Error

Set `GOOGLE_CREDENTIALS` to path of service account key:
```bash
export GOOGLE_CREDENTIALS=/path/to/gcp-key.json
```

### Import Errors

Make sure you're in the virtual environment:
```bash
source venv/Scripts/activate
pip install -r requirements.txt
```

## Next Steps

- [ ] Add deployment streaming with WebSocket
- [ ] Implement Kubernetes manifest service
- [ ] Add authentication/authorization
- [ ] Add deployment history tracking
- [ ] Implement resource topology endpoints

## License

See main repository LICENSE file.
