#! /usr/bin/perl

##################################################################
# This program was sloppily thrown together by
# Andrea Brugger 4/8/03. Edit as you like according to the terms below.
#
# You may easily change the Title and data file name by changin
# the user configurable variables declared at the start of the code.
# For colors, etc, you'll have to edit the mess further down.
#
# The data file consists of a month, day, year and then 
# HTML which represents the event, all separated by a ":" and ending
# with a ":" and a newline '\n'. 
# Take care, as any typos in the HTML will mess up the 
# webpage output. Be sure to only list one date and append all events
# to that same line in the text file. A newline indicates the end of 
# the data for that date.
#
# Example:
# 4:14:2003:<dl><B>Ferrit Association Meeting</B><BR><dd>To be held at Marriot Hotel, visit <a href="www.someurl.com">www.someurl.com</a></dd></dl>:
#
##################################################################
# Copyright (c) 2003, Intel Corporation
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
# Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in
# the documentation and/or other materials provided with the distribution.
#
# Neither the name of Intel Corporation nor the names
# of its contributors may be used to endorse or promote products
# derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##################################################################

use CGI;
$query = new CGI;

##################################################################
# These are the user configurable parameters
##################################################################
$CAL_TITLE = "OpenHPI Calendar of Events";
$DATA_FILE_NAME = "events.cal";


##################################################################
# Global variables
##################################################################

