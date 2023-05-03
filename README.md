# StreamerAI

StreamerAI is a Python-based application that allows users to engage with an AI-powered streaming assistant. The application can fetch product scripts, answer comments, and handle text-to-speech (TTS) functionalities. It utilizes SQLite for database management, GPT-based models for answering questions, and TTS services for speech synthesis.

## Overview

The main components of the StreamerAI application include:

- `StreamerAI` class: Represents the main functionality of the streamer AI, handling script fetching, comment answering, and TTS management.
- `StreamCommentsDB` class: A database utility class for managing stream comments using SQLite.
- `TextToSpeech` class: A TTS service wrapper that handles speech synthesis for the AI-generated responses.
- `Chains` class: A GPT-based question-answering module that creates context-aware AI responses.
- `Retrieval` class: A GPT-based question-answering module that retrieves relevant information based on user queries.

## Setup

1. Set OpenAI API Key environment variable via `export OPENAI_API_KEY=<key here>`
2. Set Pinecone API Key environment variable via `export PINECONE_API_KEY=<key here>`
3. Install poetry if you have not yet via `pip install poetry`
4. `poetry env use python3.10`
5. `poetry shell` to activate virtual environment
6. `poetry install` to install dependencies

## Streamer Usage

1. `poetry shell` if you haven't yet
2. `source .env` if you haven't yet
3. Start main script `poetry run start --room_id '<room id here>'`
4. Use the fake streamchat script to insert comments `poetry run fake --room_id '33'`
