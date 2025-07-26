# IROA Deployment Scripts

This directory contains comprehensive deployment scripts to build, start, stop, and manage the IROA system.

## 🚀 Quick Start

For first-time setup, use the quick start script:

```bash
./quick-start.sh
```

This will:
1. Make all scripts executable
2. Build Docker containers
3. Start the entire system

## 📋 Available Scripts

### `start.sh` - Main Startup Script
Starts the IROA system with Docker containers and frontend.

```bash
./start.sh           # Start with existing containers
./start.sh --build   # Build containers and start
./start.sh -b        # Same as --build
./start.sh --help    # Show help
```

**What it does:**
- ✅ Checks Docker status
- 🏗️ Builds containers (if --build flag)
- 🚀 Starts API container (port 8001)
- 📈 Starts Prometheus (port 9090, if available)
- 🌐 Starts frontend server (port 3000)
- ⏳ Waits for services to be ready
- 📊 Shows access URLs

### `stop.sh` - System Shutdown Script
Stops all IROA services cleanly.

```bash
./stop.sh           # Normal stop
./stop.sh --clean   # Stop and remove containers/logs
./stop.sh -c        # Same as --clean
./stop.sh --force   # Force stop all processes on IROA ports
./stop.sh -f        # Same as --force
./stop.sh --help    # Show help
```

**What it does:**
- 🛑 Stops frontend server
- 🐳 Stops Docker containers
- 🧹 Cleans up processes (if --force)
- 🗑️ Removes containers/logs (if --clean)

### `build.sh` - Docker Build Script
Builds all Docker containers for the IROA system.

```bash
./build.sh          # Build containers
./build.sh --clean  # Clean old images and build
./build.sh -c       # Same as --clean
./build.sh --help   # Show help
```

**What it does:**
- 🧹 Cleans old images (if --clean)
- 🏗️ Creates Dockerfiles if missing
- 📦 Builds IROA API container
- 📈 Builds Prometheus container
- 📋 Shows build summary

### `status.sh` - System Status Check
Checks the status of all IROA services.

```bash
./status.sh
```

**What it shows:**
- 🐳 Docker container status
- 🌐 Frontend server status
- 🔗 Service connectivity
- 🌍 Access URLs
- 📝 Log file locations

### `quick-start.sh` - One-Command Setup
Complete setup for new deployments.

```bash
./quick-start.sh
```

**What it does:**
- 🔧 Makes all scripts executable
- 🏗️ Builds containers (clean build)
- 🚀 Starts the entire system

## 🌍 Access URLs

Once started, access the system at:

- **📊 IROA Dashboard:** http://localhost:3000
- **🔧 API Documentation:** http://localhost:8001/docs
- **📈 Prometheus:** http://localhost:9090

## 📁 Directory Structure

```
IROA_Full_System_With_ML_And_Wizard/
├── start.sh              # Main startup script
├── stop.sh               # System shutdown script
├── build.sh              # Docker build script
├── status.sh             # Status check script
├── quick-start.sh        # One-command setup
├── DEPLOYMENT.md         # This file
├── logs/                 # Log files
│   └── frontend.log      # Frontend server logs
├── config/               # Configuration files
│   └── integrations.json # Saved integrations
├── data/                 # Application data
└── frontend.pid          # Frontend process ID
```

## 🔧 Prerequisites

- **Docker Desktop** - Must be running
- **Node.js** (optional) - For frontend server
- **Python 3** (fallback) - If Node.js unavailable
- **curl** - For health checks

## 📝 Logging

- **Frontend logs:** `logs/frontend.log`
- **API logs:** `docker logs iroa-api`
- **Prometheus logs:** `docker logs iroa-prometheus`

## 🐛 Troubleshooting

### Docker Issues
```bash
# Check Docker status
docker info

# Restart Docker Desktop if needed
```

### Port Conflicts
```bash
# Check what's using ports
lsof -i :3000
lsof -i :8001
lsof -i :9090

# Force stop with --force flag
./stop.sh --force
```

### Permission Issues
```bash
# Make scripts executable
chmod +x *.sh
```

### Container Issues
```bash
# Clean rebuild
./stop.sh --clean
./build.sh --clean
./start.sh --build
```

## 🔄 Common Workflows

### Daily Development
```bash
./start.sh          # Start with existing containers
./status.sh         # Check status
./stop.sh           # Stop when done
```

### After Code Changes
```bash
./stop.sh           # Stop system
./build.sh          # Rebuild containers
./start.sh          # Start with new containers
```

### Clean Deployment
```bash
./stop.sh --clean   # Stop and clean everything
./build.sh --clean  # Clean build
./start.sh --build  # Start fresh
```

### Emergency Reset
```bash
./stop.sh --force   # Force stop everything
./quick-start.sh    # Complete fresh start
```

## 🎯 Tips

1. **Use `status.sh` frequently** to monitor system health
2. **Check logs** if services don't start properly
3. **Use `--clean` flags** for fresh deployments
4. **Keep Docker Desktop running** before starting
5. **Use `quick-start.sh`** for new environments

## 🆘 Support

If you encounter issues:

1. Check `./status.sh` for service status
2. Review logs in `logs/` directory
3. Try `./stop.sh --force && ./quick-start.sh`
4. Ensure Docker Desktop is running
5. Check port availability with `lsof -i :PORT`
