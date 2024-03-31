ph_add_command() {
    last_command=$(fc -ln -1)
    last_command=$(printf "%s" "$last_command" | jq -sRr @json)
    gname=${PH_GNAME:-test}
    data="{\"gname\":\"$gname\", \"command\":$last_command}"
    url="https://tanzhasan--example-web-flask-flask-app.modal.run/add_command"
    debug=${PH_DEBUG:-false}
    if [ "$debug" = true ]; then
        (curl -s -X POST -H "Content-Type: application/json" -d "$data" "$url" &)
    else
        (curl -s -X POST -H "Content-Type: application/json" -d "$data" "$url" >/dev/null 2>&1 &)
    fi
}

ph_handle_gname() {
    if [[ $1 == *gname* ]]; then
        gname=$(cat ~/ph_gname.txt)
        export PH_GNAME=$gname
    fi
}

ph_handle_command() {
    last_command=$(fc -ln -1)
    ph_handle_gname "$last_command"
    ph_add_command
}

PROMPT_COMMAND="ph_handle_command${PROMPT_COMMAND:+; $PROMPT_COMMAND}"