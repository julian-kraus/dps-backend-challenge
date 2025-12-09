# dps-backend-challenge
A Django-based backend service for managing round-robin sports tournaments. Supports creating tournaments and players, recording match results, and generating live tournament status and leaderboards. Built with PostgreSQL and designed for easy local setup and clean, modular REST API development.

## Running the project

### 1. Copy environment variables

This project uses environment variables for both Django and PostgreSQL.  
Start by copying the example file:

```bash
cp .env.example .env
```
You can keep the defaults for local development or adjust values (e.g. database name, user, password) as needed.


2. Start the services with Docker

Build and run the Django + Postgres stack using Docker Compose:

docker-compose up --build

This will:
	•	Build the Django backend image
	•	Start the Postgres database
	•	Run database migrations
	•	Run the test suite
	•	Start the Django development server on http://localhost:8000

You should see Django’s startup logs in the console once everything is ready.

3. Smoke-test the API with the helper script

A small script is included to exercise the main API flows end-to-end:
	•	Create players
	•	Create a tournament
	•	Add players as participants
	•	Record game results
	•	Fetch tournament status and leaderboard

From the project root, run:

```bash
./test_api.sh
```
The script uses curl (and optionally jq if available) to hit the running API and print JSON responses to the console. Make sure the Docker services are up (docker-compose up) before running it.

After running the script you should see:
	•	JSON output for created players and tournament
	•	Participants added to the tournament
	•	Status changing from in_planning to started
	•	A leaderboard with calculated points