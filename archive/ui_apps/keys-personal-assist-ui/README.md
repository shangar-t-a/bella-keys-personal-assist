# Personal Assistant UI

A modern, production-ready chat interface for interacting with multiple AI services (EMS and Bella Chat). Built with Next.js, React, and TypeScript.

## Project Structure

\`\`\`
personalassistui/
├── app/
│   ├── api/
│   │   └── chat/
│   │       └── route.ts              # Chat API endpoint for streaming responses
│   ├── chat/
│   │   └── page.tsx                  # Main chat interface page
│   ├── globals.css                   # Global styles and animations
│   ├── layout.tsx                    # Root layout with providers
│   └── page.tsx                      # Home page
│
├── api/
│   └── clients/                      # Unified API client architecture
│       ├── base-client.ts            # Base class for all API clients
│       ├── ems-client.ts             # EMS (Expense Management System) client
│       ├── bella-chat-client.ts      # Bella Chat AI client
│       └── index.ts                  # Clean exports
│
├── components/
│   ├── chat-message.tsx              # Individual message component with markdown rendering
│   ├── chat-input.tsx                # User input component with terminal line stripping
│   ├── loading-status.tsx            # Status message during API calls (scalable for intermediate steps)
│   ├── markdown-renderer.tsx          # Markdown to React component renderer
│   ├── modern-header.tsx             # App header
│   ├── theme-provider.tsx            # Theme context provider
│   ├── header.tsx                    # Legacy header component
│   ├── Footer.css                    # Footer styles
│   ├── Header.css                    # Header styles
│   ├── Modal.css                     # Modal styles
│   └── ui/                           # shadcn/ui components
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       └── ... (other UI components)
│
├── hooks/
│   ├── use-mobile.ts                 # Mobile detection hook
│   └── use-toast.ts                  # Toast notification hook
│
├── lib/
│   └── utils.ts                      # Utility functions (cn for class merging)
│
├── types/
│   └── api.ts                        # TypeScript types for API responses
│
├── public/
│   └── ... (static assets)
│
├── package.json                      # Dependencies and scripts
├── tsconfig.json                     # TypeScript configuration
├── next.config.mjs                   # Next.js configuration
└── README.md                         # This file
\`\`\`

## Architecture

### API Client Architecture

The application uses a **unified, scalable API client architecture**:

\`\`\`
BaseApiClient (Abstract)
    ├── EMSClient (Expense Management System)
    │   ├── Account Management
    │   ├── Month/Year Management
    │   └── Spending Account Entries
    │
    └── BellaChatClient (AI Chat Service)
        └── Message Streaming
\`\`\`

**Key Features:**
- **Single Responsibility**: Each client handles one service
- **Inheritance**: All clients extend `BaseApiClient` for common HTTP functionality
- **Singleton Pattern**: Instances exported as singletons to prevent multiple instantiations
- **Type Safety**: Full TypeScript support with proper interfaces
- **Scalability**: Easy to add new clients by extending `BaseApiClient`

### Chat Flow

1. **User Input** → Terminal lines stripped automatically
2. **API Request** → Message sent to Bella Chat API
3. **Streaming Response** → Response streamed and rendered in real-time
4. **Markdown Rendering** → Response formatted with markdown support
5. **Status Updates** → Loading status shows intuitive messages (scalable for intermediate steps)

## Key Features

### 1. Markdown Rendering
- Beautiful formatting of API responses
- Support for headers, bold, italic, code blocks, lists, and links
- Automatic syntax highlighting for code blocks

### 2. Terminal Line Stripping
- Automatically removes terminal prompts (`$`, `>`, `#`, `%`)
- Cleans user input before sending to API
- Prevents accidental command syntax in queries

### 3. Loading Status Component
- Intuitive status messages during API calls
- Example: "Bella is thinking..."
- **Scalable for future enhancements**: Can display intermediate steps from API
  - Example future states: "Loading data...", "Generating response...", "Formatting answer..."
  - Simply update the `loadingStatus` state in `app/chat/page.tsx`

