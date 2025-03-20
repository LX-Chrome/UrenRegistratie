# Time Registrator API Documentation

This document provides detailed information about the Time Registrator API, allowing you to integrate the application with other systems and build custom solutions.

## API Overview

The Time Registrator provides a RESTful API that follows standard HTTP conventions:

- Uses standard HTTP methods (GET, POST, PUT, DELETE)
- Returns JSON-formatted responses
- Uses HTTP status codes to indicate success or failure
- Requires authentication via API keys

## Authentication

All API requests require authentication using an API key. The API key should be included in the request header.

### API Key Header

```
X-API-Key: your_api_key_here
```

The API key can be found in your `.env` file or generated through the application's admin interface.

### Example Request with Authentication

```bash
curl -X GET https://your-timeregistrator-instance.com/api/time-entries \
     -H "X-API-Key: your_api_key_here"
```

## Endpoints

### Time Entries

#### Get All Time Entries

```
GET /api/time-entries
```

Retrieves a list of time entries. Supports filtering by various parameters.

**Query Parameters:**

| Parameter | Type   | Description                          |
|-----------|--------|--------------------------------------|
| user_id   | int    | Filter by user ID                    |
| project   | string | Filter by project name               |
| start_date| string | Filter entries after this date (YYYY-MM-DD) |
| end_date  | string | Filter entries before this date (YYYY-MM-DD) |
| limit     | int    | Limit the number of results (default: 100) |
| offset    | int    | Offset for pagination (default: 0)   |

**Response:**

```json
{
  "time_entries": [
    {
      "id": 1,
      "user_id": 42,
      "date": "2023-04-15",
      "hours": 8.5,
      "description": "Implemented new dashboard features",
      "project": "Website Redesign",
      "created_at": "2023-04-15T17:30:45Z"
    },
    {
      "id": 2,
      "user_id": 42,
      "date": "2023-04-16",
      "hours": 6.25,
      "description": "Bug fixes and testing",
      "project": "Website Redesign",
      "created_at": "2023-04-16T16:42:10Z"
    }
  ],
  "total": 2,
  "limit": 100,
  "offset": 0
}
```

#### Get a Specific Time Entry

```
GET /api/time-entries/{id}
```

Retrieves a specific time entry by its ID.

**Response:**

```json
{
  "id": 1,
  "user_id": 42,
  "date": "2023-04-15",
  "hours": 8.5,
  "description": "Implemented new dashboard features",
  "project": "Website Redesign",
  "created_at": "2023-04-15T17:30:45Z"
}
```

#### Create a Time Entry

```
POST /api/time-entries
```

Creates a new time entry.

**Request Body:**

```json
{
  "user_id": 42,
  "date": "2023-04-17",
  "hours": 7.5,
  "description": "Client meeting and feature planning",
  "project": "Website Redesign"
}
```

**Response:**

```json
{
  "id": 3,
  "user_id": 42,
  "date": "2023-04-17",
  "hours": 7.5,
  "description": "Client meeting and feature planning",
  "project": "Website Redesign",
  "created_at": "2023-04-17T14:22:33Z"
}
```

#### Update a Time Entry

```
PUT /api/time-entries/{id}
```

Updates an existing time entry.

**Request Body:**

```json
{
  "hours": 8.0,
  "description": "Client meeting, feature planning, and initial implementation"
}
```

**Response:**

```json
{
  "id": 3,
  "user_id": 42,
  "date": "2023-04-17",
  "hours": 8.0,
  "description": "Client meeting, feature planning, and initial implementation",
  "project": "Website Redesign",
  "created_at": "2023-04-17T14:22:33Z",
  "updated_at": "2023-04-17T18:15:42Z"
}
```

#### Delete a Time Entry

```
DELETE /api/time-entries/{id}
```

Deletes a time entry.

**Response:**

```json
{
  "success": true,
  "message": "Time entry deleted successfully"
}
```

### Projects

#### Get All Projects

```
GET /api/projects
```

Retrieves a list of all projects.

**Query Parameters:**

