#!/bin/sh -e

# Edit the following to change the name of the database user that will be created:
APP_DB_USER=cmsc828d
# APP_DB_PASS=pass

# Edit the following to change the name of the database that is created (defaults to the user name)
APP_DB_NAME=newspapers

# Edit the following to change the version of PostgreSQL that is installed
PG_VERSION=9.6

PORT=15432

###########################################################
# Changes below this line are probably not necessary
###########################################################
print_db_usage () {
  echo "Your PostgreSQL database has been setup and can be accessed on your local machine on the forwarded port (default: $PORT)"
  echo "  Host: localhost"
  echo "  Port: $PORT"
  echo "  Database: $APP_DB_NAME"
  echo "  Username: $APP_DB_USER"
  echo "  Password: $APP_DB_PASS"
  echo ""
  echo "Admin access to postgres user via VM:"
  echo "  vagrant ssh"
  echo "  sudo su - postgres"
  echo ""
  echo "psql access to app database user via VM:"
  echo "  vagrant ssh"
  echo "  sudo su - postgres"
  echo "  PGUSER=$APP_DB_USER psql -h localhost $APP_DB_NAME"
  echo ""
  echo "Env variable for application development:"
  echo "  DATABASE_URL=postgresql://$APP_DB_USER:$APP_DB_PASS@localhost:$PORT/$APP_DB_NAME"
  echo ""
  echo "Local command to access the database via psql:"
  echo "  PGUSER=$APP_DB_USER psql -h localhost -p $PORT $APP_DB_NAME"
}

export DEBIAN_FRONTEND=noninteractive

PROVISIONED_ON=/etc/vm_provision_on_timestamp
if [ -f "$PROVISIONED_ON" ]
then
  echo "VM was already provisioned at: $(cat $PROVISIONED_ON)"
  echo "To run system updates manually login via 'vagrant ssh' and run 'apt-get update && apt-get upgrade'"
  echo ""
  print_db_usage
  exit
fi

PG_REPO_APT_SOURCE=/etc/apt/sources.list.d/pgdg.list
if [ ! -f "$PG_REPO_APT_SOURCE" ]
then
  # Add PG apt repo:
  echo "deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main" > "$PG_REPO_APT_SOURCE"

  # Add PGDG rep key:
  wget --quiet -O - https://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | apt-key add -
fi


# Update package list and upgrade all packages
apt-get -y update
apt-get -y upgrade
apt-get -y install "postgresql-$PG_VERSION" "postgresql-contrib-$PG_VERSION"

PG_CONF="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
PG_DIR="/var/lib/postgresql/$PG_VERSION/main"

# Edit postgresql.conf to change listen address to '*':
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF"

# Append to pg_hba.conf to add password auth:

# Database administrative login by Unix domain socket
echo 'local   all             postgres                                peer' > "$PG_HBA"
echo '# TYPE  DATABASE        USER            ADDRESS                 METHOD' >> "$PG_HBA"
echo '# "local" is for Unix domain socket connections only' >> "$PG_HBA"
echo 'local   all             all                                     peer' >> "$PG_HBA"
echo '# IPv4 local connections:' >> "$PG_HBA"
echo 'host    all             all             all                     trust' >> "$PG_HBA"
echo '# Allow replication connections from localhost, by a user with the' >> "$PG_HBA"
echo '# replication privilege.' >> "$PG_HBA"
echo 'local   replication     all                                     peer' >> "$PG_HBA"

# Explicitly set default client_encoding
echo "client_encoding = utf8" >> "$PG_CONF"

# Restart so that all new config is loaded:
service postgresql restart

# -- Create the database user:
# CREATE USER $APP_DB_USER WITH PASSWORD '$APP_DB_PASS';

# -- Create the database:
# CREATE DATABASE $APP_DB_NAME WITH OWNER=$APP_DB_USER
#                                   LC_COLLATE='en_US.utf8'
#                                   LC_CTYPE='en_US.utf8'
#                                   ENCODING='UTF8'
#                                   TEMPLATE=template;
echo "Making the movies table" 
sudo -u postgres createuser --createdb --superuser $APP_DB_USER
sudo -u postgres createdb $APP_DB_NAME
sudo -u postgres psql -c "grant all privileges on database $APP_DB_NAME to $APP_DB_USER ;"
PGUSER=$APP_DB_USER psql -w -f /mnt/bootstrap/Vagrant-setup/init_articles.sql -h localhost $APP_DB_NAME
PGUSER=$APP_DB_USER psql -w -f /mnt/bootstrap/Vagrant-setup/init_keywords.sql -h localhost $APP_DB_NAME

# Tag the provision time:
date > "$PROVISIONED_ON"

# echo "Initializing the movies tables"
# cat << EOF | PGUSER=${APP_DB_USER} PGPASSWORD=${APP_DB_PASS} psql -f init_movies.psql  ${APP_DB_NAME}
# EOF

print_db_usage
