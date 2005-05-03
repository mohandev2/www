#!/usr/bin/perl

use strict;
use Data::Dumper;

my $rel = shift;

our $VAR1;

my $data = load_data("tracker.db");
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

print Dumper($features);

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
    print "Changes for $rel\n";
    print "-------------------\n";
    print "New Features:\n";

    print_group($features->{$rel});

    print "\nFixed Bugs:\n";

    print_group($bugs->{$rel});
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
            $group = $tracker->{$id}->{Category};
            print "$group\n";
        }
        
	print "  $bug->{id} - $bug->{Title}\n";
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
