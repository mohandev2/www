#!/usr/bin/perl

use Data::Dumper;
use strict;

my $SDIR = "raw";
my %status = ();
my @files = ();
my $default_status = "broken";

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
    $name =~ s/\s+$//;
    while(<IN>) {
        if(/^(saHpi\w+)\s+(\w+)\s+(.*)/) {
            $status{$name}->{$1}->{state} = $2;
            $status{$name}->{$1}->{notes} = $3;
        }
    }
    close(IN);
}

foreach my $name (sort keys %status) {
    my $safename = safename($name) . ".shtml";
    print_individual($safename, $name, $status{$name});
}

print_composite("rollup.html","OpenHPI Composite Status",\%status);

sub print_composite {
    my ($file, $name, $status) = @_;
    my %infra_funcs = hpi_infra_calls();
    open(OUT,">$file");
    
    print OUT "<h2>$name</h2>\n<table>\n";
    
    # print header
    print OUT "<tr><th>HPI&nbsp;Function</th>";
    foreach my $work ((open_hpi_items())) {
        #$work =~ s/ /&nbsp;/;
        my $url = safename($work) . ".shtml";
        print OUT "<th><a href=\"$url\">$work</a></th>";
    }
    print OUT "</tr>\n";
    
    # print each status
    foreach my $func ((hpi_func_array())) {
        print OUT "<tr><td>$func</td>";
        foreach my $work ((open_hpi_items())) {
            my $state = $default_status;
            if($work !~ /Infrastructure/ and (exists $infra_funcs{$func})) {
                $state = "na";
            } else {
                $state = $status->{$work}->{$func}->{state} || $default_status;
            }
            print OUT "<td class=\"$state\">$state</td>";
        }
        print OUT "</tr>\n";
    }
    print OUT "</table>\n";
}

sub print_individual {
    my ($sn, $name, $status) = @_;
    open(OUT,">$sn");
    my $h = head_html();
    my $t = foot_html();
    print OUT <<END;
$h
<h1>$name Details</h1>
<p><a href="/status/">Return to Status Overview</a></p>
<table>
<tr><th>HPI Function</th><th>Notes</th></tr>
END
    
    foreach my $func ((hpi_func_array())) {
        my $state = $$status{$func}{state} || $default_status;
        print OUT "<tr><td class=\"$state\">$func</td><td>$$status{$func}{notes}</td></tr>\n";
    }
    print OUT "</table>\n$t";
    close(OUT);

}

sub safename {
    my $name = shift;
    $name =~ s/\W+//g;
    return $name;
}

sub open_hpi_items {
    my @array = ("OpenHPI Infrastructure","Dummy Plugin","IPMI Plugin","Sysfs Plugin","Snmp Client plugin","SNMP Blade Center","SNMP RSA", "Linux Watchdog Plugin");
    return @array;
}

sub hpi_infra_calls {
    my @array = qw(
                   saHpiVersionGet
                   saHpiRptEntryGetByResourceId
                   saHpiResourceIdGet
                   saHpiEventLogStateGet
                   saHpiSubscribe
                   saHpiUnsubscribe
                   saHpiSensorReadingConvert
                   saHpiSensorTypeGet
                   saHpiControlTypeGet
                  );
    my %hash = map {$_ => 1} @array;
    return %hash;
}

sub hpi_func_array {
    my @array = qw(
                   saHpiVersionGet
                   saHpiSessionOpen
                   saHpiSessionClose
                   saHpiDiscover
                   saHpiDomainInfoGet
                   saHpiDrtEntryGet
                   saHpiDomainTagSet
                   saHpiRptEntryGet
                   saHpiRptEntryGetByResourceId
                   saHpiResourceSeveritySet
                   saHpiResourceTagSet
                   saHpiResourceIdGet
                   saHpiEventLogInfoGet
                   saHpiEventLogEntryGet
                   saHpiEventLogEntryAdd
                   saHpiEventLogClear
                   saHpiEventLogTimeGet
                   saHpiEventLogTimeSet
                   saHpiEventLogStateGet
                   saHpiEventLogStateSet
                   saHpiEventLogOverflowReset
                   saHpiSubscribe
                   saHpiUnsubscribe
                   saHpiEventGet
                   saHpiEventAdd
                   saHpiAlarmGetNext
                   saHpiAlarmGet
                   saHpiAlarmAcknowledge
                   saHpiAlarmAdd
                   saHpiAlarmDelete
                   saHpiRdrGet
                   saHpiRdrGetByInstrumentId
                   saHpiSensorReadingGet
                   saHpiSensorThresholdsGet
                   saHpiSensorThresholdsSet
                   saHpiSensorTypeGet
                   saHpiSensorEnableGet
                   saHpiSensorEnableSet
                   saHpiSensorEventEnableGet
                   saHpiSensorEventEnableSet
                   saHpiSensorEventMasksGet
                   saHpiSensorEventMasksSet
                   saHpiControlTypeGet
                   saHpiControlGet
                   saHpiControlSet
                   saHpiIdrInfoGet
                   saHpiIdrAreaHeaderGet
                   saHpiIdrAreaAdd
                   saHpiIdrAreaDelete
                   saHpiIdrFieldGet
                   saHpiIdrFieldAdd
                   saHpiIdrFieldSet
                   saHpiIdrFieldDelete
                   saHpiWatchdogTimerGet
                   saHpiWatchdogTimerSet
                   saHpiWatchdogTimerReset
                   saHpiAnnunciatorGetNext
                   saHpiAnnunciatorGet
                   saHpiAnnunciatorAcknowledge
                   saHpiAnnunciatorAdd
                   saHpiAnnunciatorDelete
                   saHpiAnnunciatorModeGet
                   saHpiAnnunciatorModeSet
                   saHpiHotSwapPolicyCancel
                   saHpiResourceActiveSet
                   saHpiResourceInactiveSet
                   saHpiAutoInsertTimeoutGet
                   saHpiAutoInsertTimeoutSet
                   saHpiAutoExtractTimeoutGet
                   saHpiAutoExtractTimeoutSet
                   saHpiHotSwapStateGet
                   saHpiHotSwapActionRequest
                   saHpiHotSwapIndicatorStateGet
                   saHpiHotSwapIndicatorStateSet
                   saHpiParmControl
                   saHpiResourceResetStateGet
                   saHpiResourceResetStateSet
                   saHpiResourcePowerStateGet
                   saHpiResourcePowerStateSet);
    return @array;
}

sub head_html {
    return <<'HEAD';
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head>
    <title>OpenHPI - Status</title>
    <!--#include virtual="/openhpi.css" -->
  </head>

  <body>
    <table>
        <tr>
          <!--#include virtual="/sidebar.html" -->
          <td valign="top">
HEAD
}

sub foot_html {
    return <<'FOOT';
            <hr>
            <address><a href="http://dague.net/sean">Sean Dague</a></address>
          </td></tr>
    </table>
  </body>
</html>
FOOT
}
