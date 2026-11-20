---
name: mock-data
description: Generates fake test data and fixtures, such as names, addresses and orders, as JSON or CSV for unit tests and demos. Use when the user needs mock data, test fixtures or seed data.
license: MIT
---

# Mock data

Generate realistic fake records that contain no real person's data.

## Steps

1. Ask for the record shape, or read it from a schema or a model class.
2. Pick a seed so the same command gives the same data.
3. Generate the records. Use obviously fake names and the reserved `.test` domain for emails.
4. Write JSON or CSV, as the user asks.
5. Print the first three records so the user can check the shape.

## Rules

- Never copy real customer data into fixtures.
- Keep foreign keys consistent across tables.
