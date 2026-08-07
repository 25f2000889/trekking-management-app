# TrekFlow
TrekFlow is a comprehensive trekking management application designed to streamline the process of organizing and managing trekking activities. It provides features for user management, trek scheduling, booking management, and staff assignment.

## Technologies and Frameworks Used

| Technology/Library | Purpose |
|--------------------|---------|
| Flask | Core backend web framework |
| SQLAlchemy | Object Relational Mapper for SQLite database |
| Jinja2 | Template engine for rendering dynamic HTML pages |
| Bootstrap 5 | Frontend styling and responsive design |
| Flask JWT Extended | Creating JWT tokens for API clients for their authentication |
| SQLite | Lightweight local database for storing user data |

## Database Schema / ER Diagram

Tables:
1. **User** — stores user profile details (id, first_name, last_name, email, password_hash, role, status)
2. **Staff Profile** — stores staff member specific fields (id, user_id, experience, phone_number, address)
3. **Trek** — stores treks and their information (id, name, location, difficulty, duration_days, available_slots, assigned_staff_id, status, start_date, end_date, description)
4. **Trek Booking** — stores user bookings for specific treks (id, user_id, trek_id, booking_date, status)

Relationships:
- One-to-One → **User** → **Staff Profile**
- One-to-Many → **User** → **Trek Booking**
- One-to-Many → **Trek** → **Trek Booking**

## API Resource Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
/api/auth/login | POST | Authenticate user and generate JWT access token |
/api/auth/register | POST | Register user and generate JWT access token |
/api/treks | GET | Gets all treks for admin, assigned treks for staff member, and approved treks for trekkers |
/api/treks | POST | Add a new trek (admin only) |
/api/treks/{trek_id} | PUT | Update any trek by its trek id (admin only) |
/api/treks/{trek_id} | DELETE | Delete any trek by its trek id (admin only) |
/api/bookings | GET | Gets all trek bookings for admin, assigned treks’ bookings for staff member, and own bookings for trekkers |
/api/bookings | POST | Book a trek (trekker only) |
/api/bookings/{booking_id}/cancel | POST | Cancel any trek booking (admin only) |
/api/bookings/{booking_id}/restore | POST | Restore any previously cancelled trek booking (admin only) |
/api/users | GET | Get all the users (admin only) |
/api/users/{user_id} | PUT | Update user profile (also update staff profile too, if logged in as staff member) (only self profile updating allowed) |
/api/users/staff/{user_id}/approve | POST | Approve pending staff member request (admin only) |
/api/users/staff/{user_id}/reject | POST | Reject pending staff member request (admin only) |
/api/users/{user_id}/blacklist | POST | Blacklist any user (except admin) (admin only) |
/api/users/{user_id}/restore | POST | Restore any previously blacklisted user (admin only) |

YAML API Definition File:
Included separately in the submission ZIP as [api.yaml](api.yaml).

## Architecture and Features

### Architecture Overview:

- **README.md** – Project introduction as well as architecture overview
- **app.py** – main Flask application entry point
- **config.py** – the config class that loads the configuration
- **db.py** – initializes base model class and db object
- **decorators.py** – custom decorators used throughout the project
- **enums.py** – custom enums used throughout the project
- **seed.py** – the seed file which is used to prepopulate database with admin user if not present
- **utils.py** – utility functions used throughout the project
- **validation.py** – custom validation function used throughout the project to validate incoming input
- **/models** – database models using SQLAlchemy
- **/routes** – Flask Blueprints for user and trek routes (both web and api)
- **/services** – Encapsulates business logic and database operations using SQLAlchemy.
- **/static** – CSS used to style the HTML
- **/templates** – Jinja2 HTML templates

### Implemented Features:

- User registration and login with secure password hashing.
- Session-based authentication for the web interface and JWT authentication for REST APIs.
- Role-based authorization for Admin, Trek Staff, and Trekker users.
- Staff registration workflow with admin approval and rejection.
- User management including blacklisting and restoration of users.
- Trek creation, modification, deletion, and status management by administrators.
- Trek assignment to staff members.
- Trek browsing with role-specific visibility (approved treks for trekkers, assigned treks for staff, all treks for administrators).
- Trek booking, cancellation, and restoration functionality.
- Profile management for users, including staff-specific profile information.
- Input validation and centralized error handling for API requests.
- Responsive web interface built using Bootstrap 5.
- RESTful API documented using an OpenAPI YAML specification.

### Additional Features:

- Modular project structure using Flask Blueprints and service classes.
- Reusable authentication, authorization, and validation decorators.
- Optional JWT authentication on selected API endpoints for personalized responses.
- Database seeding utility for automatic administrator account creation.
- Type-annotated SQLAlchemy models with defined entity relationships.
- Consistent JSON response format for all API endpoints.

## Full Report
For full project report, please refer to the [TrekFlow Project Report](project_report.pdf)