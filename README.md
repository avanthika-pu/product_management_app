# Product Management API

A robust Django REST Framework (DRF) application for managing products with automated asynchronous thumbnail generation using Celery and Redis, all containerized with Docker.

---

## 1. Project Overview & Architecture Decisions

### Framework Choice
* **Django & DRF**: Chosen for the rapid development of secure, scalable RESTful APIs and its powerful ORM.
* **Design Patterns**: 
    * **Observer Pattern**: Leveraged via Django signals/lifecycle hooks to trigger background tasks upon model save.
    * **Asynchronous Task Queue**: Uses Celery to offload heavy image processing (thumbnails) from the main request-response cycle, ensuring a snappy user experience.

### Architecture Decisions
* **Process Supervision**: Managed via Docker Compose and internal container entrypoints to ensure the Web server and Celery worker remain active.
* **Slug-based Routing**: Products are identified by unique slugs rather than IDs to improve URL readability and SEO.



---

## 2. Setup Instructions

To build and run the entire stack, ensure you have **Docker** and **Docker Compose** installed.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/avanthika-pu/product_management_app.git
    cd product-management-api
    ```
2.  **Build and Start**:
    ```bash
    docker compose up --build
    ```
3.  **Run Migrations**:
    ```bash
    docker compose exec app python manage.py migrate
    ```

---

## 3. Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DEBUG` | Enables/Disables Django debug mode | `True` |
| `CELERY_BROKER_URL` | Connection string for Redis broker | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Connection string for task results | `redis://redis:6379/0` |

---

## 4. API Endpoint Reference

* **Health Check**: [http://localhost:8000/health/](http://localhost:8000/health/)

### Main Endpoints:
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/products/` | List products (supports `?search=` and filtering) |
| `POST` | `/api/products/` | Create product (Auto-generates unique slug) |
| `GET` | `/api/products/{slug}/` | Retrieve product details |
| `PUT` | `/api/products/{slug}/` | Update product details |
| `DELETE` | `/api/products/{slug}/` | Remove a product |

---

## 5. Database Optimization

* **Indexing**: The `slug` field is indexed (`unique=True`) to ensure $O(1)$ lookup speeds.
* **Query Strategies**: Implemented `DjangoFilterBackend` and `SearchFilter` to offload filtering logic to the database level.
* **Relationship Management**: Foreign keys are optimized for category-based filtering.

---

## 6. Celery Task Flow & Supervision

1.  **Flow**: Upon a successful `POST` request with an image, a task is sent to **Redis**. 
2.  **Worker**: The **Celery Worker** detects the task, processes the image into a 300x300 thumbnail using **Pillow**, and updates the database record.
3.  **Supervision**: The services are supervised by the Docker Engine with health checks implemented at the application level to monitor the connection status of the Database, Redis, and the Worker.



---

## 7. Known Limitations & Trade-offs

* **Local Storage**: Currently uses local Docker volumes for media storage. A production environment should use S3 or similar cloud storage.
* **Sequential Slug Generation**: The unique slug loop is reliable but performs incremental database checks which could be optimized for high-concurrency environments.