| Parameter | Type   | Description                          |
|-----------|--------|--------------------------------------|
| client_id | int    | Filter by client ID                  |
| status    | string | Filter by status (active, completed, etc.) |
| limit     | int    | Limit the number of results (default: 100) |
| offset    | int    | Offset for pagination (default: 0)   |

**Response:**

```json
{
  "projects": [
    {
      "id": 1,
      "title": "Website Redesign",
      "client_id": 5,
      "description": "Complete overhaul of company website",
      "required_skills": "HTML, CSS, JavaScript, UI/UX Design",
      "created_at": "2023-03-10T09:22:18Z"
    },
    {
      "id": 2,
      "title": "Mobile App Development",
      "client_id": 8,
      "description": "Develop a companion mobile app",
      "required_skills": "React Native, API Integration",
      "created_at": "2023-03-15T11:44:30Z"
    }
  ],
  "total": 2,
  "limit": 100,
  "offset": 0
}
```

#### Get a Specific Project

```
GET /api/projects/{id}
```

Retrieves a specific project by its ID.

**Response:**

```json
{
  "id": 1,
  "title": "Website Redesign",
  "client_id": 5,
  "client_name": "Acme Corporation",
  "description": "Complete overhaul of company website",
  "required_skills": "HTML, CSS, JavaScript, UI/UX Design",
  "created_at": "2023-03-10T09:22:18Z",
  "activities": [
    {
      "id": 1,
      "employee_id": 12,
      "employee_name": "John Smith",
      "hours": 45.5,
      "description": "Frontend development and styling"
    },
    {
      "id": 2,
      "employee_id": 15,
      "employee_name": "Jane Doe",
      "hours": 32.25,
      "description": "Backend API integration"
    }
  ]
}
```

### Clients

#### Get All Clients

```
GET /api/clients
```

Retrieves a list of all clients.

**Query Parameters:**

| Parameter | Type   | Description                          |
|-----------|--------|--------------------------------------|
| search    | string | Search term for client name or email |
| limit     | int    | Limit the number of results (default: 100) |
| offset    | int    | Offset for pagination (default: 0)   |

**Response:**

```json
{
  "clients": [
    {
      "id": 5,
      "company_name": "Acme Corporation",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@acme.com",
      "phone": "+1234567890",
      "created_at": "2023-02-15T14:30:22Z"
    },
    {
      "id": 8,
      "company_name": "TechStart Inc.",
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane.smith@techstart.com",
      "phone": "+0987654321",
      "created_at": "2023-02-28T10:15:42Z"
    }
  ],
  "total": 2,
  "limit": 100,
  "offset": 0
}
```

#### Get a Specific Client

```
GET /api/clients/{id}
```

Retrieves a specific client by its ID.

**Response:**

```json
{
  "id": 5,
  "company_name": "Acme Corporation",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@acme.com",
  "phone": "+1234567890",
  "address": "123 Business St, City, Country",
  "created_at": "2023-02-15T14:30:22Z",
  "projects": [
    {
      "id": 1,
      "title": "Website Redesign",
      "description": "Complete overhaul of company website"
    }
  ]
}
```

### Employees

#### Get All Employees

```
GET /api/employees
```

Retrieves a list of all employees.

**Query Parameters:**

| Parameter | Type   | Description                          |
|-----------|--------|--------------------------------------|
| search    | string | Search term for employee name or email |
| role      | string | Filter by employee role              |
| limit     | int    | Limit the number of results (default: 100) |
| offset    | int    | Offset for pagination (default: 0)   |

**Response:**

```json
{
  "employees": [
    {
      "id": 12,
      "first_name": "John",
      "last_name": "Smith",
      "email": "john.smith@company.com",
      "role": "Developer",
      "office": "Main Office",
      "created_at": "2022-08-10T09:15:30Z"
    },
    {
      "id": 15,
      "first_name": "Jane",
      "last_name": "Doe",
      "email": "jane.doe@company.com",
      "role": "Designer",
      "office": "Branch Office",
      "created_at": "2022-09-22T14:32:18Z"
    }
  ],
  "total": 2,
  "limit": 100,
  "offset": 0
}
```

