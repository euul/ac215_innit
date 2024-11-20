# Api-service

This module handles the communication between the frontend and backend, managing API requests and responses for the application.

## Build Container

To build the container, run:

```bash
sh docker-shell.sh
```

This dockerfile exposes the port 8000 for communication and it starts the FastAPI app using uvicorn. It also initiates the docker network so that the frontend can communicate with the backend.

## Next steps

Now head on over to the frontend folder and follow the instructions there.
