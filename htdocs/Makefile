# Sean's website makefile
#

SERVER=shell1.sourceforge.net
DIR=/home/groups/o/op/openhpi/htdocs

RSYNC = rsync -rlvC --exclude '.emacs*' --rsh=ssh ./ $(SERVER):$(DIR)
CHMOD = ssh $(SERVER) "find $(DIR) -user `whoami` -exec chmod g+w {} \;"
CHMODD = ssh $(SERVER) "find $(DIR) -user `whoami` -type d -exec chmod g+s {} \;"

all:
	$(RSYNC)
	$(CHMOD)
	$(CHMODD)