### 4. Streaming Response Animation
- **Rolling Gradient Glow**: Cool colors (green → cyan → blue) animate during streaming
- **Automatic Settlement**: Glow disappears after response completes
- **Smooth UX**: Visual feedback that response is being generated

### 5. Responsive Design
- Mobile-first approach
- Optimized for all screen sizes
- Touch-friendly interface

## Environment Variables

\`\`\`env
NEXT_PUBLIC_EMS_API_URL=http://localhost:8000
NEXT_PUBLIC_BELLA_CHAT_API_URL=http://localhost:5000
\`\`\`

## Getting Started

### Installation

\`\`\`bash
# Using shadcn CLI (recommended)
npx shadcn-cli@latest init

# Or clone and install
npm install
\`\`\`

### Development

\`\`\`bash
npm run dev
\`\`\`

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

\`\`\`bash
npm run build
npm start
\`\`\`

## Usage Examples

### Using the EMS Client

\`\`\`typescript
import { emsClient } from "@/api/clients"

// Get all accounts
const accounts = await emsClient.getAllAccounts()

// Create or get account
const account = await emsClient.getOrCreateAccount({ name: "My Account" })

// Update account
await emsClient.updateAccountName(accountId, { name: "Updated Name" })
\`\`\`

### Using the Bella Chat Client

\`\`\`typescript
import { bellaChatClient } from "@/api/clients"

// Send message and get streaming response
const response = await bellaChatClient.sendMessage("Hello, Bella!")
const reader = response.body?.getReader()

// Read streaming chunks
const decoder = new TextDecoder()
while (true) {
  const { done, value } = await reader.read()
  if (done) break
  const chunk = decoder.decode(value)
  console.log(chunk)
}
\`\`\`

### Adding a New API Client

1. Create a new file in `api/clients/` (e.g., `my-service-client.ts`)
2. Extend `BaseApiClient`:

\`\`\`typescript
import { BaseApiClient } from "./base-client"

class MyServiceClient extends BaseApiClient {
  constructor() {
    super({ baseURL: process.env.NEXT_PUBLIC_MY_SERVICE_URL })
  }

  async myMethod(): Promise<any> {
    const response = await this.getClient().get("/endpoint")
    return response.data
  }
}

export const myServiceClient = new MyServiceClient()
\`\`\`

3. Export from `api/clients/index.ts`:

\`\`\`typescript
export { myServiceClient } from "./my-service-client"
\`\`\`

## Customization

### Updating Loading Status Messages

Edit `app/chat/page.tsx` to customize status messages:

\`\`\`typescript
// For simple messages
setLoadingStatus("Bella is thinking...")

// For intermediate steps (future API enhancement)
setLoadingStatus("Loading data from database...")
setLoadingStatus("Generating response...")
setLoadingStatus("Formatting answer...")
\`\`\`

### Modifying Gradient Glow Animation

Edit `app/globals.css` to adjust the `gradient-glow` animation:

\`\`\`css
@keyframes gradient-glow {
  0% {
    box-shadow: 0 0 20px rgba(34, 197, 94, 0.3); /* Green */
  }
  /* ... adjust colors and timing ... */
}
\`\`\`

### Changing Color Scheme

Update CSS variables in `app/globals.css`:

\`\`\`css
:root {
  --primary: oklch(0.205 0 0); /* Change primary color */
  --accent: oklch(0.97 0 0);   /* Change accent color */
}
\`\`\`

## Technologies

- **Next.js 15** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS v4** - Utility-first styling
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **shadcn/ui** - Component library

## Performance Optimizations

- Server-side rendering for initial page load
- Streaming responses for real-time feedback
- Optimized re-renders with React hooks
- CSS animations for smooth UX
- Lazy loading of components

## Future Enhancements

- [ ] Intermediate step indicators in loading status
- [ ] Message history persistence
- [ ] User authentication
- [ ] Multiple conversation threads
- [ ] Message search and filtering
- [ ] Custom themes
- [ ] Voice input/output
- [ ] Message reactions and feedback

## License

MIT

## Support

For issues or questions, please open an issue in the repository.
\`\`\`

```typescriptreact file="api/client.ts" isDeleted="true"
...deleted...
