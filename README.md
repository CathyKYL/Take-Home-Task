# Bill.com Processing

A minimal Next.js frontend for processing Bill.com vendor payments and reconciling to payment holds.

## Getting Started

### Installation

```bash
npm install
```

### Environment Setup

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Replace with your backend API URL as needed.

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

### Build

```bash
npm run build
```

### Deployment

This project is configured for Netlify deployment with static export.

```bash
npm run build
```

The `out/` directory will contain the static export ready for deployment.
