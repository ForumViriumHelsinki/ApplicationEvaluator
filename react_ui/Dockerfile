# Dependencies stage - use Bun for fast dependency installation
FROM oven/bun:1.3.4-alpine AS deps

WORKDIR /app

# Copy package files
COPY package.json bun.lock* ./

# Install dependencies
RUN bun install --frozen-lockfile

# Build stage - use Node.js for reliable Vite builds
# (Bun's baseline binary can crash without AVX CPU support in some environments)
FROM node:22-alpine AS build

WORKDIR /app

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy source code
COPY . .

# Build the application using npm (which runs vite via package.json scripts)
RUN npm run build

# Production stage
FROM nginx:1.27-alpine

# Copy custom nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from build stage
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
