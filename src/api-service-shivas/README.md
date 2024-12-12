# Api-service-shivas

This module handles the communication between the frontend and backend, managing API requests and responses for the application. It is built upon the template code provided by Shivas (hence the name).

## Build Container

Important note! Due to the CI testing, the last line in the Dockerfile was commented out. If you want to run this locally, make sure to uncomment the last line:

```bash
ENTRYPOINT ["/bin/bash", "./docker-entrypoint.sh"]
```

To build the container, run:

```bash
sh docker-shell.sh
```

This runs the docker entrypoint file that exposes the port 9000 for communication and provides commands to run a FastAPI application using Uvicorn. Run the Uvicorn server with the following command:

```bash
uvicorn_server
```

## Next steps

Now head on over to the frontend-shivas folder and follow the instructions there in order to view the full website.
