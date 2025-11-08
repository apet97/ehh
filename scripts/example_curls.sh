#!/usr/bin/env bash
curl -s localhost:8000/healthz

curl -s localhost:8000/actions/parse -H 'content-type: application/json' -d \
'{"text":"slack.post_message channel=#general text=hello"}' | jq

curl -s 'localhost:8000/actions/parse?llm=true' -H 'content-type: application/json' -d \
'{"text":"Post hello to #general on Slack"}' | jq
