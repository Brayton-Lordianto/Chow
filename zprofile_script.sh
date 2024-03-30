# add to zprofile
[ -f ~/ph_commands.sh ] && source ~/ph_commands.sh

precmd() { eval "$PROMPT_COMMAND" }
PROMPT_COMMAND='ph_add_command'
