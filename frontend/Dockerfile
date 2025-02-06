FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

# Copy the rest of the application
COPY . .

# Expose port 3000 for the frontend
EXPOSE 3000

# Start the app in development mode
CMD ["npm", "run", "dev"]

