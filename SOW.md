# Statement of Work (SOW)
## AI First Academy - Backend API Development

### 1. Project Overview
The **AI First Academy** project involves the development of a robust, scalable RESTful API to power an online learning management system (LMS). The platform serves three distinct user roles: Students, Instructors, and Administrators, facilitating course creation, enrollment, payment processing, and certification.

### 2. Scope of Work

#### 2.1. Authentication & User Management
- **JWT Authentication**: Secure login and registration with token-based authentication.
- **Role-Based Access Control (RBAC)**: Distinct permissions for Students, Instructors, and Admins.
- **User Profiles**: Management of personal details, bio, and profile pictures.
- **Instructor Promotion**: Admin capability to upgrade students to instructors.

#### 2.2. Course Management
- **Hierarchical Structure**: Master Categories → Subcategories → Courses → Modules → Lessons.
- **Course Lifecycle**: Draft, Published, and Archived states.
- **Content Management**:
  - Rich course metadata (title, description, difficulty, duration).
  - Lesson content types: Video URLs, Text content, and downloadable Resources.
  - Thumbnail and banner image management.
- **Prerequisites**: System to enforce course dependencies.

#### 2.3. Enrollment & Progress Tracking
- **Enrollment System**: Manage student access to purchased courses.
- **Progress Tracking**: Track lesson completion and calculate overall course progress percentage.
- **Access Control**: Ensure users can only access content they have enrolled in.

#### 2.4. Payment Processing
- **Multi-Gateway Support**: Integration with **Razorpay** and **Stripe**.
- **Checkout Flows**:
  - Order creation and payment verification flows.
  - Webhook handling for asynchronous payment status updates.
- **Financial Records**: Transaction history, invoice generation, and refund request management.

#### 2.5. Certification System
- **Automated Generation**: Create PDF certificates upon course completion.
- **Verification**: Publicly accessible verification URLs to validate certificate authenticity.
- **Management**: Users can download certificates; Admins can regenerate them if needed.

#### 2.6. Live Sessions
- **Scheduling**: Instructors can schedule live virtual classes.
- **Integration**: Storage for meeting URLs (Zoom/Google Meet) and recording links.
- **Notifications**: Automated alerts for upcoming sessions.

#### 2.7. Admin Dashboard
- **Analytics**: Visual breakdown of revenue, user growth, and popular courses.
- **User Management**: Search, filter, and edit user details.
- **Course Oversight**: Review and moderate published courses.
- **Financial Reports**: View global payment history and revenue stats.

### 3. Technical Requirements

#### 3.1. Backend Stack
- **Framework**: Python Flask (Modularized with Blueprints).
- **Database**: PostgreSQL with SQLAlchemy ORM.
- **Migrations**: Database schema version control via Flask-Migrate.

#### 3.2. Key Libraries & Integrations
- **Authentication**: `flask-jwt-extended`
- **Payments**: `razorpay`, `stripe`
- **PDF Generation**: `reportlab`
- **File Handling**: Local storage (expandable to S3/Cloud storage).
- **CORS**: Cross-Origin Resource Sharing configured for frontend clients.

### 4. Deliverables
1.  **Source Code**: Complete Flask codebase organized by routes and services.
2.  **Database Schema**: PostgreSQL models and migration scripts.
3.  **API Endpoints**: Fully functional REST API for all modules (Auth, Courses, Payments, etc.).
4.  **Documentation**: `AGENTS.md` for developer onboarding and this SOW.

### 5. Assumptions & Constraints
- **Hosting**: The API is designed to be hosted on a containerized environment (e.g., Docker).
- **Frontend**: This SOW covers only the Backend API; the Frontend (React/Vue) is a separate entity.
- **Mail Server**: Requires valid SMTP credentials for email notifications.
- **Payment Keys**: Requires valid API keys from Razorpay and Stripe for transaction processing.
