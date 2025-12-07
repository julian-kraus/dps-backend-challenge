# dps-backend-challenge
A Django-based backend service for managing round-robin sports tournaments. Supports creating tournaments and players, recording match results, and generating live tournament status and leaderboards. Built with PostgreSQL and designed for easy local setup and clean, modular REST API development.

## Setup

### Environment Variables

This project uses environment variables to configure the Django and Postgres services.  
An example file is included in the repository and can be used like this:

```
cp .env.example .env
```
The `.env.example` file contains safe default values required to run the application locally.  
The real `.env` file is not committed for security reasons.