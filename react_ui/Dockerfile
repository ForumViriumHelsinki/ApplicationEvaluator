# Dependencies stage - use Bun for fast dependency installation
FROM oven/bun:1.3.10-alpine AS deps

WORKDIR /app

# Copy package files
COPY package.json bun.lock* ./

# Install dependencies
RUN bun install --frozen-lockfile

# ============================================================================
# DEV STAGE - Development with Vite HMR
# ============================================================================
FROM deps AS dev

WORKDIR /app

# Copy source code
COPY . .

EXPOSE 5173

CMD ["bun", "run", "dev", "--host", "0.0.0.0"]

# ============================================================================
# BUILD STAGE - Build for production
# ============================================================================
# Use Node.js for reliable Vite builds
# (Bun's baseline binary can crash without AVX CPU support in some environments)
FROM node:22-alpine AS build

WORKDIR /app

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy source code
COPY . .

# Build the application using npm (which runs vite via package.json scripts)
RUN npm run build

# ============================================================================
# RUNTIME STAGE - Production with nginx (default)
# ============================================================================
FROM nginx:1.27-alpine AS runtime

# Install envsubst (part of gettext)
RUN apk add --no-cache gettext

# Copy custom nginx configs for non-root operation
COPY nginx-main.conf /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy config template for runtime environment variable substitution
COPY public/config.js.template /usr/share/nginx/html/config.js.template

# Copy entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Prepare for non-root operation (nginx user is uid 101 in alpine)
# Note: config.js must be writable by nginx user for envsubst
RUN chown -R nginx:nginx /var/cache/nginx /usr/share/nginx/html

EXPOSE 80

USER nginx

# Environment variables with defaults (can be overridden at runtime)
ENV SERVER_ROOT="" \
    MAX_SCORE=5 \
    FINAL_SCORE_MULTIPLIER=4 \
    SHOW_SCORES_FROM_OTHER_USERS=true \
    ALLOW_SUBMIT=false

ENTRYPOINT ["/docker-entrypoint.sh"]
