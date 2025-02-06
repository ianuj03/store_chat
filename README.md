# StoreChat

StoreChat is a full-stack web application with a Django backend and a Next.js frontend. This project leverages Docker for easy deployment and Redis for efficient data management.

## Getting Started

### 1. **Clone the Repository**
```bash
git clone <repository_url>
cd storechat
```

### 2. **Set Up the `.env` File**
Create a `.env` file in the root directory and add the following environment variables:

```env
DJANGO_SECRET_KEY='your_django_secret_key'
DEBUG=True
REDIS_HOST=redis
REDIS_PORT=6379
OPENAI_API_KEY='your_openai_api_key'
```

### 3. **Ensure Execution Permissions for `init.sh`**
Make sure the backend initialization script has execution permissions:

```bash
chmod +x backend/init.sh
```

### 4. **Run the Application**
Start the application using Docker Compose:

```bash
docker-compose up --build
```

This will start:
- The Django backend at `http://localhost:8000`
- The Next.js frontend at `http://localhost:3000`
- Redis at `localhost:6379`

### 5. **Accessing the Admin Panel**
Visit `http://localhost:8000/admin` to access the Django admin panel.
`username: admin`
`password: admin123`

## Docker Overview

- **Backend Container:** Django server handling APIs and business logic.
- **Frontend Container:** Next.js application for the UI.
- **Redis Container:** In-memory data store for caching and real-time features.

## 🗒️ Notes
- Ensure Docker and Docker Compose are installed on your machine.
- The first run might take some time as Docker builds the images.
- Static files are automatically collected using `init.sh`.

---

Happy coding! 🚀
