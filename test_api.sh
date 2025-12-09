#!/bin/bash

set -e

BASE="http://localhost:8000/api"

print() {
  echo -e "\n====== $1 ======\n"
}

# Pretty-print JSON if jq is available, otherwise raw
pretty() {
  if command -v jq >/dev/null 2>&1; then
    echo "$1" | jq .
  else
    echo "$1"
  fi
}

print "Creating Players"
ALICE_JSON=$(curl -s -X POST "$BASE/players/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}')
pretty "$ALICE_JSON"

BOB_JSON=$(curl -s -X POST "$BASE/players/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Bob"}')
pretty "$BOB_JSON"

CHARLIE_JSON=$(curl -s -X POST "$BASE/players/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Charlie"}')
pretty "$CHARLIE_JSON"

# Extract player IDs
ALICE_ID=$(echo "$ALICE_JSON" | jq -r '.id')
BOB_ID=$(echo "$BOB_JSON" | jq -r '.id')
CHARLIE_ID=$(echo "$CHARLIE_JSON" | jq -r '.id')

print "Creating Tournament"
TOURNAMENT_JSON=$(curl -s -X POST "$BASE/tournaments/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Shell Script Cup"}')
pretty "$TOURNAMENT_JSON"
TOURNAMENT_ID=$(echo "$TOURNAMENT_JSON" | jq -r '.id')

print "Adding Participants"
# Add Alice
PART_A_JSON=$(curl -s -X POST "$BASE/tournaments/$TOURNAMENT_ID/participants/" \
  -H "Content-Type: application/json" \
  -d "{\"player_id\": $ALICE_ID}")
pretty "$PART_A_JSON"
PART_A_ID=$(echo "$PART_A_JSON" | jq -r '.id')

# Add Bob
PART_B_JSON=$(curl -s -X POST "$BASE/tournaments/$TOURNAMENT_ID/participants/" \
  -H "Content-Type: application/json" \
  -d "{\"player_id\": $BOB_ID}")
pretty "$PART_B_JSON"
PART_B_ID=$(echo "$PART_B_JSON" | jq -r '.id')

# Add Charlie
PART_C_JSON=$(curl -s -X POST "$BASE/tournaments/$TOURNAMENT_ID/participants/" \
  -H "Content-Type: application/json" \
  -d "{\"player_id\": $CHARLIE_ID}")
pretty "$PART_C_JSON"
PART_C_ID=$(echo "$PART_C_JSON" | jq -r '.id')

print "Status (expected: in_planning) - includes leaderboard"
STATUS1_JSON=$(curl -s "$BASE/tournaments/$TOURNAMENT_ID/status/")
pretty "$STATUS1_JSON"

print "Adding Game Results"
# Game 1: Alice (home) beats Bob (away) -> winner = ALICE_ID
GAME1_JSON=$(curl -s -X POST "$BASE/tournaments/$TOURNAMENT_ID/games/" \
  -H "Content-Type: application/json" \
  -d "{
    \"home_participant\": $PART_A_ID,
    \"away_participant\": $PART_B_ID,
    \"winner\": $ALICE_ID
  }")
pretty "$GAME1_JSON"

# Game 2: Bob vs Charlie -> draw -> winner = null
GAME2_JSON=$(curl -s -X POST "$BASE/tournaments/$TOURNAMENT_ID/games/" \
  -H "Content-Type: application/json" \
  -d "{
    \"home_participant\": $PART_B_ID,
    \"away_participant\": $PART_C_ID,
    \"winner\": null
  }")
pretty "$GAME2_JSON"

print "Status (expected: started) - includes leaderboard"
STATUS2_JSON=$(curl -s "$BASE/tournaments/$TOURNAMENT_ID/status/")
pretty "$STATUS2_JSON"

echo -e "\n=== Script completed ===\n"