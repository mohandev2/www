#!/usr/bin/perl
#
#  Perl program to pull everything out of the trackers and build a artifact
#  text files in the process.  Use other programs in this directory to do 
#  useful things with these pulls
#
#  Note: if SF gave access to their export anonymously, or let agents authenticate
#  with the site, we could do this in 2 requests instead of the couple hundred
#  that is currently required.
#
#  (C) Copyright 2003 IBM Corp.
#
#  Author: Sean Dague
#
#  This file is distributed under that same terms as OpenHPI itself

use LWP::UserAgent;
use HTML::LinkExtor;
use HTTP::Response;
use HTTP::Request::Common;
use Data::Dumper;
#use LWP::Debug qw(level); level('+');
use strict;

our @track = ();

my $ua = new LWP::UserAgent();
$ua->env_proxy(1);

my @bugs = process_tracker(532251);
my @features = process_tracker(532254);

open(OUT,">bugs.txt");
print OUT Dumper(\@bugs);
close(OUT);

open(OUT,">features.txt");
print OUT Dumper(\@features);
close(OUT);

#http://sourceforge.net/tracker/index.php?func=browse&group_id=71730&atid=532251&set=custom&_assigned_to=0&_status=100&_category=100&_group=100&order=artifact_id&sort=ASC&offset=50

#print $res->as_string;

sub callback {
    my($tag, %attr) = @_;
    if($tag eq 'a' and $attr{href} =~ m{/tracker/index.php}) {
        #        print Dumper(\%attr);
        push @track, \%attr;
    }
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
 
    foreach my $i (@links) {
        if($i->{href} =~ /offset/) { next; }

        my %keys = get_artifact($i->{href});
        print "processed $i->{href}\n";
        push @arts, \%keys;
    }
    return @arts;
}

sub get_artifact {
    my $relurl = shift;
    my %keys = ();
    my $res = $ua->request(GET "http://sourceforge.net" . $relurl);
    
    my $content = $res->content;
    foreach my $key ("Category", "Group", "Assigned To", "Priority", "Status", "Resolution", "Date Closed") {
        if($content =~ /($key):.*?<br>([^<]+)/s) {
            $keys{$1} = $2;
        }
    }
    if($content =~ /<title>SourceForge.net: Detail:(\d+) - (.*?)<\/title>/is) {
        $keys{Number} = $1;
        $keys{Title} = $2;
    }
    $keys{Link} = "http://sourceforge.net" . $relurl;
    
    return %keys;
}

sub suck_tracker {
    my ($base, %vars) = @_;

    # this has to be package scoped, other wise callbacks go crazy
    @track = ();
    
    my $p = HTML::LinkExtor->new(\&callback);      
    my $res = $ua->request(POST $base,
                           \%vars);
    
    $p->parse($res->content);
    
    my $item = $track[scalar(@track) - 1];
    my $offset = 0;
    while($item->{href} =~ /offset=(\d+)/) {
        my $newoff = $1;
        if($newoff < $offset) {
            last;
        }
        $offset = $newoff;
        pop(@track);
        $res = $ua->request(GET "http://sourceforge.net" . $item->{href});
        $p->parse($res->content);
        $item = $track[scalar(@track) - 1];
    }
    return @track;
}

    
