# add to a bash script 
ph_add_command() {
    # command data
    last_command=$(fc -ln -1) # Get the last executed command as a string``
    last_command=$(printf "%q" $last_command | jq -sR) # Properly escape the entire command string
    gname=${PH_GNAME:-test}
    data="{\"gname\":\"$gname\", \"command\":$last_command}"
    url="https://tanzhasan--example-web-flask-flask-app.modal.run/add_command"

    # # request 
    # # Adding -s to the curl command will suppress the progress meter, while >/dev/null 2>&1 redirects both stdout and stderr to /dev/null, effectively suppressing any output
    debug=${PH_DEBUG:-false}
    if [ debug = true ]; then 
        ( curl -s -X POST -H "Content-Type: application/json" -d "$data" "$url" & ) 
    else 
        ( curl -s -X POST -H "Content-Type: application/json" -d "$data" "$url" & ) >/dev/null 2>&1
    fi
}