#### Get a Specific Employee

```
GET /api/employees/{id}
```

Retrieves a specific employee by their ID.

**Response:**

```json
{
  "id": 12,
  "first_name": "John",
  "last_name": "Smith",
  "email": "john.smith@company.com",
  "birth_date": "1985-06-15",
  "role": "Developer",
  "office": "Main Office",
  "created_at": "2022-08-10T09:15:30Z",
  "projects": [
    {
      "id": 1,
      "title": "Website Redesign",
      "hours": 45.5
    }
  ],
  "skills": [
    "JavaScript",
    "React",
    "Node.js",
    "HTML",
    "CSS"
  ]
}
```

### Check-ins

#### Get Today's Check-ins

```
GET /api/check-ins/today
```

Retrieves check-ins for the current day.

**Query Parameters:**

| Parameter | Type   | Description                          |
|-----------|--------|--------------------------------------|
| user_id   | int    | Filter by user ID                    |

**Response:**

```json
{
  "check_ins": [
    {
      "id": 101,
      "user_id": 42,
      "check_in_time": "2023-04-17T08:30:22Z",
      "status": "working",
      "note": "Starting work on website redesign"
    },
    {
      "id": 102,
      "user_id": 42,
      "check_in_time": "2023-04-17T12:00:15Z",
      "status": "break",
      "note": "Lunch break"
    },
    {
      "id": 103,
      "user_id": 42,
      "check_in_time": "2023-04-17T13:00:33Z",
      "status": "working",
      "note": "Back from lunch"
    }
  ],
  "total": 3
}
```

#### Create a Check-in

```
POST /api/check-ins
```

Creates a new check-in entry.

**Request Body:**

```json
{
  "user_id": 42,
  "status": "done",
  "note": "Finished for the day"
}
```

**Response:**

```json
{
  "id": 104,
  "user_id": 42,
  "check_in_time": "2023-04-17T17:30:45Z",
  "status": "done",
  "note": "Finished for the day"
}
```

### Reports

#### Generate Time Report

```
GET /api/reports/time
```

Generates a time report based on specified parameters.

**Query Parameters:**

| Parameter   | Type   | Description                          |
|-------------|--------|--------------------------------------|
| start_date  | string | Start date for report (YYYY-MM-DD)   |
| end_date    | string | End date for report (YYYY-MM-DD)     |
| user_id     | int    | Filter by user ID (optional)         |
| project     | string | Filter by project name (optional)    |
| format      | string | Output format (json, csv, xlsx, pdf) |

**Response (JSON format):**

```json
{
  "report": {
    "title": "Time Report",
    "start_date": "2023-04-01",
    "end_date": "2023-04-17",
    "generated_at": "2023-04-17T18:22:33Z",
    "total_hours": 120.5,
    "entries_by_project": {
      "Website Redesign": 85.25,
      "Mobile App Development": 35.25
    },
    "entries_by_day": {
      "2023-04-01": 8.0,
      "2023-04-02": 0.0,
      "2023-04-03": 7.5,
      // ...additional days
      "2023-04-17": 8.0
    },
    "entries": [
      {
        "id": 1,
        "user_id": 42,
        "date": "2023-04-15",
        "hours": 8.5,
        "description": "Implemented new dashboard features",
        "project": "Website Redesign"
      },
      // ...additional entries
    ]
  }
}
```

#### Generate Project Report

```
GET /api/reports/project/{project_id}
```

Generates a detailed report for a specific project.

**Query Parameters:**

| Parameter   | Type   | Description                          |
|-------------|--------|--------------------------------------|
| start_date  | string | Start date for report (YYYY-MM-DD)   |
| end_date    | string | End date for report (YYYY-MM-DD)     |
| format      | string | Output format (json, csv, xlsx, pdf) |

**Response (JSON format):**

