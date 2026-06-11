# 🚀 Spark CRM Backend

An AI-powered CRM backend built for modern digital agencies to streamline client management, project tracking, relationship intelligence, proposal generation, and communication workflows.

Designed with a production-oriented architecture, Spark CRM combines traditional CRM capabilities with AI-driven automation to help agencies spend less time on administration and more time delivering value.

---

## ✨ Key Highlights

* 🔐 JWT Authentication & Authorization
* 👥 Multi-Tenant Agency CRM
* 📊 AI-Powered Client Health Scoring (Coming Soon)
* 🧠 AI Client Relationship Insights & Recommendations (Coming Soon)
* 📄 Automated Proposal Generation (Coming Soon)
* ✉️ AI Email Draft Generation (Coming Soon)
* 📈 AI Usage Analytics & Token Tracking (Coming Soon)
* 🗂️ Client, Project, Activity & Proposal Management
* 🔍 Advanced Filtering & Search
* 🛡️ User Data Isolation & Ownership
* ⚡ RESTful API with OpenAPI Documentation

---

## 🎯 Problem Statement

Digital agencies often manage client communication, proposals, projects, and follow-ups across multiple disconnected tools.

Spark CRM centralizes these workflows while leveraging AI to:

* Predict client relationship health
* Generate project proposals
* Draft professional client emails
* Produce actionable client recommendations
* Track AI usage and operational efficiency

---

## 🏗️ System Architecture

```text
┌──────────────────────┐
│     Frontend App     │
└──────────┬───────────┘
           │ REST API
           ▼
┌──────────────────────┐
│     FastAPI Backend  │
├──────────────────────┤
│ Authentication       │
│ Client Management    │
│ Project Management   │
│ Activity Tracking    │
│ Proposal Engine      │
│ Email Draft Engine   │
│ AI Services Layer    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      Database        │
└──────────────────────┘

           │
           ▼

┌──────────────────────┐
│      LLM Provider    │
│ (OpenAI / Gemini)    │
└──────────────────────┘
```

---

# Core Features

## 🔐 Authentication

Secure authentication system supporting:

* User Registration
* OAuth2 Password Flow
* JWT Access Tokens
* User Profile Management
* Soft Account Deletion

### Endpoints

```http
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/auth/me
DELETE /api/v1/auth/me
```

---

## 👥 Client Management

Manage agency clients through their entire lifecycle.

### Features

* Client onboarding
* Lead management
* Prospect tracking
* Client segmentation
* Contact management
* Industry classification
* Tagging system
* Notes & relationship tracking

### Client Statuses

```text
prospect
active
inactive
```

### Client Sources

```text
referral
website
cold_outreach
existing
other
```

---

## 📊 AI Client Health Scoring

One of the platform's flagship features.

The system analyzes:

* Communication frequency
* Recent activities
* Client engagement history
* Relationship signals

to generate a health score indicating the strength of the client relationship.

### Example Response

```json
{
  "health_score": 86,
  "explanation": "Regular communication and consistent engagement indicate a healthy client relationship."
}
```

### Endpoint

```http
POST /api/v1/clients/{client_id}/score-health
```

---

## 🧠 AI Client Intelligence

Generate AI-powered relationship summaries and recommendations.

### Capabilities

* Relationship analysis
* Account health reviews
* Client risk detection
* Growth opportunities
* Recommended next actions

### Endpoint

```http
GET /api/v1/clients/{client_id}/ai-summary
```

---

## 📁 Project Management

Track client projects from lead to delivery.

### Supported States

```text
prospect
proposal_sent
in_progress
completed
paused
```

### Features

* Budget tracking
* Estimated hours
* Timeline management
* Project lifecycle monitoring
* Client-project relationships

---

## 📝 Activity Tracking

Maintain a complete audit trail of client interactions.

### Activity Types

```text
email
call
meeting
proposal
note
```

### Automated Intelligence

When activities are created:

* Client last-contact date updates
* Relationship metrics refresh
* Health score recalculations trigger automatically

---

## 🤖 AI Proposal Generator

Generate professional client proposals using AI.

The proposal engine automatically creates:

* Project scope
* Deliverables
* Timeline
* Budget estimation

### Endpoint

```http
POST /api/v1/proposals/generate
```

### Generated Output

```text
Project Scope
Deliverables
Timeline
Estimated Cost
```

---

## ✉️ AI Email Draft Generator

Generate context-aware client communications.

### Supported Use Cases

```text
follow_up
proposal
check_in
custom
```

### Examples

* Client follow-ups
* Project updates
* Proposal submissions
* Relationship nurturing emails

### Endpoint

```http
POST /api/v1/email-drafts/generate
```

---

## 📈 AI Usage Analytics

Monitor AI consumption and platform usage.

Tracked Metrics:

* Total AI interactions
* Input tokens
* Output tokens
* Usage by feature
* Token consumption by feature

### Endpoint

```http
GET /api/v1/ai/stats
```

---

# REST API Resources

| Resource     | Operations                |
| ------------ | ------------------------- |
| Auth         | Register, Login, Profile  |
| Clients      | Full CRUD                 |
| Projects     | Full CRUD                 |
| Activities   | Full CRUD                 |
| Proposals    | Full CRUD + AI Generation |
| Email Drafts | Full CRUD + AI Generation |
| AI Analytics | Reporting                 |

---

# Security

### Authentication

* OAuth2 Password Flow
* JWT Access Tokens
* Protected Routes

### Data Ownership

All resources are scoped to authenticated users:

* Clients
* Projects
* Activities
* Proposals
* Email Drafts

This ensures complete tenant isolation between agencies.

---

# API Documentation

OpenAPI Specification Included

Interactive documentation available through:

```text
/docs
```

and

```text
/redoc
```

when running the application.

---

# Example Workflow

```text
Register Agency
      │
      ▼
Create Client
      │
      ▼
Create Project
      │
      ▼
Log Activities
      │
      ▼
Generate Health Score
      │
      ▼
Generate AI Summary
      │
      ▼
Generate Proposal
      │
      ▼
Generate Follow-up Email
```

---

# Why This Project Stands Out

This project demonstrates real-world backend engineering skills including:

### Backend Development

* REST API Design
* Authentication & Authorization
* Multi-Tenant Architecture
* Business Logic Modeling
* Data Validation

### AI Engineering

* LLM Integration
* Prompt-Oriented Workflows
* AI Feature Orchestration
* Usage Tracking & Analytics

### Software Architecture

* Separation of Concerns
* Service Layer Design
* Scalable Resource Modeling
* Domain-Driven API Structure

### Production Readiness

* OpenAPI Documentation
* Secure Authentication
* Resource Ownership Enforcement
* Consistent API Contracts

---

## Tech Stack

```text
FastAPI
Python
Pydantic
JWT Authentication
OpenAPI / Swagger
AI Provider APIs (OpenAI / Gemini)
PostgreSQL / SQL Database
```

---

## Future Improvements

* Team Collaboration
* CRM Pipelines
* AI Meeting Summaries
* AI Lead Scoring
* Webhook Integrations
* CRM Integrations (HubSpot, Salesforce)
* Email Sending Infrastructure
* Subscription Billing
* Real-Time Notifications

---

## License

MIT License

---

Built to demonstrate how modern AI capabilities can be embedded directly into business workflows, transforming a traditional CRM into an intelligent agency operating system.