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
    foreach my $bid (sort keys %{$features->{$rel}}) {
        my $bug = $features->{$rel}->{$bid};
        print "  $bug->{Number} - $bug->{Title}\n";
    }
    print "\nFixed Bugs:\n";
    foreach my $bid (sort keys %{$bugs->{$rel}}) {
        my $bug = $bugs->{$rel}->{$bid};
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
