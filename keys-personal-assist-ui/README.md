# Keys Personal Assist UI

A modern React application for personal assistance, expense management, and AI chat features.

## Technology Stack

- **React 19** - Latest React with hooks and modern features
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **Material UI v6** - Complete UI component library with modern design
- **React Router v7** - Client-side routing with lazy loading
- **Axios** - HTTP client (not directly used, using fetch API)
- **React Hook Form + Zod** - Form management and validation
- **React Markdown** - Markdown rendering with syntax highlighting
- **Sonner** - Toast notifications
- **Date-fns** - Date utilities

## Features

### 1. Home Page

- Modern landing page with hero section
- Gradient design with emerald/cyan color scheme
- Responsive navigation

### 2. Chat Interface

- Real-time AI chat with Bella
- Streaming response support
- Markdown rendering with code syntax highlighting
- Auto-scroll and message history
- Clean, modern chat UI

### 3. Dashboard

- Access to various management tools
- Card-based navigation

### 4. Spending Account Summary

- Complete CRUD operations for spending accounts
- Filtering by account, month, and year
- Pagination with configurable page sizes
- Real-time metrics calculation
- Currency formatting (INR)
- Responsive table design

## Development

### Prerequisites

- Node.js 25+ and npm

### Installation

```bash
npm install --legacy-peer-deps
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
VITE_HOST=localhost
VITE_PORT=3000
```

**Note:** API endpoints are configured through Vite proxy (development) and nginx (production). No environment variables needed for API URLs - the app uses relative paths like `/api/ems` and `/api/bella-chat`.

### Running the Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000` (or your configured VITE_HOST:VITE_PORT)

### Building for Production

```bash
npm run build
```

Build output will be in `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## API Integration

The application uses **relative paths** for API calls that are proxied:

### Development Mode

Vite dev server proxies API requests:

- `/api/bella-chat/*` → `http://localhost:5000/*`
- `/api/ems/*` → `http://localhost:8000/*`

### Production Mode

nginx proxies API requests:

- `/api/bella-chat/*` → `http://bella-chat-service:5000/*`
- `/api/ems/*` → `http://expense-manager-service:8000/*`

### Backend Services

#### 1. Bella Chat Service

- Container: `bella-chat-service:5000`
- Endpoint: `/v1/chat/`
- Provides AI chat functionality with streaming responses

#### 2. EMS (Expense Management System)

- Container: `expense-manager-service:8000`
- Account management endpoints: `/v1/account/*`
- Month/Year management endpoints: `/v1/month_year/*`
- Spending account CRUD operations: `/v1/spending_account/*`

## Docker Deployment

### Multi-Stage Build

The Dockerfile uses a 2-stage build process:

**Stage 1 - Builder (node:25-alpine):**

- Installs dependencies
- Builds production bundle
- Size: ~300 MB (discarded)

**Stage 2 - Production (nginx:1.27-alpine):**

- Serves static files via nginx
- Proxies API requests to backend services
- Final image size: ~22 MB

### Building the Docker Image

```bash
docker build -t keys-personal-assist-ui .
```

### Running with Docker Compose

```bash
# From project root
docker-compose up -d

# Rebuild UI only
docker-compose up -d --build keys-personal-assist-ui
```

The UI will be available at `http://localhost:3000`

### nginx Configuration

Production nginx config includes:

- Gzip compression
- Static asset caching (1 year)
- React Router support (SPA fallback to index.html)
- API proxying to backend services
- Security headers

## Build Optimizations

### Code Splitting

- **Route-based lazy loading** - All pages load on-demand
- **Vendor chunking** - Libraries split into separate chunks:
  - vendor-react: React core
  - vendor-mui: Material-UI components
  - vendor-markdown: Markdown rendering (lazy-loaded)
  - vendor-router: React Router
  - vendor-forms: Form libraries
  - vendor-utils: Utilities

### Performance Metrics

- Initial load (homepage): ~470 KB gzipped
- Chat page (on-demand): +270 KB gzipped (markdown libs)
- Final Docker image: 21.8 MB

## Theme and Styling

The application uses Material UI with a custom theme featuring:

- **Primary**: Emerald green - for trust and growth
- **Secondary**: Cyan - for accents
- **Dark Mode**: Toggle in header, persisted in localStorage
- **Fonts**: Space Grotesk (headings), DM Sans (body)

## Network Architecture

For detailed information about networking, Docker setup, and proxy configuration, see [docs/network-setup.md](docs/network-setup.md)

## License

Private - All rights reserved
