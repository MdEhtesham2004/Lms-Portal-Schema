# API Documentation

This document provides a comprehensive reference for the API endpoints available in the application.

## Base URL
All API endpoints are prefixed with `/api/v1` unless otherwise noted.

## Authentication (`/auth`)

| Method | Endpoint | Description | Auth Required | Rate Limit |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/register` | Register a new user (Student/Instructor). | No | 5/min |
| `POST` | `/login` | Login user and return JWT tokens. | No | 5/min |
| `POST` | `/logout` | Logout user and blacklist refresh token. | Yes | - |
| `POST` | `/refresh` | Refresh access token using refresh token. | Yes (Refresh) | - |
| `POST` | `/forgot-password` | Send password reset link to email. | No | - |
| `POST` | `/reset-password/<token>` | Reset password using token. | No | 5/min |
| `POST` | `/change-password` | Change password for logged-in user. | Yes | - |
| `POST` | `/google` | Google OAuth login/registration. | No | 5/min |
| `POST` | `/send-token` | Send OTP for verification. | No | 3/min |
| `POST` | `/verify-otp` | Verify OTP. | No | 5/min |

### Request/Response Details

**POST /register**
*   **Body:** `{ "email": "user@example.com", "password": "password123", "first_name": "John", "last_name": "Doe", "role": "student" }`
*   **Response:** `201 Created` - `{ "message": "User created successfully", "user": {...} }`

**POST /login**
*   **Body:** `{ "email": "user@example.com", "password": "password123" }`
*   **Response:** `200 OK` - `{ "access_token": "...", "refresh_token": "...", "user": {...} }`

---

## User Management (`/users`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/profile` | Get current user's profile. | Yes |
| `PUT` | `/profile` | Update current user's profile. | Yes |
| `GET` | `/my-courses` | Get courses the user is enrolled in. | Yes |
| `GET` | `/my-teaching-courses` | Get courses taught by the user (Instructor). | Yes (Instructor) |

### Request/Response Details

**GET /profile**
*   **Response:** `200 OK` - `{ "user": { "id": 1, "email": "...", ... } }`

**PUT /profile**
*   **Body:** `{ "first_name": "Jane", "bio": "..." }`
*   **Response:** `200 OK` - `{ "message": "Profile updated", "user": {...} }`

---

## Public Routes (`/public`)

| Method | Endpoint | Description | Rate Limit |
| :--- | :--- | :--- | :--- |
| `GET` | `/get-courses` | Get all published courses with filters. | 30/min |
| `GET` | `/get-courses/<id>` | Get details of a specific course. | 30/min |
| `GET` | `/get-categories` | Get all master categories. | 30/min |
| `GET` | `/get-subcategories` | Get all subcategories. | 30/min |
| `POST` | `/search` | Search courses by query. | 20/min |

### Request/Response Details

**GET /get-courses**
*   **Query Params:** `page`, `per_page`, `category_id`, `subcategory_id`, `search`
*   **Response:** `200 OK` - `{ "courses": [...], "pagination": {...} }`

---

## Courses (`/courses`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/create-courses` | Create a new course. | Yes (Instructor) |
| `GET` | `/get-courses` | Get all courses (Instructor view). | Yes (Instructor) |
| `GET` | `/get-courses/<id>` | Get specific course details. | Yes (Instructor) |
| `PUT` | `/update-courses/<id>` | Update a course. | Yes (Instructor) |
| `DELETE` | `/delete-courses/<id>` | Delete a course. | Yes (Instructor) |

### Request/Response Details

**POST /create-courses**
*   **Body:** `{ "title": "Python 101", "description": "...", "price": 49.99, "subcategory_id": 1 }`
*   **Response:** `201 Created` - `{ "message": "Course created", "course": {...} }`

---

## Master Categories (`/master-categories`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/create-mastercategories` | Create a master category. | Yes (Admin) |
| `POST` | `/get-mastercategories` | Get all master categories. | Yes (Admin) |
| `POST` | `/get-mastercategories/<id>` | Get a specific master category. | Yes (Admin) |
| `PUT` | `/update-mastercategories/<id>` | Update a master category. | Yes (Admin) |
| `DELETE` | `/delete-mastercategories/<id>` | Delete a master category. | Yes (Admin) |

---

## Subcategories (`/subcategories`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/create-subcategories` | Create a subcategory. | Yes (Admin) |
| `POST` | `/get-subcategories` | Get all subcategories. | Yes (Admin) |
| `POST` | `/get-subcategories/<id>` | Get a specific subcategory. | Yes (Admin) |
| `PUT` | `/update-subcategories/<id>` | Update a subcategory. | Yes (Admin) |
| `DELETE` | `/delete-subcategories/<id>` | Delete a subcategory. | Yes (Admin) |

---

## Modules (`/modules`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/create-modules/<course_id>` | Create a module for a course. | Yes (Instructor) |
| `POST` | `/get-modules` | Get all modules. | Yes (Instructor) |
| `POST` | `/get-modules/<id>` | Get a specific module. | Yes (Instructor) |
| `PUT` | `/update-modules/<id>` | Update a module. | Yes (Instructor) |
| `DELETE` | `/delete-modules/<id>` | Delete a module. | Yes (Instructor) |

---

## Lessons (`/lessons`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/create-lessons/<module_id>` | Create a lesson for a module. | Yes (Instructor) |
| `POST` | `/get-lessons` | Get all lessons. | Yes (Instructor) |
| `POST` | `/get-lessons/<id>` | Get a specific lesson. | Yes (Instructor) |
| `PUT` | `/update-lessons/<id>` | Update a lesson. | Yes (Instructor) |
| `DELETE` | `/delete-lessons/<id>` | Delete a lesson. | Yes (Instructor) |

