#!/usr/bin/perl

use Data::Dumper;
use strict;

my $SDIR = "raw";
my %status = ();
my @files = ();

# aquire files
opendir(DIR,$SDIR);
while(my $f = readdir(DIR)) {
    if($f !~ /^\./) {
        push @files, $f;
    }
}
closedir(DIR);

# read each file

foreach my $file (@files) {
    open(IN,"$SDIR/$file");
    my $name = <IN>;
    chomp($name);
    while(<IN>) {
        if(/^(saHpi\w+)\s+(\w+)\s+(.*)/) {
            $status{$name}->{$1}->{state} = $2;
            $status{$name}->{$1}->{notes} = $3;
        }
    }
    close(IN);
}

foreach my $name (sort keys %status) {
    my $safename = safename($name) . ".html";
    print_individual($safename, $name, $status{$name});
}

print_composite("rollup.html","OpenHPI Composite Status",\%status);

sub print_composite {
    my ($file, $name, $status) = @_;
    open(OUT,">$file");
    
    print OUT "<h2>$name</h2>\n<table>\n";
    
    # print header
    print OUT "<tr><th>HPI&nbsp;Function</th>";
    foreach my $work ((open_hpi_items())) {
        #$work =~ s/ /&nbsp;/;
        print OUT "<th>$work</th>";
    }
    print OUT "</tr>\n";
    
    # print each status
    foreach my $func ((hpi_func_array())) {
        print OUT "<tr><td>$func</td>";
        foreach my $work ((open_hpi_items())) {
            my $state = $status->{$work}->{$func}->{state} || "nodata";
            print OUT "<td class=\"$state\">$state</td>";
        }
        print OUT "</tr>\n";
    }
    print OUT "</table>\n";
}

sub print_individual {
    my ($sn, $name, $status) = @_;
    open(OUT,">$sn");
    print OUT <<END;
<h2>$name</h2>
<table>
<tr><th>HPI Function</th><th>Notes</th></tr>
END
    
    foreach my $func ((hpi_func_array())) {
        my $state = $$status{$func}{state} || "nodata";
        print OUT "<tr><td class=\"$state\">$func</td><td>$$status{$func}{notes}</td></tr>\n";
    }
    print OUT "</table>\n";
    close(OUT);

}

sub safename {
    my $name = shift;
    $name =~ s/\W+//g;
    return $name;
}

sub open_hpi_items {
    my @array = ("OpenHPI Infrastructure","Dummy Plugin","IPMI Plugin","Sysfs Plugin","Text Remote Plugin","Linux Watchdog Plugin");
    return @array;
}

sub hpi_func_array {
    my @array = qw(
                   saHpiInitialize
                   saHpiFinalize 
                   saHpiSessionOpen 
                   saHpiSessionClose 
                   saHpiResourcesDiscover 
                   saHpiRptInfoGet 
                   saHpiRptEntryGet 
                   saHpiRptEntryGetByResourceId 
                   saHpiResourceSeveritySet 
                   saHpiResourceTagSet 
                   saHpiResourceIdGet 
                   saHpiEntitySchemaGet 
                   saHpiEventLogInfoGet 
                   saHpiEventLogEntryGet 
                   saHpiEventLogEntryAdd 
                   saHpiEventLogEntryDelete 
                   saHpiEventLogClear 
                   saHpiEventLogTimeGet 
                   saHpiEventLogTimeSet 
                   saHpiEventLogStateGet 
                   saHpiEventLogStateSet 
                   saHpiSubscribe 
                   saHpiUnsubscribe 
                   saHpiEventGet 
                   saHpiRdrGet 
                   saHpiSensorReadingGet 
                   saHpiSensorReadingConvert 
                   saHpiSensorThresholdsGet 
                   saHpiSensorThresholdsSet 
                   saHpiSensorTypeGet 
                   saHpiSensorEventEnablesGet 
                   saHpiSensorEventEnablesSet 
                   saHpiControlTypeGet 
                   saHpiControlStateGet 
                   saHpiControlStateSet 
                   saHpiEntityInventoryDataRead 
                   saHpiEntityInventoryDataWrite 
                   saHpiWatchdogTimerGet 
                   saHpiWatchdogTimerSet 
                   saHpiWatchdogTimerReset 
                   saHpiHotSwapControlRequest 
                   saHpiResourceActiveSet 
                   saHpiResourceInactiveSet 
                   saHpiAutoInsertTimeoutGet
                   saHpiAutoInsertTimeoutSet
                   saHpiAutoExtractTimeoutGet
                   saHpiAutoExtractTimeoutSet
                   saHpiHotSwapStateGet 
                   saHpiHotSwapActionRequest 
                   saHpiResourcePowerStateGet 
                   saHpiResourcePowerStateSet 
                   saHpiHotSwapIndicatorStateGet 
                   saHpiHotSwapIndicatorStateSet 
                   saHpiParmControl 
                   saHpiResourceResetStateGet 
                   saHpiResourceResetStateSet);
    return @array;
}
