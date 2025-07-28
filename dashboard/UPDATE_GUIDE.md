# IROA Dashboard Update Guide

## 🚨 Issue: Updates Not Showing After Git Pull

When you `git pull` new changes, the dashboard on port 3000 may not show updates immediately due to browser caching and CSS compilation issues.

## ✅ Solution: Use the Update Script

After each `git pull`, run the update script:

```bash
./update-and-restart.sh
```

**OR** manually run these commands:

```bash
# 1. Rebuild CSS (important!)
npm run build-css

# 2. Restart the server
pkill -f "node server.js"
node server.js &
```

## 🔧 What Was Fixed

1. **Added cache-busting headers** to server.js
2. **Created update script** that rebuilds CSS and restarts server
3. **Added npm scripts** for easier maintenance

## 📋 Quick Reference

| Command | Description |
|---------|-------------|
| `npm run dev` | Development server (Vite) - always shows latest changes |
| `npm run start` | Production server (port 3000) - use after git pull |
| `npm run build-css` | Rebuild Tailwind CSS styles |
| `./update-and-restart.sh` | One-command update after git pull |

## 🌐 Development vs Production

- **Development** (`npm run dev`): Auto-reloads, shows changes immediately
- **Production** (`npm run start` or `node server.js`): Needs manual updates after changes

## 💡 Browser Cache Issues

If you still see old content after updating:
- **Chrome/Edge**: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- **Firefox**: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
- **Safari**: Cmd+Option+R

## 🔄 Recommended Workflow

1. `git pull` to get latest changes
2. `./update-and-restart.sh` to apply changes
3. Hard refresh browser if needed
4. Dashboard should show all new features and updates!