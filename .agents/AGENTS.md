# Cheating Sentiment Project Guidelines

This repository consists of two main parts: a Python backend service and a SvelteKit frontend web application. All data is managed using Firestore, and the web application is hosted on Firebase.

## Python Application (`extraction_service`)
- **Purpose**: Extracts "cheating sentiment" from Steam reviews utilizing a local LLM.
- **Code Standards**: 
  - Must be written using Python best practices.
  - Follow PEP 8 guidelines for formatting and styling.
  - Use Python type hints comprehensively.
  - Keep the code modular, testable, and well-documented.

## Web Application (`frontend`)
- **Framework**: **SvelteKit** (Single Page Application).
- **Svelte Version**: **Svelte 5** is explicitly required. Ensure all components and logic use Svelte 5 specific features (such as runes for reactivity) and avoid deprecated patterns from Svelte 4.
- **Purpose**: A frontend interface to display the cheating sentiment data extracted by the Python service.
- **Integration**: Fetches and displays data directly from Firestore.

## Infrastructure & Database
- **Database**: Firebase Firestore is the primary data store for all sentiment data.
- **Hosting**: The frontend is hosted on Firebase Hosting.
