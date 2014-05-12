#!/bin/bash
# This script will setup MariaDB, create the beaker DB
# and populate it's tables
# Create an admin user for Beaker

set -e

# root
if (( EUID != 0 )); then
   echo "You must be root to do this." 1>&2
   exit 100
fi

#Let's apply some useful settings to the MariaDB server.
cp /etc/my.cnf /etc/my.cnf-orig
cat /etc/my.cnf-orig | awk '
        {print $0};
        /\[mysqld\]/ {
            print "character-set-server=utf8";
        }' > /etc/my.cnf

systemctl start mariadb
systemctl enable mariadb

# setup Beaker DB
echo "CREATE DATABASE beaker;" | mysql
echo "GRANT ALL ON beaker.* TO 'beaker'@'localhost' IDENTIFIED BY 'beaker';" | mysql

# initialize Beaker DB tables
echo -n "Please enter a login name for the Beaker admin account: "
read admin
echo -n "Please enter an email address for $admin: "
read email
password="dummy"
stty -echo
trap "stty echo; exit" INT TERM EXIT
while [ "$password" != "$password_again" ]; do
    echo -n "Please enter a passowrd for $admin: "
    read password
    echo
    echo -n "Please enter the password again: "
    read password_again
    echo
    if [ "$password" != "$password_again" ]; then
        echo "Passwords don't match, try again"
        echo
    fi
done
stty echo
trap - INT TERM EXIT
su -s /bin/sh apache -c "beaker-init -u \"$admin\" -p \"$password\" -e \"$email\""