---

## Lesson Resources (`/lesson-resources`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/create-lesson-resources/<lesson_id>` | Upload a resource for a lesson. | Yes (Instructor) |
| `POST` | `/get-lesson-resources` | Get all resources. | Yes |
| `POST` | `/get-lesson-resources/<id>` | Get a specific resource. | Yes |
| `PUT` | `/update-lesson-resources/<id>` | Update a resource. | Yes (Instructor) |
| `DELETE` | `/delete-lesson-resources/<id>` | Delete a resource. | Yes (Instructor) |

---

## Prerequisites (`/prerequisites`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/create-prerequisites/<course_id>` | Add prerequisites to a course. | Yes (Instructor/Admin) |
| `GET` | `/get-prerequisites/<course_id>` | Get prerequisites for a course. | No |
| `PUT` | `/update-prerequisites/<course_id>` | Update prerequisites. | Yes (Instructor/Admin) |
| `DELETE` | `/delete-prerequisites/<course_id>/<prereq_id>` | Remove a prerequisite. | Yes (Instructor/Admin) |

---

## Enrollments (`/enrollments`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/create-enrollments/<course_id>` | Enroll in a course (Free/Paid). | Yes |
| `GET` | `/get-enrollments` | Get current user's enrollments. | Yes |
| `GET` | `/get-enrollments/<course_id>/progress` | Get course progress. | Yes |
| `GET` | `/get-enrollments/<course_id>/lessons/<lesson_id>/progress` | Update lesson progress. | Yes |

---

## Payments (`/payments`)

| Method | Endpoint | Description | Auth Required | Rate Limit |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/create-order` | Create a Razorpay order. | Yes | 10/min |
| `POST` | `/verify-payment` | Verify Razorpay payment. | Yes | 20/min |
| `POST` | `/create-checkout-session` | Create Stripe checkout session. | Yes | 10/min |
| `GET` | `/history` | Get payment history. | Yes | - |
| `GET` | `/<id>` | Get payment details. | Yes | - |
| `POST` | `/<id>/refund` | Request a refund. | Yes | - |

---

## Files (`/files`)

| Method | Endpoint | Description | Auth Required | Rate Limit |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/upload` | Upload lesson resource file. | Yes (Instructor) | 20/hour |
| `GET` | `/download/<id>` | Download lesson resource. | Yes (Enrolled) | 100/hour |
| `POST` | `/upload-course-thumbnail` | Upload course thumbnail. | Yes (Instructor) | 20/hour |
| `POST` | `/upload-profile-picture` | Upload profile picture. | Yes | 10/hour |

---

## Notifications (`/notifications`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/get-notifications` | Get user notifications. | Yes |
| `PUT` | `/<id>/read` | Mark notification as read. | Yes |
| `PUT` | `/mark-all-read` | Mark all as read. | Yes |
| `DELETE` | `/<id>` | Delete notification. | Yes |
| `POST` | `/send` | Send notification to specific users. | Yes (Admin) |
| `POST` | `/broadcast` | Broadcast notification to all users. | Yes (Admin) |

---

## Certificates (`/certificates`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/get-certificate` | Get user's certificates. | Yes |
| `POST` | `/generate/<course_id>` | Generate certificate for completed course. | Yes |
| `GET` | `/download/<id>` | Download certificate PDF. | Yes |
| `GET` | `/verify/<number>` | Verify certificate validity. | No |

---

## Live Sessions (`/live-sessions`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/get-live-sessions` | Get live sessions. | Yes |
| `POST` | `/create-live-sessions` | Create a live session. | Yes (Instructor) |
| `GET` | `/get-live-sessions/<id>` | Get session details. | Yes |
| `PUT` | `/update-live-sessions/<id>` | Update session. | Yes (Instructor) |
| `DELETE` | `/delete-live-sessions/<id>` | Delete session. | Yes (Instructor) |
| `GET` | `/get-live-courses/upcoming` | Get upcoming sessions. | Yes |
| `GET` | `/join-live-sessions/<id>/join` | Join a live session. | Yes |

---

## Contact (`/contact`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/contact-forms` | Submit a contact form. | No |
| `GET` | `/contact-forms` | Get all contact forms. | No (Should be Admin) |
| `GET` | `/contact-forms/<id>` | Get specific contact form. | No (Should be Admin) |
| `PUT` | `/contact-forms/<id>` | Update contact form. | No (Should be Admin) |
| `DELETE` | `/contact-forms/<id>` | Delete contact form. | No (Should be Admin) |

### Request/Response Details

**POST /contact-forms**
*   **Body:** `{ "name": "John", "email": "john@example.com", "message": "Hello", "phone_number": "1234567890" }`
*   **Response:** `201 Created` - `{ "id": 1, "name": "John", ... }`

---

## Admin (`/admin`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/dashboard` | Get admin dashboard stats. | Yes (Admin) |
| `GET` | `/users` | Get all users. | Yes (Admin) |
| `PUT` | `/users/<id>` | Update user details. | Yes (Admin) |
| `DELETE` | `/users/<id>` | Deactivate user. | Yes (Admin) |
| `GET` | `/courses` | Get all courses. | Yes (Admin) |
| `PUT` | `/courses/<id>/status` | Update course status (publish/draft). | Yes (Admin) |
| `GET` | `/payments` | Get all payments. | Yes (Admin) |
| `GET` | `/analytics` | Get revenue and enrollment analytics. | Yes (Admin) |
