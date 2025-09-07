# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python image processing tool that uses Google's Gemini AI API to add photocopy artifacts and aging effects to images. The project is a simple single-file application.

## Dependencies and Environment

- **Python Version**: 3.11 (specified in `.python-version`)
- **Package Manager**: UV (used for dependency management)
- **Key Dependencies**: 
  - `google-genai>=1.33.0` - Google Gemini AI API client
  - `pillow>=11.3.0` - Image processing library

## Environment Setup

1. Install dependencies: `uv sync`
2. Set environment variable: `GEMINI_API_KEY=your_api_key_here`

## Running the Application

```bash
python main.py <input_image_path>
```

The application will generate an output image with "_photocopy_effect" appended to the original filename.

## Code Architecture

This is a single-file application (`main.py`) with the following structure:

- **Configuration**: API key loading and client initialization
- **Core Function**: `add_photocopy_artifacts()` - handles image loading, API communication, and saving
- **Main Entry Point**: Command-line interface for processing images

The application loads an image using PIL, sends it to Gemini's image generation model with a photocopy effect prompt, and saves the processed result.