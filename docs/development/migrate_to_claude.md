# Migration Guide: OpenAI to Claude

This guide helps you migrate from the OpenAI GPT-4o setup to the new Anthropic Claude-4 Opus configuration.

## Required Changes

### 1. Environment Variables

**Old (OpenAI):**

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
```

**New (Claude):**

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CLAUDE_MODEL=claude-opus-4-20250514
```

### 2. Get Anthropic API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and set it as `ANTHROPIC_API_KEY` in your environment

### 3. Install New Dependencies

The system now uses:

- **Anthropic Claude** for the main LLM (instead of OpenAI GPT)
- **HuggingFace Embeddings** for vector storage (instead of OpenAI embeddings)

Dependencies are automatically installed when you run:

```bash
pip install -r requirements.txt
```

### 4. Key Changes Made

- **LLM Provider**: Switched from OpenAI GPT-4o to Anthropic Claude-4 Opus
- **Agent Type**: Changed from `OPENAI_FUNCTIONS` to `STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION`
- **Embeddings**: Now using local HuggingFace `sentence-transformers/all-MiniLM-L6-v2` model
- **No Vendor Lock-in**: Embeddings run locally, no external API calls needed

### 5. Performance Considerations

- **Claude-4 Opus**: Enhanced reasoning capabilities, better at complex tasks, frontier intelligence
- **Local Embeddings**: No API calls for embeddings = faster response times + cost savings
- **Agent Architecture**: Structured chat format works well with Claude's capabilities

### 6. Re-index Property Data (Optional)

If you want to regenerate the vector store with the new embedding model:

```bash
python index_property.py
```

This will rebuild the vector database using HuggingFace embeddings instead of OpenAI embeddings.

### 7. Test the Migration

1. Set your `ANTHROPIC_API_KEY` environment variable
2. Start the server: `python main.py`
3. Test a simple query to ensure Claude is responding correctly

## Rollback Instructions

If you need to rollback to OpenAI:

1. Switch back to the `main` branch: `git checkout main`
2. Restore your OpenAI environment variables
3. The system will work as before

## Support

If you encounter any issues during migration, please check:

1. API key is correctly set
2. All dependencies are installed
3. Vector store is accessible

The evaluation system and all tools remain compatible with the new Claude setup.
