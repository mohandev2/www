#!/usr/bin/perl

use strict;
use Data::Dumper;

our $VAR1;

my @RELEASES = ("0.7","0.9","1.0.0","1.9.0","1.9.1","Future","None");

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

foreach my $rel (@RELEASES) {
    if(exists $bugs->{$rel} or exists $features->{$rel}) { 
        print "<h2>Release Status for $rel</h2>\n";
        print "<table>\n";
        
        print_group("Features",$features->{$rel});
        print_group("Bugs",$bugs->{$rel});

        print "</table>\n";
    }
}

sub print_group {
    my ($name, $tracker) = @_;
    print "<tr><th colspan=5>$name</th></tr>\n";
    my $group = "";
    foreach my $id (sort 
                    {$tracker->{$a}->{Category}.$a cmp
                       $tracker->{$b}->{Category}.$b} keys %{$tracker}) {
        
        if($group ne $tracker->{$id}->{Category}) {
            $group = $tracker->{$id}->{Category};
            print "<tr><td class='group' colspan=5>$group</td></tr>\n";
        }
        my $bug = $tracker->{$id};
        print_item_html($bug);
    }
}

sub print_item_html {
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
    
    print "<tr>\n<td class=$flag>$bid</td>\n";
    print "<td class=sumary><a href=\"$url\">$sum</a></td><td class=owner>$owner</td>\n";
    print "<td class=status>$status - $resolve</td></tr>\n";
    
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
