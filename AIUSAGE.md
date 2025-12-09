# AI Usage

I used ChatGPT to speed up parts of the work, mainly around boilerplate and wording, rather than to make core design or logic decisions.

## What AI Was Used For
- Clarifications & quick checks: Short questions about Docker, environment variables, and basic configuration (e.g. docker-compose, healthchecks, test running on container startup).
- Documentation & wording: Generating rough versions of sections of the README.md and the AI usage notes, then I reviewed and occasionally tweaked the text.
- Test case generation: I described the exact test style and behavior I wanted (e.g. APITestCase + reverse() + testing GET, POST, PUT, DELETE for the Player endpoints), and ChatGPT produced test code that I then used, integrated into the project, and ran as part of the test suite.

The main goal in all of this was to speed up repetitive or boilerplate work, not to outsource the problem solving or domain logic.

## What AI Was Not Used For
- Designing the data model or API structure
- Deciding how tournaments, players, participants, or leaderboard logic should work

## Example Prompt

Here is an example of the kind of prompts I used:

I first want to test the player endpoints.
Create the tests for listing players -> there shouldn't be any in there,
adding a player and then checking if it is also in the list,
updating a player and deleting a player.

Use pytest and Django's APITestCase style with reverse(),
similar to this code example: [paste existing test class from old project].
