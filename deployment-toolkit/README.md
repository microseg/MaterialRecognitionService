# Deployment Toolkit

This toolkit provides a standardized way to deploy Python applications to AWS EC2 instances using AWS CodeBuild and CodePipeline.

## What's Included

- `buildspec.yml` - AWS CodeBuild configuration
- `deploy.sh` - Deployment script for EC2 instances
- `README.md` - This documentation

## How to Use

### 1. Copy to Your Project

Copy the entire `deployment-toolkit` folder to your project root:

```bash
cp -r deployment-toolkit/ your-project/
```

### 2. Configure Your Project

Your project should have:
- A Python application (Flask, FastAPI, etc.)
- `requirements.txt` (optional, will auto-detect)
- Main entry point (`app.py`, `main.py`, etc.)

### 3. Environment Variables (Optional)

You can customize deployment by setting these environment variables in your CodeBuild project:

- `SERVICE_NAME` - Systemd service name (default: `matsight-backend`)
- `APP_DIR` - Subdirectory containing your app (default: `.`)
- `REQUIREMENTS_FILE` - Python requirements file (default: `requirements.txt`)
- `PORT` - Application port (default: `8000`)
- `HEALTH_PATH` - Health check endpoint (default: `/health`)
- `INSTALL_SYSTEM_PACKAGES` - Install system packages (default: `true`)
- `START_CMD` - Custom start command (default: auto-detected)

### 4. Auto-Detection

The deployment script automatically detects:
- **Gunicorn**: If `gunicorn` is in `requirements.txt`
- **Uvicorn**: If `uvicorn` is in `requirements.txt`
- **Flask/Django**: If `app.py` exists
- **Generic Python**: If `main.py` exists
- **Fallback**: Creates a minimal Flask app if nothing is detected

### 5. AWS Infrastructure Requirements

Your AWS account needs:
- Production EC2 instance with tag `Name=RecogBackendStack/RecogProdHost`
- EC2 instance with SSM agent installed
- IAM role with SSM permissions
- CodeBuild project configured to use this `buildspec.yml`

## Example Project Structure

```
your-project/
├── deployment-toolkit/
│   ├── buildspec.yml
│   ├── deploy.sh
│   └── README.md
├── app.py
├── requirements.txt
└── README.md
```

## Supported Application Types

- **Flask**: `app.py` with `app = Flask(__name__)`
- **FastAPI**: `app.py` with `app = FastAPI()`
- **Django**: `manage.py` in project root
- **Generic Python**: Any Python application with `main.py` or `app.py`

## Troubleshooting

### Common Issues

1. **Instance not found**: Ensure your production EC2 has the correct tag
2. **Permission denied**: Check IAM roles and SSM agent
3. **Port already in use**: Change `PORT` environment variable
4. **Dependencies not found**: Ensure `requirements.txt` exists and is valid

### Logs

- CodeBuild logs: Available in AWS Console
- Application logs: `sudo journalctl -u your-service-name`
- Deployment logs: Check `/opt/matsight/backup/` for previous deployments

## Customization

### Custom Start Commands

Set `START_CMD` environment variable for custom startup:

```bash
START_CMD="gunicorn -w 4 -b 0.0.0.0:8000 app:app"
```

### Custom Health Checks

Set `HEALTH_PATH` for custom health check endpoints:

```bash
HEALTH_PATH="/api/health"
```

### Multiple Applications

For projects with multiple applications, use `APP_DIR`:

```bash
APP_DIR="backend"  # Deploy from backend/ subdirectory
```
