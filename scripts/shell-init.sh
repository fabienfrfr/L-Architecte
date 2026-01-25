#!/usr/bin/env bash

# 1. POSIX-compliant interactive check (Works in sh, bash, zsh)
case $- in
    *i*) ;;
      *) return 0;;
esac

# --- Configuration ---
SESSION_NAME="stack"
THEME_COLOR="\033[38;5;75m"
RESET="\033[0m"
BOLD="\033[1m"

# --- Aliases ---
alias ta="tmux attach -t $SESSION_NAME"
alias tl="tmux ls"
alias k="kubectl"
alias architect-up="devbox run up"

# --- Functions ---
# Note: removed 'function' keyword for POSIX compatibility
_check_and_attach() {
    # Skip if already inside TMUX
    [ -n "$TMUX" ] && return

    # Check if tmux is even installed
    if ! command -v tmux >/dev/null 2>&1; then
        return
    fi

    # Check if the session exists
    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        # Check if anyone is already attached
        if ! tmux list-sessions | grep "^${SESSION_NAME}:" | grep -q "(attached)"; then
            echo -e "${THEME_COLOR}🔗 Auto-attaching to: ${BOLD}$SESSION_NAME${RESET}"
            sleep 0.5
            tmux attach -t "$SESSION_NAME"
        else
            echo -e "${THEME_COLOR}ℹ️  Session ${BOLD}$SESSION_NAME${RESET} is active (already attached)."
            echo -e "   Type ${BOLD}'ta'${RESET} to force attach."
        fi
    fi
}

# --- Welcome Message ---
echo -e "${THEME_COLOR}${BOLD}--- AgenticArchitect Dev Environment ---${RESET}"
echo -e "Commands: ${BOLD}ta${RESET} (attach), ${BOLD}tl${RESET} (list), ${BOLD}k${RESET} (kubectl)"

# Execute
_check_and_attach