def greet(name: str) -> str:
    """Return a friendly greeting for name."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    # simple CLI entrypoint
    print(greet("World"))
