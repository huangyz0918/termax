bash_plugin = """
# ====== Termax Bash Plugin ======
_termax_bash() {
    if [[ -n "$READLINE_LINE" ]]; then
        set +m
        local _termax_prev_line="$READLINE_LINE"
        { spin 5 & } 2>/dev/null
        SPIN_PID=$!

        READLINE_LINE=$(t termax -p "$_termax_prev_line")
        kill "$SPIN_PID"
        printf "\r%s" "                 "
        echo " "
        READLINE_POINT=${#READLINE_LINE}
    fi
}
spin() {
    local -a marks=('⠋ Generating.' '⠙ Generating..' '⠹ Generating...' '⠸ Generating.' '⠼ Generating..' '⠴ Generating...' '⠦ Generating.' '⠧ Generating..' '⠇ Generating...' '⠏ Generating...')
    local i=0

    while true; do
        printf "\r%s" "${marks[i++ % ${#marks[@]}]}"
        sleep 0.3
    done
}
bind -x '"\\C-k": _termax_bash'
# ====== Termax Bash Plugin End ======
"""
