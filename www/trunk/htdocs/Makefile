# Sean's website makefile
#

SERVER=shell1.sourceforge.net
DIR=/home/groups/o/op/openhpi/htdocs

RSYNC = rsync -rplvC --exclude '.emacs*' --rsh=ssh ./ $(SERVER):$(DIR)
CHMOD = ssh $(SERVER) find $(DIR) -user `whoami` -exec chmod g+w {}\;

all:
	$(RSYNC)
	-$(CHMOD)

