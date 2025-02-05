# Use Node.js official image
FROM node:18-alpine

# Set working directory inside the container
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./
RUN npm install

# Copy all project files
COPY . .

# Expose port 3000 for Next.js
EXPOSE 3000

# Build the application
RUN npm run build

# Start Next.js in production mode
CMD ["npm", "start"]

