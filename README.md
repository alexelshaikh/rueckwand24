# FastAPI Auth & Catalog Service

This project is a small backend service built with **FastAPI** and **MySQL**.

It demonstrates:

- JWT-based authentication (login/logout, token sessions)
- User management (CRUD)
- Simple product catalog (materials, product types, items)
- Image processing: cropping a base image and generating a **PDF per item**
- Dockerized setup (MySQL + app)
- Basic tests with `pytest`

---

## Project Structure

```text
├─ api_routes/                 # all endpoints are located here
│  ├─ auth.py                  # login/logout endpoints
│  ├─ material.py              # catalog materials endpoints
│  ├─ product_types.py         # catalog product types endpoints
│  ├─ items.py                 # catalog items endpoints
│  └─ users.py                 # user CRUD endpoints
├─ core/
│  ├─ auth_core.py             # hashing, JWT creation/verification, current_user dependency
│  ├─ database_core.py         # engine, async session using get_db()
│  ├─ image_core.py            # contains the method generate_item_pdf() to generate cropped images of items
│  └─ crud/
│     ├─ crud_users.py         # user CRUD operations
│     ├─ crud_tokens.py        # tokens CRUD operations
│     └─ crud_items.py         # material/product/item CRUD operations
├─ models/
│  ├─ api_models/              # App models (classes) 
│  │  ├─ db_user_models.py     # Models for User
│  │  ├─ db_auth_models.py     # Models for Token/Session
│  │  └─ db_catalog_models.py  # Models for Material, ProductType, ItemConfiguration
│  ├─ db_models/               # Database models (tables) 
│  │  ├─ db_base.py            # The base model
│  │  ├─ db_user_models.py     # Models for User
│  │  ├─ db_auth_models.py     # Models for Token/Session
│  │  └─ db_catalog_models.py  # Models for Material, ProductType, ItemConfiguration
├─ resources/
│  ├─ images/
│  │  └─ calm_kitchen.jpg      # Static image for cropping - this image is from: https://rueckwand24.com/collections/kuechenrueckwand
│  └─ cropped_images/          # Generated cropped images as PDFs (item_<id>.pdf)
├─ tests/
│  ├─ conftest.py              # Adds project root to sys.path
│  ├─ test_auth_core.py        # Tests for hashing & JWT
│  └─ test_image_core.py       # tests for PDF generation
├─ main.py                     # FastAPI app + lifespan (DB create_all)
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
├─ .env                        # Contains environment variables, e.g., MySQL user, password, etc.
└─ README.md
```


## Configuration

All configuration is driven by environment variables, loaded from a `.env` file.

Modify `.env` in the project root:

```env
MYSQL_ROOT_PASSWORD=root_password
MYSQL_DATABASE=db_alex
MYSQL_USER=user_alex
MYSQL_PASSWORD=user_alex_password
SECRET_KEY=rueckwand24_rocks
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

On startup, the app creates tables for all imported SQLAlchemy models:
  - `users`
  - `token_sessions`
  - `materials`
  - `product_types`
  - `item_configurations`


---
## Running with Docker

### Build & start

From the project root:

```bash
  docker-compose up --build
```

This will:

- Start **MySQL**
- Initialise `db_alex` and `user_alex` on first run
- Build the FastAPI app image
- Start the app container (`fastapi_app`) on port **8000**

### Access the API docs

On your host machine:

- Swagger UI: **http://localhost:8000/docs**  
- ReDoc: **http://localhost:8000/redoc**  
- OpenAPI JSON: **http://localhost:8000/openapi.json**


---

## Running Locally (without Docker)

If you prefer to run the app directly on your machine:

### Install dependencies

```bash
  pip install --upgrade pip
  pip install -r requirements.txt
```

### Set up a local MySQL

Make sure you have a MySQL server running locally and either:

- Set a `DATABASE_URL` environment variable, or  
- Set the default in `core/database_core.py`.

Example `DATABASE_URL`:

```bash
  export DATABASE_URL="mysql+aiomysql://user_alex:my_secure_password@localhost:3306/db_alex"
