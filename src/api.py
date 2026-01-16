from infrastructure.fastapi.main import create_api

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app=create_api(),
        port=8000,
        reload=False,
        loop="uvloop",
    )
