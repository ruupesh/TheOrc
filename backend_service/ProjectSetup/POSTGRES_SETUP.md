# PostgreSQL Setup

## PostgreSQL Setup Using Docker (With Persistent Storage)

This guide explains how to run **PostgreSQL in Docker** with **persistent storage** so your database data remains even if the container is removed.

---

# 1. Prerequisites

Make sure the following are installed:

* Docker
* Docker Compose (optional but recommended)

Check installation:

```bash
docker --version
docker compose version
```

---

# 2. Pull PostgreSQL Image

Download the official PostgreSQL image from Docker Hub.

```bash
docker pull postgres:latest
```

---

# 3. Create Persistent Storage

Create a Docker volume for storing database data.

```bash
docker volume create postgres_data
```

Check if the volume exists:

```bash
docker volume ls
```

---

# 4. Run PostgreSQL Container

Start a PostgreSQL container with persistent storage.

```bash
docker run -d \
  --name postgres_db \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_DB=my_db \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:latest
```

### Explanation

| Option                                      | Description                    |
| ------------------------------------------- | ------------------------------ |
| `-d`                                        | Run container in detached mode |
| `--name`                                    | Name of the container          |
| `POSTGRES_USER`                             | Database username              |
| `POSTGRES_PASSWORD`                         | Database password              |
| `POSTGRES_DB`                               | Default database created       |
| `-p 5432:5432`                              | Maps container port to host    |
| `-v postgres_data:/var/lib/postgresql/data` | Mount persistent storage       |

PostgreSQL stores its data in:

```
/var/lib/postgresql/data
```

---

# 5. Verify Container Is Running

```bash
docker ps
```

You should see the `postgres_db` container running.

---

# 6. Connect to PostgreSQL

## From Host Machine

```bash
psql -h localhost -U admin -d my_db
```

## From Inside the Container

```bash
docker exec -it postgres_db psql -U admin -d my_db
```

---

# 7. Stop and Restart the Container

Stop the container:

```bash
docker stop postgres_db
```

Start it again:

```bash
docker start postgres_db
```

Because we used a **Docker volume**, the database data will remain intact.

---

# 8. Remove Container Without Losing Data

```bash
docker rm -f postgres_db
```

Since the data is stored in `postgres_data` volume, the database will persist.

To recreate the container:

```bash
docker run -d \
  --name postgres_db \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_DB=my_db \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:latest
```

---

# 9. Optional: Use Local Directory Instead of Volume

Create a directory:

```bash
mkdir postgres_data
```

Run container:

```bash
docker run -d \
  --name postgres_db \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_DB=my_db \
  -p 5432:5432 \
  -v $(pwd)/postgres_data:/var/lib/postgresql/data \
  postgres:latest
```

Now the database files will be stored locally in the `postgres_data` directory.

---

# 10. Recommended Setup Using Docker Compose

Create a file named `docker-compose.yml`.

```yaml
version: "3.9"

services:
  postgres:
    image: postgres:latest
    container_name: postgres_db
    restart: always
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin
      POSTGRES_DB: my_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Start PostgreSQL:

```bash
docker compose up -d
```

Stop it:

```bash
docker compose down
```

---

# 11. Useful Docker Commands

List containers:

```bash
docker ps
```

View logs:

```bash
docker logs postgres_db
```

Open shell inside container:

```bash
docker exec -it postgres_db bash
```

List Docker volumes:

```bash
docker volume ls
```

Inspect volume:

```bash
docker volume inspect postgres_data
```

---

# 12. Match the Backend `.env`

The backend currently expects a connection string in this shape:

```env
DATABASE_URL=postgresql+asyncpg://admin:admin@localhost:5432/my_db
```

If you use different PostgreSQL credentials or a different database name, update the backend `.env` accordingly.

---

# 12. Important Notes

* Always use **volumes or bind mounts** for database containers.
* Without persistent storage, **data will be lost when the container is deleted**.
* Avoid committing credentials in code repositories. Use environment variables or secrets management.

---

# 13. Default PostgreSQL Port

```
5432
```

If this port is already in use, change it:

```bash
-p 5433:5432
```

Then connect using:

```bash
psql -h localhost -p 5433 -U admin -d mydb
```

---

# 14. Cleanup

Remove container:

```bash
docker rm -f postgres_db
```

Remove volume (this deletes database data):

```bash
docker volume rm postgres_data
```

---

# Summary

To run PostgreSQL with Docker and persistent storage:

1. Pull the image
2. Create a Docker volume
3. Run the container with volume mounted at `/var/lib/postgresql/data`

This ensures your **database survives container restarts and recreations**.
