#!/usr/bin/perl
#
# program to generate text for the status of the next release.

use strict;
use Data::Dumper;

my $rel = shift;
if(!$rel) {
    die "please specify release number";
}

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
    print "Release Status for $rel\n";
    print "----------------------------\n";
    print "Features:\n";
    foreach my $bid (sort keys %{$features->{$rel}}) {
        my $bug = $features->{$rel}->{$bid};
        print_item($bug);
    }
    
    print "\nBugs:\n";
    foreach my $bid (sort keys %{$bugs->{$rel}}) {
        my $bug = $bugs->{$rel}->{$bid};
        print_item($bug);
    }
}

sub print_item {
    my $art = shift;
    my $bid = $art->{Number};
    my $status = $art->{Status};
    my $flag = $status;
    my $owner = $art->{"Assigned To"};
    my $cat = $art->{Category};
    my $resolve = $art->{Resolution};
    my $sum = $art->{Title};

    if($owner =~ /Nobody/ and $status !~ /Closed/) {
        $flag = "Bad";
    }
    
    my $url = "https://sourceforge.net/tracker/index.php?func=detail&amp;aid=$bid&amp;group_id=71730";
    if($art->{Type} =~ /Feature/) {
        $url .= "&amp;atid=532254";
    } elsif($art->{Type} =~ /Bug/) {
        $url .= "&amp;atid=532251";
    }
    
    print "  $bid - $sum\n";
    print "      $owner : $status - $resolve\n"
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
