"""Entry point for the panos-mcp server."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "panos_mcp.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
