#!/usr/bin/perl

use strict;
use Data::Dumper;
use POSIX;

our $VAR1;

our $table = "";

my @RELEASES = ("1.9.2","1.9.3","2.0.0","Future","None","1.0.0");

my $data = load_data("tracker.db");

#my @f = load_items("features.txt");
#my @b = load_items("bugs.txt");

my $features = {};
foreach my $i (sort keys %{$data->{features}->{data}}) {
    my $tmp = $data->{features}->{data}->{$i};
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
foreach my $i (sort keys %{$data->{bugs}->{data}}) {
    my $tmp = $data->{bugs}->{data}->{$i};
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
        $table .=  "<h4>Release Status for $rel</h4>\n";
        $table .=  "<div><table>\n";

        print_group("Features",$features->{$rel});
        print_group("Bugs",$bugs->{$rel});

        $table .= "</table></div>\n";
    }
}

################
#
#  Now do file sub work
#
################
{
    local $/ = undef;
    open(IN,"<index.tmpl");
    my $content = <IN>;
    close(IN);

    $content =~ s/%% data %%/$table/igs;

    my $date = ctime(time());

    $content =~ s/%% time %%/$date/igs;

    open(OUT,">index.shtml");
    print OUT $content;
    close(OUT);
}


sub print_group {
    my ($name, $tracker) = @_;
    $table .=  "<tr><th colspan=\"5\">$name</th></tr>\n";
    my $group = "";
    foreach my $id (sort
                    {$tracker->{$a}->{Category}.$a cmp
                       $tracker->{$b}->{Category}.$b} keys %{$tracker}) {

        if($group ne $tracker->{$id}->{Category}) {
            $group = $tracker->{$id}->{Category};
            $table .=  "<tr><td class=\"group\" colspan=\"5\">$group</td></tr>\n";
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

    $table .= "<tr>\n<td class=\"$flag\">$bid</td>\n";
    $table .= "<td class=\"summary\"><a href=\"$url\">$sum</a></td><td class=\"owner\">$owner</td>\n";
    $table .= "<td class=\"status\">$status - $resolve</td></tr>\n";

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
    return $data;
}
