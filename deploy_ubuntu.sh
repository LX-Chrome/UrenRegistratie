#!/bin/bash
#
# Wrapper script for Ubuntu deployment
# Redirects to scripts/deploy_ubuntu.sh
#

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Make the deployment script executable if it's not already
chmod +x "${SCRIPT_DIR}/scripts/deploy_ubuntu.sh"

# Run the actual deployment script with all arguments
"${SCRIPT_DIR}/scripts/deploy_ubuntu.sh" "$@" 