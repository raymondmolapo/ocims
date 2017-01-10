#!/usr/bin/expect

# set Variables
#description="CKAN" #lrange $argv 0 0]
#name_surname="Raymond_Molapo" #[lrange $argv 1 1]
#email="rmolapo@csir.co.za" #[lrange $argv 2 2]
#keywords="CKAN_docker"
#gitusername="rmolapo"
#set arg1 #[lrange $argv 3 3]

set timeout 1

spawn scp -r raymond@yak.dhcp.meraka.csir.co.za:~/docker-data/ .

#Filter description with (yes/no)
expect "*(yes/no)*" { send "yes\r" }

#Filter description without prompts
expect "*password:*" { send "dnomyar\r" }


interact
