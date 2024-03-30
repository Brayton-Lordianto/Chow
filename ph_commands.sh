# add to a bash script 
ph_add_command() {
    # command data
    last_command=$(fc -ln -1) # Get the last executed command as a string
    gname=$PH_GNAME
    data="{\"gname\":\"$gname\", \"command\":\"$last_command\"}"
    url="https://tanzhasan--example-web-flask-flask-app.modal.run/add_command"

    # request 
    curl -X POST -H "Content-Type: application/json" -d "$data" "$url"
}
