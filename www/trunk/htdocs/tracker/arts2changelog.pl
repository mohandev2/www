#!/usr/bin/perl

use strict;
use Data::Dumper;

my $rel = shift;

our $VAR1;

my @f = load_items("features.txt");
my @b = load_items("bugs.txt");

my $features = {};
foreach my $tmp (@f) {
    $tmp->{Type} = "Feature";
    if($tmp->{Status} =~ /Deleted/) {
        next;
    }
    # probably old
    if($tmp->{Status} =~ /Closed/ and
       $tmp->{Group} =~ /None/) {
        next;
    }
    
    $features->{$tmp->{Group}}->{$tmp->{Number}} = $tmp;
    
}

my $bugs = {};
foreach my $tmp (@b) {
    $tmp->{Type} = "Bug";
    if($tmp->{Status} =~ /Deleted/) {
        next;
    }
    # probably old
    if($tmp->{Status} =~ /Closed/ and
       $tmp->{Group} =~ /None/) {
        next;
    }
    $bugs->{$tmp->{Group}}->{$tmp->{Number}} = $tmp;
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
        
        if($group ne $tracker->{$id}->{Category}) {
            $group = $tracker->{$id}->{Category};
            print "$group\n";
        }
        my $bug = $tracker->{$id};
        print "  $bug->{Number} - $bug->{Title}\n";
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
