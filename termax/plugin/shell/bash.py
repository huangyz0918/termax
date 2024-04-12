bash_plugin = """
# ====== Termax Bash Plugin ======
_termax_bash() {
    if [[ -n "$READLINE_LINE" ]]; then
        local _termax_prev_line="$READLINE_LINE"
        READLINE_LINE="⌛ Processing..."
        READLINE_POINT=${#READLINE_LINE}
        # Execute 't' and capture the output directly into READLINE_LINE
        READLINE_LINE=$(t termax -p "$_termax_prev_line")
        READLINE_POINT=${#READLINE_LINE}
    fi
}
bind -x '"\\C-k": _termax_bash'
# ====== Termax Bash Plugin End ======
"""
