# Nature App Frontend

A Next.js web application for nature assessment and analysis, developed in collaboration with Høje-Taastrup Municipality and DTU.

## Features

- **Interactive Map Interface**: OpenLayers-based mapping with polygon drawing capabilities
- **Authentication System**: NextAuth.js integration with custom credentials provider
- **Analysis Tools**: Submit and view nature analysis results
- **Real-time Data**: Integration with backend API for analysis processing
- **Responsive Design**: Built with Tailwind CSS and Material-UI components

## Prerequisites

Before running the application locally, ensure you have the following installed:

- **Node.js**: Version 20 or higher
- **npm**, **yarn**, **pnpm**, or **bun**: Package manager of your choice

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd nature-app
```

### 2. Install Dependencies

Using npm:
```bash
npm install
```

Using yarn:
```bash
yarn install
```

Using pnpm:
```bash
pnpm install
```

Using bun:
```bash
bun install
```

### 3. Environment Configuration

Create a `.env.local` file in the root directory and configure the following environment variables:

```env
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
AUTH_SECRET=INSERT-FROM-CREDENTIALS-FILE-IN-PROJECT-SUBMISSION

# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://130.226.56.134/api/v1

# Optional: WMS Configuration (if using custom map tiles)
NEXT_PUBLIC_WMS_BASE_URL=https://services.datafordeler.dk/DKskaermkort/topo_skaermkort_daempet/1.0.0/Wmts
NEXT_PUBLIC_WMS_USERNAME=STGGAEECCJ
NEXT_PUBLIC_WMS_PASSWORD=een!oM8HJ7_!aCw6
```

### 4. Start the Development Server

```bash
npm run dev
```

Or with your preferred package manager:
```bash
# yarn
yarn dev

# pnpm
pnpm dev

# bun
bun dev
```

The application will start on [http://localhost:3000](http://localhost:3000).
