# IoT

## Quick Start

1. Build the Docker image:
   ```bash
   docker build -t iot .
   ```
2. Run the container:
   ```bash
   docker run -p 8080:8080/tcp iot
   ```
3. The API will be available at `localhost:8080`.

## Local Setup

1. Create a database and a user with appropriate permissions.
2. Edit the necessary details in the `settings.py` file.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the API:
   ```bash
   python main.py
   ```

## Testing

Run the tests using the following command:
```bash
pytest tests.py
```

## API Endpoints

```
GET POST        /api/apiuser
GET PUT DELETE  /api/apiuser/{id}

GET POST        /api/location
GET PUT DELETE  /api/location/{id}

GET POST        /api/device
GET PUT DELETE  /api/device/{id}
```
