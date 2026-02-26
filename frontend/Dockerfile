###############################################
# Stage 1: Build the React app
###############################################
FROM node:20-alpine AS builder

WORKDIR /app

# Accept build-time environment variable for backend URL
ARG REACT_APP_BACKEND_URL=http://localhost:8000
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL

# Install dependencies first (layer caching)
COPY package*.json ./
RUN npm ci --silent

# Copy source code
COPY . .

# Build for production
RUN npm run build

###############################################
# Stage 2: Serve with Nginx
###############################################
FROM nginx:1.27-alpine AS production

# Security: remove default nginx config
RUN rm -rf /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built React app from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Security: make nginx run as non-root where possible
# (Alpine nginx image already runs worker as 'nginx' user)
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
