fish_function = """
# ====== Termax Fish Plugin ======
function termax_fish
    set -l _buffer (commandline)
    if test -n "$_buffer"
        t termax -p "$_buffer" > /tmp/termax_output.txt &
        set -l job_id $last_pid
        while kill -0 $job_id 2>/dev/null
            commandline -a "."
            sleep 1
        end
        set -l BUFFER (cat /tmp/termax_output.txt)
        rm /tmp/termax_output.txt
        commandline $BUFFER
        # commandline -f end-of-line
    end
end
# ====== Termax Fish Plugin End ======
"""

fish_plugin = """
# ====== Termax Fish Plugin ======
bind \ck 'termax_fish'
# ====== Termax Fish Plugin End ======
"""
