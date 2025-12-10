# ProTaskFlow - API & Integrations Guide

## REST API Overview

Our API allows you to programmatically access ProTaskFlow data and automate workflows.

**Base URL**: `https://api.protaskflow.com/v1`

### Authentication

All API requests require authentication using an API key.

#### Getting Your API Key
1. Go to **Settings** > **API** (Business+ plan required)
2. Click "Generate New Key"
3. Copy and store your key securely (it won't be shown again)

#### Using Your API Key
Include the key in the Authorization header:
```
Authorization: Bearer YOUR_API_KEY
```

### Rate Limits
- **Business**: 1,000 requests/hour
- **Enterprise**: 10,000 requests/hour

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Your limit
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Reset timestamp

---

## Common Endpoints

### Tasks

#### List Tasks
```
GET /tasks
```
Query parameters:
- `project_id`: Filter by project
- `assignee_id`: Filter by assignee
- `status`: Filter by status
- `limit`: Results per page (max 100)
- `offset`: Pagination offset

#### Create Task
```
POST /tasks
```
Body:
```json
{
  "title": "Task title",
  "description": "Task description",
  "project_id": "proj_123",
  "assignee_id": "user_456",
  "due_date": "2024-12-31",
  "priority": "high"
}
```

#### Update Task
```
PATCH /tasks/{task_id}
```

#### Delete Task
```
DELETE /tasks/{task_id}
```

### Projects

#### List Projects
```
GET /projects
```

#### Create Project
```
POST /projects
```
Body:
```json
{
  "name": "Project Name",
  "workspace_id": "ws_123",
  "template": "software_development"
}
```

### Users

#### List Workspace Members
```
GET /workspaces/{workspace_id}/members
```

#### Get Current User
```
GET /me
```

---

## Webhooks

Receive real-time notifications when events occur.

### Setup
1. Go to **Settings** > **API** > **Webhooks**
2. Click "Add Webhook"
3. Enter your endpoint URL
4. Select events to receive
5. Save and copy the signing secret

### Events
- `task.created`
- `task.updated`
- `task.deleted`
- `task.completed`
- `project.created`
- `project.updated`
- `comment.created`
- `member.added`
- `member.removed`

### Webhook Payload Example
```json
{
  "event": "task.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "task_id": "task_789",
    "title": "New Task",
    "project_id": "proj_123",
    "created_by": "user_456"
  }
}
```

### Verifying Webhooks
Verify the signature in the `X-PTF-Signature` header using your signing secret.

---

## Native Integrations

### Slack Integration

#### Setup
1. Go to **Settings** > **Integrations** > **Slack**
2. Click "Connect to Slack"
3. Authorize the ProTaskFlow app
4. Select default channel for notifications

#### Features
- Create tasks from Slack messages: `/ptf create [task name]`
- Get task updates in channels
- Complete tasks: `/ptf done [task id]`
- View task details: `/ptf info [task id]`

### Google Workspace

#### Calendar Sync
1. Connect Google Calendar in **Settings** > **Integrations**
2. Tasks with due dates appear on your calendar
3. Changes sync both ways

#### Google Drive
- Attach Drive files directly to tasks
- Preview documents without leaving ProTaskFlow
- Automatic permission handling

### Microsoft 365

#### Teams Integration
- Create tasks from Teams chats
- Get notifications in Teams channels
- Link to tasks opens in ProTaskFlow

#### Outlook Calendar
- Two-way sync with task due dates
- Meeting notes link to projects
- Email-to-task functionality

### GitHub/GitLab

#### Setup
1. Connect your repository in **Settings** > **Integrations**
2. Link commits to tasks using `PTF-123` in commit messages
3. Auto-update task status on PR merge

#### Features
- View linked commits on tasks
- Auto-close tasks when PRs merge
- Create branches from tasks

---

## Zapier Integration

Connect ProTaskFlow to 3000+ apps using Zapier.

### Common Zaps
- **New form submission** → Create ProTaskFlow task
- **New email (Gmail)** → Create ProTaskFlow task
- **Task completed** → Send Slack message
- **New task** → Add row to Google Sheets
- **Due date approaching** → Send reminder via SMS

### Setup
1. Go to [zapier.com](https://zapier.com)
2. Search for "ProTaskFlow"
3. Connect your account
4. Create your Zap

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad request - Check your parameters |
| 401 | Unauthorized - Invalid API key |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not found - Resource doesn't exist |
| 429 | Rate limited - Slow down |
| 500 | Server error - Contact support |

---

## SDK Libraries

Official SDKs:
- **Python**: `pip install protaskflow`
- **JavaScript/Node**: `npm install protaskflow`
- **Ruby**: `gem install protaskflow`

Community SDKs:
- Go, PHP, Java (see GitHub)

### Python Example
```python
from protaskflow import Client

client = Client(api_key="YOUR_API_KEY")

# Create a task
task = client.tasks.create(
    title="Review documentation",
    project_id="proj_123",
    priority="high"
)

# List all tasks
tasks = client.tasks.list(status="todo")
```
