# AI Usage

I used ChatGPT selectively throughout this challenge as a support tool, mainly to speed up routine work and to sanity-check certain implementation details. All architectural decisions, data model design, tournament logic, and final code were written and validated by me.

## What AI Was Used For

- **Clarifications & quick checks**  
  Short questions related to Docker, environment variables, health checks, and Django testing configuration.
  
- **Boilerplate generation**  
  Drafting patterns for Django viewsets, serializers, and DRF testing structures. These were then adapted by me to fit the project’s conventions and actual logic.

- **Test scaffolding**  
  I described the exact test style I wanted (APITestCase + pytest + reverse()) and AI produced skeleton test code, which I reviewed, edited, and integrated into the real test suite.

- **Documentation and wording**  
  Producing initial versions of README.md sections and improving sentence clarity. These drafts were refined manually.

## What AI Was *Not* Used For

- Designing the database schema, tournament rules logic, or API endpoints  
- Implementing the scoring logic, leaderboard generation, or tournament status algorithm  
- Deciding how the application behaves or how edge cases are handled  
- Writing final production code without manual revision

## Notes on AI-Generated Code

Some generated snippets were discarded, and others required adjustments (e.g., adapting test code to my actual URL structure, replacing generic serializer logic, or fixing assumptions about model fields). Final code reflects my own decisions and modifications.

## Example Prompts Used

Below are representative examples of prompts I used (links omitted because the sessions are private):


```
Can you check this docker-compose.yml and Dockerfile and tell me if there is any room for improvement? [Copied docker-compose.yml and Dockerfile]
```


```
How can I add a health endpoint in Django so Docker can check if the service is alive?
```

```
How do I set up pytest correctly for a Django project, and use it with APITestCase?
```

```
Create tests for the Player endpoints using APITestCase:
	•	test listing players (initially empty)
	•	test creating a player
	•	test updating a player
	•	test deleting a player
Use Django reverse() for URL resolution.
Structure the code similar to these test implementations:
[Copied old test code]
```

```
Can you help me outline instructions for running the project in Docker, including copying the .env file and docker-compose up --build?
```

```
Can you give me an example of a shell script that uses curl to test my endpoints?
```