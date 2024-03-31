# Runs every command sent to the shell
ph_handle_command() { 
    last_command=$(fc -ln -1) # Get the last executed command as a string
    ph_handle_gname "$last_command" # Check if the last command contains gname. If it does, run the command within an eval
    ph_add_command "$last_command" # Send the last command to the server
}

ph_add_command() {
    # Command data
    last_command=$(printf "%s" "$1" | jq -sRr @json) # Properly escape the entire command string
    gname=${PH_GNAME:-test}
    data="{\"gname\":\"$gname\", \"command\":$last_command}"
    url="https://tanzhasan--example-web-flask-flask-app.modal.run/add_command"
    echo $lastcomm

    # Request 
    # Adding -s to the curl command will suppress the progress meter, while >/dev/null 2>&1 redirects both stdout and stderr to /dev/null, effectively suppressing any output
    debug=${PH_DEBUG:-false}
    if [ "$debug" = true ]; then 
        ( curl -s -X POST -H "Content-Type: application/json" -d "$data" "$url" & ) 
    else 
        ( curl -s -X POST -H "Content-Type: application/json" -d "$data" "$url" & ) >/dev/null 2>&1
    fi
}

# Check if the last command contains gname. If it does, export $PH_GNAME
ph_handle_gname() {
    if [[ $1 == *gname* ]]; then
        # get gname from ph_gname.txt 
        gname=$(cat ~/ph_gname.txt)
        export PH_GNAME=$gname
    fi
}