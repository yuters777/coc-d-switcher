#!/bin/bash
# Start the frontend development server on all network interfaces

cd "$(dirname "$0")/frontend"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the dev server (Vite will use config from vite.config.ts with host: 0.0.0.0)
echo "Starting frontend dev server on 0.0.0.0:5173..."
npm run dev