@MONTHS = ('x', 'January','February', 'March', 'April', 'May', 'June', 'July', '
August', 'September', 'October', 'November', 'December');
($MONTHS_ABRV{'Jan'}, $MONTHS_ABRV{'Feb'}, $MONTHS_ABRV{'Mar'}) = (1,2,3);
($MONTHS_ABRV{'Apr'}, $MONTHS_ABRV{'May'}, $MONTHS_ABRV{'Jun'}) = (4,5,6);
($MONTHS_ABRV{'Jul'}, $MONTHS_ABRV{'Aug'}, $MONTHS_ABRV{'Sep'}) = (7,8,9);
($MONTHS_ABRV{'Oct'}, $MONTHS_ABRV{'Nov'}, $MONTHS_ABRV{'Dec'}) = (10,11,12);


##################################################################
# extract data from text file
##################################################################
sub parse_data
{
  ($a_month, $a_year) = @_;

  while ($line = <DATA>)
  {
     chop($line);
     ($month, $day, $year, $value) = split(/:/, $line);

     # only store this months events
     if ($month == $a_month && $year == $a_year)
     {
        $data{$day} = $value;
     }
  }
}

##################################################################
# If a day is specified, then it will attempt to display 
# events for that day.
# Otherwise, the event panel (to right of calendar)
# will display "Select a day to display events"
##################################################################
sub display_calendar
{

   ($a_month, $a_day, $a_year) = @_;

   get_data($a_month, $a_year);

   print "<table border=2 cellspacing=2 cellpadding=4 bgcolor=\"#333333\" bordercolor=\"#000066\">";

   print "<tr><td bgcolor=\"#003399\" height=1%><font face=\"Arial, Helvetica, sans-serif\" size=\"5\" color=\"#FFFFFF\">";

   print "</font><b><font size=\"5\" face=\"Arial, Helvetica, sans-serif\" color=\"#FFFFFF\">";
   print $CAL_TITLE;

   print "</font></b></td></tr><tr>\n";
   print " <td bgcolor=\"#DDDDDD\" valign=top> ";
   print "         <table border=0 cellspacing=0 cellpadding=4 width=100%>";
   print "            <tr><td width=25% valign=top>";
   print "        <table border=1 cellspacing=0 cellpadding=5 bgcolor=\"#FFFFFF\">";
   print "<tr align=center>\n";
   print "  <td colspan=7>\n";
   print "  <table border=0 cellspacing=0 cellpadding=0 width=100%><tr>\n";
   print "<td align=center><font size=2 face=\"arial\"><B>$title</B></font></td></tr></table></td></tr>\n";
   print "<tr align=right>\n";
   print "<td><font size=1 face=\"arial\"><B>Sun</b></font></td>\n";
   print "<td><font size=1 face=\"arial\"><B>Mon</b></font></td>\n";
   print "<td><font size=1 face=\"arial\"><B>Tue</b></font></td>\n";
   print "<td><font size=1 face=\"arial\"><B>Wed</b></font></td>\n";
   print "<td><font size=1 face=\"arial\"><B>Thu</b></font></td>\n";
   print "<td><font size=1 face=\"arial\"><B>Fri</b></font></td>\n";
   print "<td><font size=1 face=\"arial\"><B>Sat</b></font></td>\n";
   print "</tr>\n";

  show_days($a_month, $a_day, $a_year);

  print "</table></td><td valign=top rowspan=2>\n";
  print " <table width=100% border=1 cellspacing=0 cellpadding=1>\n";
  print "<tr><td bgcolor=\"#330066\"> <font size=2 face=\"arial\" color=\"#FFFFFF\">\n";

  show_events($a_month, $a_day, $a_year);

}

##################################################
# If day is equal to 0, then the event panel
# (to right of calendar) will show no date or 
# events.
##################################################
sub show_events
{
   ($a_month, $a_day, $a_year) = @_;

   if ($a_day eq 0)
   {
      print "&nbsp</font></td></tr><tr>\n";
   }
   else
   {
     print "<b>$MONTHS[$a_month] $a_day, $a_year";
     print "</b></font> </td></tr><tr>\n";
   }

   print "<td valign=top height=255 bgcolor=\"#FFFFFF\">\n";
   print "   <table border=0 cellspacing=0 cellpadding=5>\n";
   print " <tr><td><font size=2 face=\"arial\">\n";

   if ($a_day eq 0)
   {
      print "<i>Select a day to display events here</i>\n";
   }

   if ($data{$a_day} =~ /\S+/)
   {
      print "$data{$a_day}\n";
   }

   print "                            </font> </td>\n ";
   print "                      </tr>\n";
   print " </table></td></tr></table></td></tr>\n";
   print "<tr> <td valign=bottom>\n";
   print "<table width=100% border=1 cellspacing=0 cellpadding=3 bgcolor=\"#FFFFFF\">\n";
   print " <tr><td> <font face=\"arial\" size=1>&nbsp;SELECT MONTH AND YEAR: </font><br>\n";
   print "<center> \n";
   print "  <select name=\"month\">\n";
   print "    <option value=1  selected>January\n ";
   print "    <option value=2  >February\n";
   print "    <option value=3  >March\n";
   print "    <option value=4  >April\n";
   print "    <option value=5  >May\n";
   print "    <option value=6  >June\n";
   print "     <option value=7 >July\n";
   print "    <option value=8  >August\n";
   print "    <option value=9  >September\n";
   print "    <option value=10 >October \n";
   print "    <option value=11 >November\n";
   print "    <option value=12 >December \n";
   print "  </select>\n";
   print "  <select name=\"year\" >\n";
   print "    <option value=2003 selected>2003 \n ";
   print "   <option value=2004 >2004\n";
   print "    <option value=2005 >2005\n ";
   print "  </select>\n";
   print"  <input type=submit value=\"Go\">\n";
   print "  <br>\n";
   print "</center></td></tr></table></td></tr>\n";
   print "</table></td></tr></table>\n";
}

##################################################################
# Shows the days of the week, making links for days which contain
# events
##################################################################
sub show_days
{
   ($a_month, $a_day, $a_year) = @_;

$heading = <INPUT>;
chop($heading);

while ($line = <INPUT>)
{
   print "<TR>\n";

  if ($line =~ /(.{3})(.{3})(.{3})(.{3})(.{3})(.{3})(.{2})$/)
   {
      $number[0] = $1;
      $number[1] = $2;
      $number[2] = $3;
      $number[3] = $4;
      $number[4] = $5;
      $number[5] = $6;
      $number[6] = $7;
   }
   #elsif ($line =~ /^(\d\d)(.+\d\d)*$/)
   else
   # elsif ($line =~ /^(\d\d)(\s\d\d)(\s\d\d)(\s\d\d)$/)
   {

      (@number)=split(/\s/,$line);
  }

   foreach $num (@number)
   {
      if ($num =~ /\s*(\d+)\s*/)
      {
         $num = $1;
      }
      # make the new row definition
      print "<td ";

      # provide a background color, if it is today's date or has an event
      if ($data{$num} =~ /\S+/)
      {
         print " bgcolor=\"#9999FF\">";
      }
     # elsif ($num == $today_day)
     # {
     #    print " bgcolor=\"#7777DD\">";
     # }
 else
      {
         print ">"; # not a special day, so close the tag
      }

      # if it is an event today, display it after the number
      if ($data{$num} =~ /\S+/)
      {
         print "<a href=\"/cgi-bin/calendar.cgi?event=1&day=$num&month=$a_month&year=$a_year\">";
         print "<font size=2 face=\"arial\"><B>$num</B></font></a></td>\n";
      }
      else
      {
         print "<font size=2 face=\"arial\"><B>$num</B></font></td>\n";
      }

   }
   print "</TR>\n";
}

}
##################################################################
#
##################################################################
sub get_data
{
  ($a_month, $a_year) = @_;

  open(DATA, "<$DATA_FILE_NAME") || die "unable to open $DATA_FILE_NAME $!\n";
  open(INPUT, "cal $a_month $a_year |") || die "unable to call cal: $!\n";
  $title = <INPUT>;
  chop($title);

  if ($title =~ /\s*(\S+)\s(\d+)$/)
  {
    $MONTH = $1;
  }

  # gets the data for days which have events
  parse_data($a_month, $a_year);
  close(DATA);
}

##################################################################
# if user not submitting info regarding which date to display
# then create the form based on current date
##################################################################

# Get today's date which may or may not be used.######### 
open(DATE, "date +%m/%e/%Y|") || die "unable to call date: $!\n";
$today = <DATE>;
chop($today);
($today_month, $today_day, $today_year) = split(/\//,$today);


# Start webpage #########################################
print $query->header,
      $query->start_html(-title=>'OpenHPI Calendar of Events',
                         -expires=>now);


print $query->startform('post',
                        'calendar.cgi',
                        'multipart/form-data');

# if user did not submit data, then display today's calendar
if (!$query->param)
{
   display_calendar($today_month, $today_day, $today_year);
}
else
{
   # if user clicked a day on the calendar, then display that 
   # day's events
   if ($query->param('event') eq 1)
   {
      display_calendar($query->param('month'), 
                       $query->param('day'),
                       $query->param('year'));

   }
   else # display a month and year as selected by user
   {
      display_calendar($query->param('month'), 
                       0,
                       $query->param('year'));
   }
}

print $query->endform;
print $query->end_html;

close (INPUT);