```json
{
  "report": {
    "title": "Project Report - Website Redesign",
    "project_id": 1,
    "client": "Acme Corporation",
    "start_date": "2023-04-01",
    "end_date": "2023-04-17",
    "generated_at": "2023-04-17T18:30:45Z",
    "total_hours": 85.25,
    "employee_contributions": [
      {
        "employee_id": 12,
        "name": "John Smith",
        "hours": 45.5,
        "percentage": 53.4
      },
      {
        "employee_id": 15,
        "name": "Jane Doe",
        "hours": 39.75,
        "percentage": 46.6
      }
    ],
    "daily_progress": {
      "2023-04-01": 5.5,
      "2023-04-02": 0.0,
      "2023-04-03": 6.25,
      // ...additional days
      "2023-04-17": 8.0
    }
  }
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. The current limits are:

- 60 requests per minute per API key
- 1000 requests per day per API key

Rate limit information is included in the response headers:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1618675200
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of a request:

- 200 OK - The request was successful
- 201 Created - A resource was successfully created
- 400 Bad Request - The request was invalid
- 401 Unauthorized - Authentication failed
- 403 Forbidden - The request is not allowed
- 404 Not Found - The requested resource was not found
- 429 Too Many Requests - Rate limit exceeded
- 500 Server Error - An error occurred on the server

Error responses include a JSON object with details about the error:

```json
{
  "error": {
    "code": 400,
    "message": "Invalid date format. Use YYYY-MM-DD format."
  }
}
```

## Webhook Notifications

The Time Registrator API supports webhooks for real-time notifications about system events.

### Available Events

- `time_entry.created` - A new time entry is created
- `time_entry.updated` - A time entry is updated
- `time_entry.deleted` - A time entry is deleted
- `check_in.created` - A new check-in is recorded
- `project.created` - A new project is created
- `project.updated` - A project is updated

### Webhook Registration

To register a webhook, make a POST request to:

```
POST /api/webhooks
```

**Request Body:**

```json
{
  "url": "https://your-application.com/webhook-receiver",
  "events": ["time_entry.created", "time_entry.updated"],
  "description": "Notify our system about time entry changes"
}
```

**Response:**

```json
{
  "id": "wh_123456",
  "url": "https://your-application.com/webhook-receiver",
  "events": ["time_entry.created", "time_entry.updated"],
  "description": "Notify our system about time entry changes",
  "created_at": "2023-04-17T19:30:22Z",
  "secret": "whsec_abcdefghijklmnopqrstuvwxyz"
}
```

### Webhook Payloads

Webhook payloads include information about the event and the affected resource:

```json
{
  "event": "time_entry.created",
  "created_at": "2023-04-17T19:45:32Z",
  "data": {
    "id": 5,
    "user_id": 42,
    "date": "2023-04-17",
    "hours": 7.5,
    "description": "API integration development",
    "project": "Website Redesign",
    "created_at": "2023-04-17T19:45:30Z"
  }
}
```

### Webhook Security

Webhook requests include a signature in the `X-Webhook-Signature` header for verification. To verify the signature:

1. Get the request body as a string
2. Create an HMAC with SHA-256 using your webhook secret
3. Compare the computed signature with the value in the `X-Webhook-Signature` header

Example verification code (Python):

```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    computed_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed_signature, signature)
```

## API Versioning

The API uses versioning to ensure compatibility as the API evolves. The current version is v1.

You can specify the API version in the request URL:

```
https://your-timeregistrator-instance.com/api/v1/time-entries
```

If no version is specified, the latest version will be used.

## Pagination

For endpoints that return lists of items, pagination is supported using the `limit` and `offset` query parameters:

- `limit`: The maximum number of items to return (default: 100, max: 500)
- `offset`: The number of items to skip (default: 0)

Response objects include pagination metadata:

```json
{
  "time_entries": [ /* items */ ],
  "total": 237,
  "limit": 100,
  "offset": 0
}
```

## Conclusion

This API documentation covers the main functionality of the Time Registrator API. For additional support or questions, please contact the application administrator or refer to the main application documentation. 