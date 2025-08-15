# Bella (Keys' Personal Assist)

A modern personal assistant application with expense tracking capabilities, built with Next.js and FastAPI. Bella helps you manage your day, track expenses, and will soon include AI-powered chatbot functionality.

## Features

- 🏠 **Personal Dashboard**: Clean interface for managing daily tasks
- 📊 **Expense Tracking**: Comprehensive spending account summary with filtering
- 🎨 **Modern UI**: Clean, responsive design with dark/light mode support
- 📱 **Mobile Friendly**: Fully responsive across all devices
- 🤖 **AI Ready**: Architecture prepared for future chatbot integration

## Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python)
- **Icons**: Lucide React
- **Fonts**: Space Grotesk, Inter

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.13+ (for FastAPI backend)
- npm or yarn package manager

### Installation & Setup

1. **Clone the repository**

   ```bash
   git clone \`<your-repo-url>\`
   cd keys-personal-assist-ui
   ```

2. **Install frontend dependencies**

   ```bash
   npm install
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local` with your configuration:

   ```env
   PORT=3000
   HOSTNAME=localhost
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

4. **Start your FastAPI backend server**

   Make sure your FastAPI backend is running on `http://localhost:8000` (or update the `NEXT_PUBLIC_API_BASE_URL` to match your backend URL).

5. **Run the frontend development server**

   ```bash
   npm run dev
   ```

6. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
npm run build
npm start
```

## Troubleshooting

### "Failed to fetch" Error

If you see "Failed to fetch" errors:

1. **Check if your FastAPI backend is running**
   - Ensure your FastAPI server is started and accessible
   - Default expected URL: `http://localhost:8000`

2. **Verify environment variables**
   - Check that `NEXT_PUBLIC_API_BASE_URL` in `.env.local` matches your backend URL
   - Remember: Next.js requires `NEXT_PUBLIC_` prefix for client-side environment variables

3. **CORS Configuration**
   - Ensure your FastAPI backend allows CORS from `http://localhost:3000`
   - Add CORS middleware in your FastAPI app if needed

4. **Network Issues**
   - Check if both frontend and backend are on the same network
   - Verify firewall settings aren't blocking the connection

### Common Setup Issues

- **Port conflicts**: Change `PORT` in `.env.local` if 3000 is already in use
- **Node version**: Ensure you're using Node.js 18 or higher
- **Dependencies**: Run `npm install` again if you encounter module errors

## Project Structure

```txt
├── app/                    # Next.js App Router pages
│   ├── dashboard/         # Dashboard pages
│   │   └── spending-account-summary/  # Expense tracking page
│   ├── layout.tsx         # Root layout
│   ├── page.tsx          # Homepage (Bella's main page)
│   └── globals.css       # Global styles
├── components/            # Reusable components
│   ├── ui/               # UI library components
│   └── modern-header.tsx # Navigation header
└── .env.example          # Environment variables template
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## API Integration

The app connects to a FastAPI backend. The spending account summary page expects these API endpoints to be available on your backend server.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.
