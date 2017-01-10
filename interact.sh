#!/usr/bin/expect

# set Variables
#description="CKAN" #lrange $argv 0 0]
#name_surname="Raymond_Molapo" #[lrange $argv 1 1]
#email="rmolapo@csir.co.za" #[lrange $argv 2 2]
#keywords="CKAN_docker"
#gitusername="rmolapo"
#set arg1 #[lrange $argv 3 3]

#set timeout 5

spawn paster --plugin=ckan create -t ckanext ckanext-tester_theme

#Filter description 
expect "*description*" { send "try\r" }
#Send description
#send -- "$description\r"
#send "try\r"

#Match author string
expect "*Threepwood*" { send "Raymond Molapo\r"}
#Send author
#send --"$name_surname\r"

#Match email string
expect "*_email*" { send "rmolapo@csir.co.za\r"}
#Send email
#send --"$email\r"
#send -- "try\r"


#Match keywords string
expect "*keywords*" { send "CKAN docker\r" }
#Send author
#send --"$keywords\r"
#send -- "try\r"


#Match gitusername string
expect "*github_user_name*" { send "rmolapo\r" }
#Send author
#send --"$gitusername\r"
#send -- "try\r"


#send -- "\r"

#expect eof

interact
