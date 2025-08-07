# Todo Project
This is a Django REST API project for managing tasks (ToDo list) with user registration, authentication, and PostgreSQL database.

---
## Technologies Used

- Python 3.x  
- Django 4.x  
- Django REST Framework  
- PostgreSQL  
- Docker & Docker Compose  
- JWT Authentication (Simple JWT)  
- django-filter for filtering  
- drf-spectacular for API schema  

---
## Local Setup
This section explains how to set up the project locally for development.

### 1. Clone the repository and navigate to the backend folder
git clone https://github.com/yourusername/todo_project.git  
cd todo_project/backend

> **Note:**  
> The project has a nested folder structure. The backend folder contains the Django project files, including `manage.py`.  
> You must run Django commands from inside this folder.

### 2. Create and activate a Python virtual environment
Create a virtual environment to isolate dependencies:  
python -m venv venv

Activate the environment:  
- On Linux/macOS:  
  source venv/bin/activate  
- On Windows (Command Prompt):  
  venv\Scripts\activate

### 3. Install Python dependencies
The `requirements.txt` file is located **one directory level above** the `backend` folder, so install dependencies with:  
pip install -r ../requirements.txt

### 4. Configure environment variables
Copy the example environment file:  
cp .env.example .env

Open `.env` in a text editor and update variables according to your local setup, for example:  
DEBUG=True  
SECRET_KEY=your_secret_key_here  
DB_NAME=todo_db  
DB_USER=todo_user  
DB_PASSWORD=your_password  
DB_HOST=localhost  
DB_PORT=5432

### 5. Set up PostgreSQL database
Make sure PostgreSQL is installed and running on your machine.  
To create the database and user, connect to PostgreSQL using `psql` or a GUI tool and run:  
CREATE DATABASE todo_db;  
CREATE USER todo_user WITH PASSWORD 'your_password';  
GRANT ALL PRIVILEGES ON DATABASE todo_db TO todo_user;

### 6. Apply database migrations
Run migrations to create the database schema:  
python manage.py migrate

### 7. (Optional) Create a superuser
To access the Django admin panel, create a superuser:  
python manage.py createsuperuser

### 8. Run the development server
Start the Django development server:  
python manage.py runserver

Your API will be available at:  
http://127.0.0.1:8000/api/

---
## Docker Setup

This section explains how to set up and run the project using Docker and Docker Compose.

### 1. Build and start the containers
Make sure you have Docker and Docker Compose installed on your machine.

Run the following command from the root folder (where `docker-compose.yml` is located):  
docker-compose up --build

This command will:  
- Build the Docker images for the web app.  
- Start the PostgreSQL database container.  
- Start the Django web server.

### 2. Environment variables
Make sure you have a `.env` file in the root folder with all necessary environment variables:  
SECRET_KEY=your_secret_key_here  
DEBUG=True  
DB_NAME=todo_db  
DB_USER=todo_user  
DB_PASSWORD=your_password  
DB_HOST=db  
DB_PORT=5432

> **Note:** The project initially did not start inside Docker because `settings.py` had hard-coded database credentials.  
> To fix this, all database settings must be loaded from environment variables as shown above.  
> Make sure your `settings.py` uses environment variables (e.g., via `os.getenv`) instead of hard-coded values.

### 3. Apply database migrations inside the running web container
Open a new terminal and run:  
docker-compose exec web python manage.py migrate

### 4. (Optional) Create a superuser inside the running web container
To create a superuser, run:  
docker-compose exec web python manage.py createsuperuser

### 5. Access the API
Once the containers are running, the API will be available at:  
http://localhost:8000/api/

---
### Stopping containers
To stop and remove the containers, run:  
docker-compose down

---
## User Registration and Authentication

- New users can register by sending a POST request to `/api/users/` without authentication.  
- Accessing the list of users (`GET /api/users/`) requires admin rights and a valid JWT token.  
- Authentication is handled via JWT (JSON Web Tokens) — obtain tokens at `/api/token/`.  
- All API endpoints except registration require authentication by default.

---
## Running Tests

- The project includes unit tests covering:  
  - User registration (including weak password and duplicate username cases)  
  - JWT token obtain/refresh  
  - Permissions and access control (401/403 cases)  
  - Task CRUD operations with ownership checks  
  - Filtering tasks by status (including invalid filters)  

Run tests with:  
python manage.py test

---
## Project Structure Notes

> The project root folder has this structure:  
> todo_project/  
> ├── backend/           # Django project folder with manage.py  
> ├── requirements.txt   # Python dependencies  
> └── docker-compose.yml # Docker config  
>  
> Commands like `manage.py` should be run from `backend/`.  
> When installing dependencies, use `../requirements.txt` because it's outside `backend/`.

---
## Summary of key points
- Always run Django commands **inside the `backend` folder** because `manage.py` is located there.  
- The `requirements.txt` file is located **one level above** `backend`, so use `../requirements.txt` when installing dependencies.  
- Use the `.env` file for sensitive settings like database credentials and secret keys.  
- Ensure your PostgreSQL database and user match the `.env` configuration.  
- Apply migrations before running the server.  
- Creating a superuser is optional but recommended for admin access.  
- For Docker, set `DB_HOST=db` in `.env` to connect to the database container.  
- Use `docker-compose exec web python manage.py migrate` to apply migrations inside Docker.  

---
## Author
Teymuraz Safarov
