zsh_plugin = """
# ===== Termax ZSH Plugin =====
_termax_zsh() {
    if [[ -n "$BUFFER" ]]; then
        local _termax_prev_cmd=$BUFFER
        local pid spinner i tmpfile
        BUFFER=""
        zle reset-prompt

        # Create a temporary file for output
        tmpfile=$(mktemp)

        # Start termax in the background and redirect its output to the temporary file
        set +m
        t termax -p "$_termax_prev_cmd" > "$tmpfile" &
        pid=$!

        # Spinner
        spinner=('⠋ Generating.' '⠙ Generating..' '⠹ Generating...' '⠸ Generating.' '⠼ Generating..' '⠴ Generating...' '⠦ Generating.' '⠧ Generating..' '⠇ Generating...' '⠏ Generating...')
        i=0
        # Display spinner until the process has finished
        while kill -0 $pid 2>/dev/null; do
            BUFFER="${spinner[i++ % ${#spinner[@]}]}"
            zle reset-prompt
            zle end-of-line
            sleep 0.3
        done

        # Wait for the background process to finish
        wait $pid

        # Read the result from the temporary file and clean up
        BUFFER=$(<"$tmpfile")
        rm "$tmpfile"

        zle end-of-line
    fi
}
zle -N _termax_zsh
bindkey '^k' _termax_zsh
# ===== Termax ZSH Plugin End =====
"""