```

### Start the app

```bash
  uvicorn main:app --reload
```

Then navigate to:

- http://127.0.0.1:8000/docs


---


# Using the API – Example

All examples below assume you’re using **Swagger UI** at `/docs`.

### Create a user

1. Expand **`POST /users`**
2. Click **Try it out**
3. Example request body:

```json
{
  "email": "alex@el-shaikh.com",
  "password": "myHardPassword2.0",
  "is_active": true
}
```
Note that the email provided must be a valid email (syntax-wise).

4. Execute → expect `200 OK` with `UserRead`:

```json
{
  "email": "alex@el-shaikh.com",
  "is_active": true,
  "id": 0,
  "created_at": "2025-11-28T14:36:12.794Z"
}
```

### Log in and get a JWT

1. Expand **`POST /login`**
2. Click **Try it out**
3. Use form fields (not JSON):
   - `username`: `alex@el-shaikh.com`
   - `password`: `myHardPassword2.0`
   - Ignore the other fields
4. Execute → response:

```json
{
  "access_token": "<JWT_TOKEN_HERE>",
  "token_type": "bearer"
}
```

### Authorize in Swagger

1. Click the **Authorize** button at the top right in `/docs`.
2. Enter your username (=email) and password.
3. Click **Authorize**, then **Close**.

Now every protected endpoint automatically sends:

```
Authorization: Bearer <JWT_TOKEN_HERE>
```

### Test protected user endpoints

- **`GET /users`** – list users (requires auth)  
- **`GET /users/{user_id}`** – get a single user by its id
- **`DELETE /users/{user_id}`** – delete a user by its id

All of these will fail with `Not authenticated` if you have not authorized with a valid token.

---

## Catalog & Image Processing

The catalog consists of:

- `Material` (e.g. “Wood”)
- `ProductType` (e.g. “Backwall”)
- `ItemConfiguration` (an item combining material + product type + dimensions)

When you create an **ItemConfiguration**, the app:

1. Loads the base image: `resources/images/calm_kitchen.jpg`
2. Crops it to `width x height` (top-left origin)
3. Draws a timestamp overlay (with a white background rectangle)
4. Saves the result as a **PDF** in `resources/cropped_images/item_<id>.pdf`
5. Stores the cropped image's path in `pdf_path` in the DB in `item_configurations`

### Create a material

Use **`POST /materials`** with:

```json
{
  "name": "Wood",
  "description": "Warm wood!"
}
```
The returned response should contain the id `1`.

### Create a product type

Use **`POST /product-types`** with:

```json
{
  "name": "Backwall",
  "description": "Kitchen backwall"
}
```
The returned response should contain the id `1`.

### Create an item (triggers cropped image PDF generation)

**`POST /items`**

```json
{
  "material_id": 1,
  "product_type_id": 1,
  "width": 700,
  "height": 700
}
```

Example response:

```json
{
  "material_id": 1,
  "product_type_id": 1,
  "width": 700,
  "height": 700,
  "id": 1,
  "pdf_path": "resources/cropped_images/item_1.pdf",
  "created_at": "2025-11-28T13:17:32"
}
```

When running in Docker, the file lives at:

```bash
  /app/resources/cropped_images/item_1.pdf
```

You can inspect files inside the app container with:

```bash
  docker exec -it fastapi_app sh
  ls /app/resources/cropped_images
```


---

## Running Tests

### Locally (host machine)
Navigate to the root directory of the project, then run:
```bash
  pytest
```

You should see something like:

```text
================================================= test session starts =================================================
platform win32 -- Python 3.13.2, pytest-9.0.1, pluggy-1.6.0
rootdir: C:\Users\Alex\PycharmProjects\FastAPI
plugins: anyio-4.9.0
collected 5 items

tests\test_auth_core.py ..                                                                                       [ 40%]
tests\test_image_core.py ...                                                                                     [100%]

================================================== 5 passed in 1.26s ==================================================
```

### Inside Docker

Run tests inside the `app` service:

```bash
  docker-compose run --rm app pytest
```
