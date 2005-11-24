#!/usr/bin/perl
#
#  Perl program to pull everything out of the trackers and build a artifact
#  text files in the process.  Use other programs in this directory to do 
#  useful things with these pulls
#
#  Note: if SF gave access to their export anonymously, or let agents authenticate
#  with the site, we could do this in 2 requests instead of the couple thousand
#  that is currently required.
#
#  (C) Copyright 2003-2005 IBM Corp.
#
#  Author: Sean Dague
#  Modifications: Renier Morales
#
#  This file is distributed under that same terms as OpenHPI itself

use LWP::UserAgent;
use HTML::LinkExtor;
use HTTP::Response;
use HTTP::Request::Common;
use Data::Dumper;
use Time::Local;
use Getopt::Std;
use strict;
use constant OPENHPI => 71730;

our @track = ();
our @items = ();
our %opts = ();

# options -
#    -a        : get all (means you must use the SF tracker)
#    -m mbox   : get a delta from an mbox (you must have a tracker mbox)
#    -s single : get a single artifact
#    -h        : usage

getopts('ahm:t:s:', \%opts);

if($opts{'h'}) { 
    usage(); 
}

#unless($opts{'a'} or $opts{'m'} or $opts{'s'}) {
    #print Dumper(\%opts);
    #usage("must specify either -a or -m mbox");
#}

if($opts{'a'} and $opts{'m'}) {
    usage("must specify *only* one of -a and -m");
}

# now we get down to work

my $ua = new LWP::UserAgent();
$ua->env_proxy(0);

# Database of past bugs / features looks as follows:
#my $data = {
#            features => {
#                         trackerid => "", # tracker id for this
#                         newest => "", # time of newest feature
#                         data => {}, # hash (by id) of features
#                        },
#            bugs => {
#                     trackerid => "", # tracker id for this
#                     newest => "", # time of newest feature
#                     data => {}, # hash (by id) of features
#                    },
#           };

my $data = load_data("tracker.db");

set_newest($data);

## Add trackers here
$data->{'bugs'}->{'trackerid'} ||= 532251;
$data->{'features'}->{'trackerid'} ||= 532254;    

# if we want a full pull
if($opts{'a'}) {
    pull_all($data);
}
if($opts{'m'}) {
    pull_from_mbox($data, $opts{'m'}, $opts{'t'});
}
if($opts{'s'}) {
    pull_single($data, $opts{'s'});
}

unless($opts{'a'} or $opts{'m'} or $opts{'s'}) {
    pull_new($data);
}


# always set the newest globally before saving
set_newest($data);

save_data("tracker.db",$data);

######################################################
#
# usage
#
######################################################

sub usage {
    my $msg = shift;
    print "ERROR: $msg\n" if($msg);
    print <<END;
sfexport.pl - export sourceforge tracker data. pulls newest artifacts by default.
  -a      : pull ALL data from SF trackers (this will take a while)
  -m mbox : use an mbox file to pull recent changes
  -h      : display help
END
    exit(1);
}

######################################################
#
# pull_all($data) - pull everything from the trackers
#
######################################################

sub pull_all {
    my $data = shift;
    $data->{'bugs'}->{'data'} = pull_entire_tracker($data->{'bugs'}->{'trackerid'});
    $data->{'features'}->{'data'} = pull_entire_tracker($data->{'features'}->{'trackerid'});
}

sub pull_new {
    my $data = shift;
    $data->{'bugs'}->{'data'} = pull_new_in_tracker($data->{'bugs'}->{'trackerid'});
    $data->{'bugs'}->{'data'} = pull_new_in_tracker($data-{'newest'},
    						    $data->{'bugs'}->{'trackerid'});
}
######################################################
#
# pull_from_mbox($data) - pull from an mbox file
#
######################################################
sub pull_single {
    my ($data, $item) = @_;

    foreach my $t (keys %$data) {
        my %ids = ();
        my @ids = ($item);
        
        # make them unique
        foreach my $i (@ids) { $ids{$i}++; }

        foreach my $i (sort keys %ids) {
            print "Getting data for TID: $data->{$t}->{trackerid}, ID: $i\n";
            my %data = get_artifact(OPENHPI,
                                    $data->{$t}->{'trackerid'},
                                    $i);
            if(!$data{'Number'}) {
                next;
            }
            print Dumper(\%data);
            $data->{$t}->{'data'}->{$i} = \%data;
            delay("in pull_single");
        }
    }
}

######################################################
#
# pull_from_mbox($data) - pull from an mbox file
#
######################################################

sub pull_from_mbox {
    my ($data, $mbox, $backlog) = @_;
    
    $backlog ||= 40; # number of days of backlog

    foreach my $t (keys %$data) {
        my %ids = ();
        my @ids = find_mbox_items_newer($mbox, $backlog, $data->{$t}->{'newest'}, $data->{$t}->{'trackerid'});
        
        # make them unique
        foreach my $i (@ids) { $ids{$i}++; }

        foreach my $i (sort keys %ids) {
            print "Getting data for TID: $data->{$t}->{trackerid}, ID: $i\n";
            my %data = get_artifact(OPENHPI,
                                    $data->{$t}->{'trackerid'},
                                    $i);
            $data->{$t}->{'data'}->{$i} = \%data;
            delay("in pull_from_mbox");
        }
    }
}

