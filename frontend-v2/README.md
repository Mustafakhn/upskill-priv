# Inurek - AI Learning Companion Frontend

A beautiful, modern frontend for Inurek built with Next.js 14, TypeScript, and Tailwind CSS featuring the Mint Zen design theme.

## Features

- 🎨 **Mint Zen Theme** - Clean, minimal design with light/dark mode
- 🤖 **AI-Powered** - Conversational onboarding and personalized learning paths
- 📱 **Fully Responsive** - Works seamlessly on mobile, tablet, and desktop
- ⚡ **Fast & Modern** - Built with Next.js 14 App Router and TypeScript
- 🎯 **User-Friendly** - Intuitive navigation and smooth animations
- 🔒 **Secure** - JWT authentication with token refresh

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 3
- **Icons**: Lucide React
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Forms**: React Hook Form

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running (see `backend/README.md`)

### Installation

1. Clone the repository and navigate to the frontend directory:

```bash
cd frontend-v2
```

2. Install dependencies:

```bash
npm install
```

3. Create environment file:

```bash
# Copy the example file
cp .env.example .env.local
```

4. Update `.env.local` with your API URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

   Or create `.env.local` manually with:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

5. Run the development server:

```bash
npm run dev
```

6. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
frontend-v2/
├── app/
│   ├── components/
│   │   ├── common/          # Reusable components (Button, Card, Badge, etc.)
│   │   ├── home/            # Landing page components
│   │   └── layout/          # Layout components (Header, Footer, ThemeToggle)
│   ├── contexts/            # React contexts (ThemeContext)
│   ├── hooks/               # Custom hooks (useAuth, etc.)
│   ├── services/            # API services
│   ├── about/               # About page
│   ├── journey/[id]/        # Journey detail page
│   ├── login/               # Login page
│   ├── my-learning/         # Learning dashboard
│   ├── register/            # Registration page
│   ├── start/               # Chat onboarding page
│   ├── globals.css          # Global styles
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Landing page
├── public/                  # Static assets
├── .env.local.example       # Environment variables example
├── next.config.js           # Next.js configuration
├── tailwind.config.ts       # Tailwind configuration
└── tsconfig.json            # TypeScript configuration
```

## Design System - Mint Zen Theme

### Light Mode
- Background: Gradient from slate-50 via teal-50 to cyan-50
- Cards: White with subtle shadows
- Primary: Teal-600
- Text: Slate-900

### Dark Mode
- Background: Gradient from slate-900 via gray-900 to slate-950
- Cards: Slate-800 with 50% opacity
- Primary: Teal-500
- Text: Slate-100

### Design Principles
- Minimal and clean - zero clutter
- Smooth transitions between light/dark mode
- Fresh mint accents prevent fatigue
- Focus on content, not decoration
- Generous white space
- Smooth animations (300-500ms)

## Key Pages

### Landing Page (`/`)
- Hero section with search
- How it works
- Featured topics
- Stats

### Start/Chat Page (`/start`)
- Conversational AI onboarding
- Dynamic question flow
- Journey creation

### My Learning (`/my-learning`)
- Dashboard with all journeys
- Progress tracking
- Quick stats

### Journey Detail (`/journey/[id]`)
- Structured learning path with sections
- Resource cards with completion tracking
- Progress visualization
- External resource links

### Auth Pages
- Login (`/login`)
- Register (`/register`)

## Available Scripts

```bash
# Development
npm run dev          # Start development server

# Production
npm run build        # Build for production
npm start            # Start production server

# Linting
npm run lint         # Run ESLint
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

## Features Breakdown

### ✅ Implemented
- Landing page with hero and search
- Theme toggle (light/dark mode)
- Chat-based onboarding
- Journey creation flow
- My Learning dashboard
- Journey detail with sections
- Progress tracking UI
- Responsive design
- Authentication (login/register)
- API integration

### 🚧 Future Enhancements
- AI companion chat within journeys
- Quiz generation and taking
- Resource content viewer
- Social sharing
- Offline mode
- Push notifications

## Responsive Breakpoints

- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Follow the existing code style
2. Use TypeScript for all new files
3. Keep components small and focused
4. Write meaningful commit messages
5. Test on multiple screen sizes

## License

MIT

## Support

For issues or questions, please open an issue on GitHub or contact support@inurek.com
