zsh_plugin = """
# ===== Termax ZSH Plugin =====
_termax_zsh() {
    if [[ -n "$BUFFER" ]]; then
        local _termax_prev_cmd=$BUFFER
        BUFFER=" ⌛ Processing..."
        zle reset-prompt
        BUFFER=$(t termax -p "$_termax_prev_cmd")
        zle end-of-line
    fi
}
zle -N _termax_zsh
bindkey '^k' _termax_zsh
# ===== Termax ZSH Plugin End =====
"""
