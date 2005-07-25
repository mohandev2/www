#!/usr/bin/perl

use strict;
use Data::Dumper;
use Getopt::Std;

our %opts = ();
our $VAR1;

# options:
#     -w	     produce html output instead of plain text
#     -r release     release for which to produce changelog (required)
#     -h             print this message

getopts('hwr:', \%opts);

if($opts{h}) {
    usage();
}

my $data = load_data("tracker.db");
my $rel = $opts{r};
if(!$rel) {
	usage("Need a release (e.g. ... -r 2.0.0)");
}
# = load_items("features.txt");
#my @b = load_items("bugs.txt");

my $features = {};
foreach my $key (sort keys (%{$data->{features}->{data}})) {
    my $tmp = $data->{features}->{data}->{$key};
    $tmp->{Type} = "Feature";
    if($tmp->{Status} =~ /Deleted/) {
        next;
    }
    # probably old
    if($tmp->{Status} =~ /Closed/ and
       $tmp->{Group} =~ /None/) {
        next;
    }
    
    $features->{$tmp->{Group}}->{$tmp->{id}} = $tmp;
    
}

#print Dumper($features);

my $bugs = {};
foreach my $key (sort keys (%{$data->{bugs}->{data}})) {
    my $tmp = $data->{bugs}->{data}->{$key};
    $tmp->{Type} = "Bug";
    if($tmp->{Status} =~ /Deleted/) {
        next;
    }
    # probably old
    if($tmp->{Status} =~ /Closed/ and
       $tmp->{Group} =~ /None/) {
        next;
    }
    $bugs->{$tmp->{Group}}->{$tmp->{id}} = $tmp;
}

if(exists $bugs->{$rel} or exists $features->{$rel}) {
    if($opts{w}) {
	print "<!--#include virtual=\"changelog_head.shtml\" -->\n";
	print "             <h3>Changelog for $rel</h3>\n";
	print "             <h4>New Features</h4>\n";
	print "             <div>\n";
    } else {
    	print "Changelog for $rel\n";
    	print "-------------------\n";
    	print "New Features:\n";
    }

    print_group($features->{$rel});

    if($opts{w}) {
	print "              </div>\n";
	print "              <h4>Fixed Bugs</h4>\n";
	print "              <div>\n";
    } else {
	print "\nFixed Bugs:\n";
    }

    print_group($bugs->{$rel});

    if($opts{w}) {	
	print "              </div>\n";
	print "<!--#include virtual=\"changelog_bottom.html\" -->\n";
    }
}

sub usage {
    my $msg = shift;
    print "ERROR: $msg\n" if($msg);
    print <<END;
arts2changelog.pl - generate changelog from tracker
  -w      	  : produce html output instead of plain text
  -r release	  : specifies release for which to produce changelog (required)
  -h      	  : print this message
END
    exit(1);
}

sub print_group {
    my ($tracker) = @_;
    my $group = "";
    foreach my $id (sort 
                    {$tracker->{$a}->{Category}.$a cmp
                       $tracker->{$b}->{Category}.$b} keys %{$tracker}) {
        
        my $bug = $tracker->{$id};
	if ($bug->{Status} ne "Closed") {
		next;
	}
	
	if($group ne $tracker->{$id}->{Category}) {
	    if($group && $opts{w}) {
		print "                  </ul>\n";
	    }
            $group = $tracker->{$id}->{Category};
            if($opts{w}) {
		print "                  <b>$group:</b>\n";
	        print "                  <ul>\n";
	    } else {
	        print "$group\n";
	    }
        }
        
	if($opts{w}) {
	    print "                      <li><a href=\"$bug->{Link}\">$bug->{id}</a> - $bug->{Title}\</li>\n";
	} else {
	    print "  $bug->{id} - $bug->{Title}\n";
	}
    }
    
    if($group && $opts{w}) {
        print "                  </ul>\n";
    }
}

sub load_items {
    $VAR1 = undef;
    my $file = shift;
    local $/ = undef;
    open(IN,"<$file");
    my $var = <IN>;
    close(IN);
    
    eval($var);

    my @value = @$VAR1;
    
    return @value;
}

#########################################
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
#    print Dumper($data);
    return $data;
}
