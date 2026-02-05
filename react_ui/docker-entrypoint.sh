#!/bin/sh
set -e

# Substitute environment variables into config.js template
# Uses shell parameter expansion for defaults (${VAR:-default})
envsubst < /usr/share/nginx/html/config.js.template > /usr/share/nginx/html/config.js

# Start nginx
exec nginx -g 'daemon off;'
