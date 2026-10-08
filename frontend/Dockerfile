# Build stage
FROM node:18-alpine AS build

WORKDIR /app

# Copy package.json and install dependencies
# Note: Uncomment these once you initialize your frontend project with package.json
# COPY package*.json ./
# RUN npm install

# Copy application code
COPY . .

# Build the app
# RUN npm run build

# Serve stage
FROM nginx:alpine

# Copy built assets from build stage (adjust 'dist' folder based on your framework e.g., 'build' for React)
# COPY --from=build /app/dist /usr/share/nginx/html

# For now, simply serve the frontend directory (you can replace this later)
COPY . /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
