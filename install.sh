#!/bin/bash
# Kore Utility Suite — Linux Setup Script
# Detects distribution and ensures system-level python3 & tkinter dependencies
# are installed before starting the visual onboarding & installation setup.

set -e

# Color tokens for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0;37m' # No Color

echo -e "${PURPLE}==============================================${NC}"
echo -e "${CYAN}      Kore Utility Suite — Setup Launcher      ${NC}"
echo -e "${PURPLE}==============================================${NC}"

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 is not installed on this system.${NC}"
    echo -e "Please install Python 3.11+ using your package manager and try again."
    exit 1
fi

# Detect Linux Distribution
DISTRO="unknown"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    DISTRO_LIKE=$ID_LIKE
fi

echo -e "${BLUE}[INFO] Detected OS: ${DISTRO} (like: ${DISTRO_LIKE})${NC}"

# Function to check and install tkinter & venv
ensure_dependencies() {
    HAS_TKINTER=true
    python3 -c "import tkinter" &> /dev/null || HAS_TKINTER=false

    HAS_VENV=true
    python3 -c "import venv" &> /dev/null || HAS_VENV=false

    if [ "$HAS_TKINTER" = true ] && [ "$HAS_VENV" = true ]; then
        echo -e "${GREEN}[SUCCESS] Tkinter and Venv system modules are present.${NC}"
        return 0
    fi

    echo -e "${YELLOW}[WARNING] Missing system python requirements. Root authorization needed to install.${NC}"
    
    # Install dependencies based on distribution
    if [[ "$DISTRO" == "ubuntu" || "$DISTRO" == "debian" || "$DISTRO_LIKE" == *"ubuntu"* || "$DISTRO_LIKE" == *"debian"* ]]; then
        echo -e "${BLUE}[INFO] System uses apt. Launching installation...${NC}"
        sudo apt-get update
        sudo apt-get install -y python3-tk python3-venv python3-pip
    elif [[ "$DISTRO" == "fedora" || "$DISTRO_LIKE" == *"fedora"* || "$DISTRO" == "rhel" || "$DISTRO" == "centos" ]]; then
        echo -e "${BLUE}[INFO] System uses dnf. Launching installation...${NC}"
        sudo dnf install -y python3-tkinter python3-pip
    elif [[ "$DISTRO" == "arch" || "$DISTRO" == "cachyos" || "$DISTRO_LIKE" == *"arch"* ]]; then
        echo -e "${BLUE}[INFO] System uses pacman. Launching installation...${NC}"
        sudo pacman -Sy --noconfirm tk python-pip
    elif [[ "$DISTRO" == "opensuse" || "$DISTRO_LIKE" == *"suse"* ]]; then
        echo -e "${BLUE}[INFO] System uses zypper. Launching installation...${NC}"
        sudo zypper install -y python3-tk python3-pip
    else
        echo -e "${RED}[ERROR] Unsupported distribution: ${DISTRO}.${NC}"
        echo -e "Please manually install the python tkinter and venv modules using your system's package manager."
        exit 1
    fi
}

ensure_dependencies

# Launch the visual setup script
echo -e "${GREEN}[SUCCESS] Starting visual setup tool...${NC}"
python3 setup_gui.py