##############################################
#
# find_mbox_items_newer - find tracker urls from an mbox
#                         for messages no older than 1 week before the
#                         last update on the tracker.
#
##############################################

sub find_mbox_items_newer {
    use Mail::Box::Manager;
    my @ids = ();
    
    my ($file, $backdays, $newest, $trackerid) = @_;

    my $time = $newest - $backdays*24*60*60; # back a week
    
    my $mgr = new Mail::Box::Manager;
    my $folder = $mgr->open($file);
    
    foreach my $msg ($folder->messages) {
        if($msg->timestamp < $time) {next;}
        
        print "Message Subject: " . $msg->subject . "\n";
        if($msg->body =~ m{(sourceforge.net/tracker/\S+)}) {
            my $url = $1;
            print "Found URL: $url\n";
            if($url =~ /atid=$trackerid/g) {
                my ($project, $tracker, $id) = parse_url($url);
                push @ids, $id;
            } else {
                print "URL didn't match $trackerid\n";
            }
        } else {
            print "No url found\n";
        }
    }
    return @ids;
}
#################

sub load_data {
    my $data = {};
    my $file = shift;
    my $VAR1 = undef;
    my $tmp;
    
    return $data if(!-e $file);
    
    open(IN,"<$file") or die "Can't open $file";
    {
        local $/ = undef;
        $tmp = <IN>;
    }
    close(IN);
    eval $tmp;
    $data = $VAR1;
    return $data;
}

sub save_data {
    my ($file, $data) = @_;
    open(OUT,">$file") or die "Can't save $file";
    print OUT Dumper($data);
    close(OUT);
}

sub pull_entire_tracker {
    my $tid = shift;
    my %arts = ();
    my @links = suck_tracker("http://sourceforge.net/tracker/index.php",
                             group_id => OPENHPI,
                             atid => $tid,
                             _status => 100,
                             set => "custom",
                          );
    print "Resting 2 seconds to keep SF off our back\n";
    sleep 2;
			  
    foreach my $i (@links) {
        if($i->{'href'} =~ /offset/) { next; }

        my ($project, $tracker, $id) = parse_url($i->{'href'});
        print "Getting data for TID: $tracker, ID: $id\n";        
        my %data = get_artifact($project, $tracker, $id);
        $arts{$id} = \%data;

        delay("in pull_entire_tracker");
    }
    return \%arts;
}

sub pull_new_in_tracker {
    my $newest = shift;
    my $tid = shift;
    my %arts = ();
    my @links = suck_new_in_tracker($newest,
    				    "http://sourceforge.net/tracker/index.php",
                                    group_id => OPENHPI,
				    atid => $tid,
				    _status => 100,
				    set => "custom");
    print "Resting 2 seconds to keep SF off our back\n";
    sleep 2;

    foreach my $i (@links) {
        if($i->{'href'} =~ /offset/) { next; }

        my ($project, $tracker, $id) = parse_url($i->{'href'});
        print "Getting data for TID: $tracker, ID: $id\n";
        my %data = get_artifact($project, $tracker, $id);
        $arts{$id} = \%data;

        delay("in pull_entire_tracker");
    }
    return \%arts;
}

sub process_tracker {
    my $tid = shift;
    my @arts = ();
    my @links = suck_tracker("http://sourceforge.net/tracker/index.php",
                             group_id => 71730,
                             atid => $tid,
                             _status => 100,
                             set => "custom",
                          );

    delay("on process_tracker 1");
			  
    foreach my $i (@links) {
        if($i->{'href'} =~ /offset/) { next; }

        my %keys = get_artifact($i->{'href'});
        print "processed $i->{href}\n";
        push @arts, \%keys;

        delay("on process_tracker");
    }
    return @arts;
}

sub get_artifact {
    my ($project, $tracker, $id) = @_;
    my %keys = (
                project => $project,
                tracker => $tracker,
                id => $id
               );
    
    my $url = gen_url($project, $tracker, $id);

    my $res = $ua->request(GET $url);
    
    my $content = $res->content;

    foreach my $key ("Category", "Group", "Assigned To", "Priority", "Status", "Resolution") {    
        if($content =~ />($key): .*?br>(.*?)<\/td/s) {    	
	    $keys{$key} = $2;
	    $keys{$key} =~ s/[\x0a\x09]//g;
        }
    }
    foreach my $key ("Date","Closed as of","Date Submitted","Date Last Updated") {
        if($content =~ /($key):.*?(\d.*?)$/sm) {
	    $keys{$key} = $2;
	    $keys{$key} =~ s/[\x0a\x09]//g;
        }
    }
    $keys{"Closed"} = $keys{"Closed as of"};

    if($keys{"Date Last Updated"} =~ /update/) {
       $keys{"Date Last Updated"} = $keys{"Date Submitted"}; 
    }
    
    $keys{'mtime'} = convert_time($keys{"Date Submitted"});

    if($content =~ m{<h2>\s*\[\s*(\d+)\s*\]\s*(.*?)\s*</h2>}is) {
        $keys{'Number'} = $1;
        $keys{'Title'} = $2;
    }

    $keys{'Link'} = gen_url($project, $tracker, $id);

#    print STDERR Dumper(\%keys); # Debug
    
    return %keys;
}

