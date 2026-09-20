"""Offline setup: create a private local config without overwriting existing settings."""
from pathlib import Path
import secrets


def initialize(root):
    target = root / '.env'
    if target.exists():
        print('Existing .env preserved. Compare its setting names with .env.example.')
        return False
    content = (root / '.env.example').read_text()
    password = secrets.token_urlsafe(32)
    content = content.replace('replace-with-random-password', password)
    content = content.replace('replace-with-different-random-password', secrets.token_urlsafe(32))
    content = content.replace('replace-with-random-token', secrets.token_urlsafe(32))
    content = content.replace('replace-with-different-random-token', secrets.token_urlsafe(32))
    content = content.replace('RAG_API_URL=\n', 'RAG_API_URL=http://127.0.0.1:8000\n')
    with target.open('x') as f:
        f.write(content)
    target.chmod(0o600)
    print('Created .env with local passwords. Add your three API keys and Pinecone host privately.')
    return True


if __name__ == '__main__':
    initialize(Path(__file__).resolve().parents[1])
