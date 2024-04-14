fish_function = """
# ====== Termax Fish Plugin ======
function termax_fish
    set -l _buffer (commandline)
    if test -n "$_buffer"
        set -l BUFFER "new command here"
        commandline $BUFFER
        commandline -f end-of-line
        set -l BUFFER (t termax -p "$_buffer")
        commandline $BUFFER
        commandline -f end-of-line
    end
end
# ====== Termax Fish Plugin End ======
"""

fish_plugin = """
# ====== Termax Fish Plugin ======
bind \ck 'termax_fish'
# ====== Termax Fish Plugin End ======
"""