sub callback {
    my($tag, %attr) = @_;
    
    if($tag eq 'a' and $attr{'href'} =~ m{aid=|offset=}) {
#        print "$attr{href}\n"; # Debug
        push @track, \%attr;
    }
}

#######################################################
#
#  suck_tracker - pull all the artifacts for a given tracker
#
#######################################################

sub suck_tracker {
    my ($base, %vars) = @_;

    # this has to be package scoped, other wise callbacks go crazy
    @track = ();
    
    my $p = HTML::LinkExtor->new(\&callback);      
    my $res = $ua->request(POST $base,
                           \%vars);
    #print $res->content;
    
    $p->parse($res->content);
    
    my $item = $track[scalar(@track) - 1];
    my $offset = 0;
    while($item->{'href'} =~ /offset=(\d+)/) {
        my $newoff = $1;
        if($newoff < $offset) {
            last;
        }
        $offset = $newoff;
        pop(@track);
        $res = $ua->request(GET "http://sourceforge.net" . $item->{'href'});
        $p->parse($res->content);
        $item = $track[scalar(@track) - 1];
        
        delay("on tracker suck");
	#print $res->content;
    }
    return @track;
}

sub suck_new_in_tracker {
    my ($newest, $base, %vars) = @_;
    
    my $res = $ua->request(POST $base,
                           \%vars);
    
    @items = ();
    
    parse_newest($newest, $res->content, \@items);
    
    my $item = $items[scalar(@items) - 1];
    my $offset = 0;
    
    while($item->{'href'} =~ /offset=(\d+)/) {
        my $newoff = $1;
        if($newoff < $offset) {
            last;
        }
        $offset = $newoff;
        pop(@items);
        $res = $ua->request(GET "http://sourceforge.net" . $item->{'href'});
        parse_newest($res->content, \@items);
        $item = $items[scalar(@items) - 1];
        
        delay("on tracker suck");
	#print $res->content;
    }
    
    return @items;
}

sub parse_newest {
    my ($newest, $content, @items) = @_;
    
    use HTML::TokeParser;

    my $p = HTML::TokeParser->new(\$content);

    while (my $token = $p->get_tag('a')) {
    	my $url = $token->[1]{'href'};
	my %item = {};
    	if ($url =~ /aid=/) {
            if ($token = $p->get_tag('td')) {
                my $open_date = $p->get_trimmed_text('/td');
                $open_date =~ s/[\xa0\x09 ]//g;
                if (convert_time($open_date) > $newest) {		    
		    $item{'href'} = $url;
		    push(@items, \%item);
		}
            }
        } elsif ($url =~ /offset=/) {
	    $item{'href'} = $url;
	    push(@items, \%item);
        }
    }
}

##################################################
#
#  set_newest($data) - sets the newest field of the trackers
#                      in the data.
#
##################################################

sub set_newest {
    my $data = shift;
    foreach my $t (keys %$data) {
        foreach my $art (sort keys %{$data->{$t}->{'data'}}) {
            if($data->{$t}->{'data'}->{$art}->{'mtime'} > $data->{$t}->{'newest'}) {
                $data->{$t}->{'newest'} = $data->{$t}->{'data'}->{$art}->{'mtime'};
            }
        }
    }
}

##################################################
#
#  convert_time($sftime) - convert from SF Text Time to Epoch Time
#
##################################################

sub convert_time {
    my $sftime = shift;
    my $time = 0;
    if($sftime =~ /^(\d\d\d\d)-(\d\d)-(\d\d) (\d+):(\d\d)/) {
        my ($y, $m, $d, $H, $M) = ($1, $2, $3, $4, $5);
        $time = timegm(0,$M, $H, $d, ($m - 1), ($y - 1900));
    }
    return $time;
}

sub parse_url {
    my $url = shift;
    my ($project, $tracker, $id);
    if($url =~ /aid=(\d+)/) {
        $id = $1;
    }
    if($url =~ /group_id=(\d+)/) {
        $project = $1;
    }
    if($url =~ /atid=(\d+)/) {
        $tracker = $1;
    }
    return ($project, $tracker, $id);
}

sub gen_url {
    my ($project, $tracker, $id) = @_;
    my $url = "http://sourceforge.net/tracker/?func=detail&aid=$id&group_id=$project&atid=$tracker";
    return $url;
}    

sub delay {
    my $msg = shift;
    print "Resting 2 secs to keep SF off our back";
    print ": $msg" if $msg;
    print "\n";
    sleep 2;
}

