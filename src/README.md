# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- View active announcements loaded from MongoDB
- Manage announcements from the UI when signed in as a teacher

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| GET    | `/announcements`                                                  | Get only active announcements for the public site                  |
| GET    | `/announcements/manage?teacher_username=principal`                | Get all announcements for the management dialog                    |
| POST   | `/announcements?teacher_username=principal`                       | Create an announcement with title, message, start date, and expiration date |
| PUT    | `/announcements/{announcement_id}?teacher_username=principal`     | Update an existing announcement                                    |
| DELETE | `/announcements/{announcement_id}?teacher_username=principal`     | Delete an announcement                                             |

## Data Model

The application uses MongoDB with a simple data model and seeded example content:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

3. **Announcements** - Uses a generated identifier:
   - Title
   - Message
   - Optional start date
   - Required expiration date
   - Seeded with an example registration reminder during database initialization

Data is stored in MongoDB, and the initial sample activities, teachers, and announcement are created automatically when the collections are empty.
