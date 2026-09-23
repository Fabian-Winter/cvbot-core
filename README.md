# cvbot-core

Shared building blocks of the CVBot RAG system, used by cvbot-embedder and
cvbot-retriever.

The package holds everything both services need identically, so ingestion and
retrieval cannot drift apart: the Bedrock embedding factory, the ChromaDB
connection, the `cl100k_base` token counting, the environment parsers and
validators behind each service `Settings`, the log configuration, the
structural interfaces of the backends and the section metadata vocabulary.

`metadata.py` defines how a `> key: value` field is normalized and how the
observed schema is encoded. Both sides must agree on it: cvbot-embedder writes
the schema onto the collection, cvbot-retriever reads it back, injects it into
its prompt and matches the extracted filters against chunk metadata. It also
holds the single period rule (`period_end_year`) that cvbot-embedder derives the
published `years` lists from and cvbot-retriever rates recency against, so the
two sides can never disagree on when a period ends.

## Usage

The package is not published to a package index. Consumers install the release
tarball of an exact tag, so that embedder and retriever always run against the
same revision and no git client is required to resolve the dependency:

```
cvbot-core @ https://github.com/Fabian-Winter/cvbot-core/archive/refs/tags/v0.1.0.tar.gz
```

## Development

To work on a service against an unreleased change, install the checkout in
editable mode instead of the pinned tag:

```bash
pip install -e ../cvbot-core
```

## Releases

`.github/workflows/release.yml` runs the test suite on every push to `main` and,
on a green run, bumps the patch level of the latest `v*` tag and pushes the new
tag. A commit that already carries a tag is skipped, so re-runs never create
duplicates. The `version` field in `pyproject.toml` is a placeholder - the tag is
the source of truth.
