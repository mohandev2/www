#! /usr/bin/perl

##################################################################
# This program was sloppily thrown together by
# Andrea Brugger. Edit as you like according to the terms below.
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

use CGI qw/:standard :html3/;
$query = new CGI;

##################################################################
# These are the user configurable parameters
##################################################################
$CAL_TITLE = "OpenHPI Calendar of Events";
$DATA_FILE_NAME = "/home/groups/o/op/openhpi/htdocs/script/events.cal";
$CGI_NAME = "hpi_cal.cgi";
$IMAGE_DIR = "/images";
$HTDOCS_DIR = "";

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

   print "<center>";
   print "<table border=2 cellspacing=2 cellpadding=4 bgcolor=\"#333333\" width=80% bordercolor=\"#000066\">";

   print "<tr><td bgcolor=\"#150185\" height=1%><font face=\"Arial, Helvetica, sans-serif\" size=\"5\" color=\"#FFFFFF\">";

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

  print "</center>";
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

   print "<td valign=top height=233 bgcolor=\"#FFFFFF\">\n";
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
         print "<a href=\"/cgi-bin/$CGI_NAME?event=1&day=$num&month=$a_month&year=$a_year\">";
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
-style=>{-src=>'http://openhpi.sourceforge.net/css/style.css', 
                                  -type=>'text/css',
                                  -rel=>'stylesheet'},
                         -expires=>now,
                         -vlink=>"#150185",
                         -alink=>"#FF0000",
                         -link=>"#150185",
                         -leftmargin=>"0",
                         -topmargin=>"5",
                         -marginheight=>"0", 
                         -marginwidth=>"0", 
                         -bgcolor=>"#FFFFFF");


print $query->startform('post',
                        $CGI_NAME,
                        'multipart/form-data');
top_body();

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

end_body();

print $query->endform;
print $query->end_html;

close (INPUT);

sub top_body
{
print <<"EOF";
<TABLE cellSpacing=0 cellPadding=0 width=760 align=center border=0>
  <TBODY>
  <TR>
    <TD>
      <TABLE cellSpacing=0 cellPadding=0 width="100%" border=0 height="57">
        <TBODY>
        <TR>
              <TD rowSpan=2 align="left" valign="bottom" height=57>
              <img border="0" src="$IMAGE_DIR/openhpi_blue_blnk.gif" width="124" height="59"></TD>
              <TD align=right width=501 height=34><i>
Last modified: Mar 28 2003            </TR>
        <TR>
          <TD vAlign=top width=501 height=23>
            <TABLE cellSpacing=0 cellPadding=0 width="100%" align=right
            background="" border=0>
              <TBODY>
              <TR>
                      <TD width=23 background="$IMAGE_DIR/topblackleft.gif" height=24>&nbsp;</TD>      
                      <TD align=center background="$IMAGE_DIR/toplinkbg.gif"><STRONG><FONT color=#ffffff><A
                  class=whitelink
                  href="http://openhpi.sf.net">Home</A> | <A class=whitelink
                  href="http://sourceforge.net/projects/openhpi">Project Page</A>
                        |
                  <A class=whitelink
                  href="mailto:rustyl\@users.sourceforge.net">Contact</A></FONT></STRONG></TD>
                      <TD width=20 background="$IMAGE_DIR/topblackright.gif"
          height=24>&nbsp;</TD>
                    </TR></TBODY></TABLE></TD></TR></TBODY></TABLE></TD></TR>
  <TR>
    <TD>
      <TABLE cellSpacing=0 cellPadding=0 width="100%" border=0>
<TBODY>
        <TR>
              <TD vAlign=top width=26 background="" height=21><IMG height=21
            src="$IMAGE_DIR/graybarleft.gif" width=26></TD>
              <TD background=$IMAGE_DIR/topgraybg.gif height=21><EM><STRONG>Hardware
              Platform Interface:&nbsp; Online Discussions</STRONG></EM></TD>
              <TD width=20 background="$IMAGE_DIR/graybarright.gif" height=21>&nbsp;</TD>
            </TR>
        </TBODY></TABLE></TD></TR>
  <TR>
    <TD bgcolor="#150185">&nbsp;</TD></TR>
  <TR>
    <TD>&nbsp;</TD></TR>
  <TR>
    <TD>
      <TABLE cellSpacing=0 cellPadding=0 width="100%" border=0>
<TBODY>
        <TR>
          <TD vAlign=top width=145>
            <TABLE cellSpacing=0 cellPadding=0 width="100%" border=0>
              <TBODY>
              <TR>
                <TD>
                  <TABLE cellSpacing=0 cellPadding=0 width="100%" border=0 ?>
                    <TBODY>
                    <TR>
                              <TD vAlign=top width=21 background=""><IMG height=21
                        src="$IMAGE_DIR/darkgrayleft.gif" width=21></TD>
                              <TD align=middle
                        background=$IMAGE_DIR/darkgraybg.gif><STRONG><FONT 
                        color=#ffffff>Links</FONT></STRONG></TD>
                              <TD vAlign=top width=19 
                      background=$IMAGE_DIR/darkgraybg.gif><IMG height=21
                        src="$IMAGE_DIR/darkgrayright.gif" 
                    width=19></TD>
                            </TR></TBODY></TABLE></TD></TR>
              <TR>
                      <TD><IMG height=5 
                  src="$IMAGE_DIR/trans.gif" width=5 border=0></A></TD>
</TR>
              <TR>
                <TD>
                  <TABLE cellSpacing=2 cellPadding=2 width="100%" border=0>
                    <TBODY>
                    <TR>
                              <TD vAlign=center align=middle width=20><IMG height=10 
                        src="$IMAGE_DIR/bwhite.gif" width=10></TD>
                      <TD vAlign=center>
                      <a href="http://lists.sourceforge.net/lists/listinfo/openhpi-devel">
                      <font size="-2">Mailing List Subscription</font></a></TD></TR>
                    <TR>
                              <TD vAlign=center align=middle width=20><IMG height=10 
                        src="$IMAGE_DIR/bwhite.gif" width=10></TD>
                      <TD vAlign=center>
                      <a href="http://sourceforge.net/mailarchive/forum.php?forum=openhpi-devel">
                      <font size="-2">Mailing List Archives</font></a></TD></TR>
                    <TR>
                              <TD vAlign=center align=middle width=20><IMG height=10 
                        src="$IMAGE_DIR/bwhite.gif" width=10></TD>
                      <TD vAlign=center>

                      <font size="-2"><a href="http://cvs.sourceforge.net/cgi-bin/viewcvs.cgi/openhpi">Browse Source</a></font></a></TD></TR>
                    <TR>
                              <TD vAlign=center align=middle width=20><IMG height=10 
                        src="$IMAGE_DIR/bwhite.gif" width=10></TD>
                      <TD vAlign=center>
                      <font size="-2"><a href="$HTDOCS_DIR/design.php">High-Level Design</a></font></TD></TR>
                    <tr>
                              <TD vAlign=center align=middle width=20><IMG height=10
                        src="$IMAGE_DIR/bwhite.gif" width=10></TD>
                      <TD vAlign=center>
                      <a href="$HTDOCS_DIR/status.php"><font size="-2">Status</font></a></TD>
                    </tr>
                    <tr>
                              <TD vAlign=center align=middle width=20><IMG height=10
                        src="$IMAGE_DIR/bwhite.gif" width=10></TD>
                      <TD vAlign=center>
                      <font size="-2">Calendar</font></TD>
                    </tr>
                    </TBODY></TABLE></TD></TR>
              <TR>
                <TD>&nbsp;</TD></TR>
              <TR>
                <TD>
                  <TABLE cellSpacing=0 cellPadding=0 width="100%" border=0 ?>
                    <TBODY>
                    <TR>
                              <TD vAlign=top width=21 
                      background=$IMAGE_DIR/darkgraybg.gif><IMG height=21
                        src="$IMAGE_DIR/darkgrayleft.gif" width=21></TD>
                              <TD align=middle
                        background=$IMAGE_DIR/darkgraybg.gif><STRONG><FONT 
                        color=#ffffff>News</FONT></STRONG></TD>
                              <TD vAlign=top width=19 
                      background=$IMAGE_DIR/darkgraybg.gif><IMG height=21
                        src="$IMAGE_DIR/darkgrayright.gif" 
                    width=19></TD>
                            </TR></TBODY></TABLE></TD></TR>
              <TR>
                      <TD><IMG height=5 
                  src="$IMAGE_DIR/trans.gif" width=5 border=0></A></TD>
</TR>
              <TR>
                <TD><!-- begin scroller -->
                  <SCRIPT language=JavaScript1.2 src="$HTDOCS_DIR/script/scroller.js"></SCRIPT>
                  <ILAYER id=fscrollerns 
                  width="&amp;{fwidth};" height="&amp;{fheight};"><LAYER
                  left="0" top="0" width="&amp;{fwidth};" 
                  height="&amp;{fheight};" id=fscrollerns_sub></LAYER></ILAYER><!-- end scroller --></TD></TR>
                  <TR><TD>&nbsp;</TD></TR>

                  <tr>
                <TD>
                  <TABLE cellSpacing=0 cellPadding=0 width="100%" border=0>
                    <TBODY>
                    <TR>
                              <TD vAlign=top width=21 background=""><IMG height=21 
                        src="$IMAGE_DIR/darkgrayleft.gif" width=21></TD>
                              <TD align=middle 
                        background=$IMAGE_DIR/darkgraybg.gif><strong>
                              <font color="#FFFFFF">Hosted By</font></strong></TD>
                              <TD vAlign=top width=19
                      background=$IMAGE_DIR/darkgraybg.gif><IMG height=21 
                        src="$IMAGE_DIR/darkgrayright.gif"
                    width=19></TD>
                            </TR></TBODY></TABLE></TD>
              </tr>
              <tr>
                      <TD><IMG height=5 
                  src="$IMAGE_DIR/trans.gif" width=5 border=0></A></TD>
              </tr>
              <tr>
                <TD>
                  <p align="center">
                  <a href="http://sourceforge.net"><img 
src="http://sourceforge.net/sflogo.php?group_id=71730&amp;type=3"
width="125" height="37" border="0" alt="SourceForge.net Logo"></a></TD>
              </tr>
                  <TR><TD>&nbsp;</TD></TR>

                  </TBODY></TABLE></TD>
          <TD>&nbsp;</TD>
              <TD width=593 valign="top">
                <TABLE cellSpacing=0 cellPadding=0 width="100%" border=0>
<TBODY>
              <TR>
                <TD>
EOF

}

sub end_body
{
print <<"EOF2";
              <tr>
                              <TD valign="top">
&nbsp;</TD>
              </tr>
              <tr>
                <TD>
                  <TABLE cellSpacing=0 cellPadding=0 width="100%" border=0>
                    <TBODY>
                    <TR>
                              <TD vAlign=top width=21
                      background=$IMAGE_DIR/darkgraybg.gif><IMG height=21
                        src="$IMAGE_DIR/darkgrayleft.gif" width=21></TD>
                              <TD align=middle
                        background=$IMAGE_DIR/darkgraybg.gif><strong>
                              <font color="#FFFFFF">IRC Discussion Information</font></strong></TD>
                              <TD vAlign=top width=19
                      background=$IMAGE_DIR/darkgraybg.gif><IMG height=21
                        src="$IMAGE_DIR/darkgrayright.gif"
                    width=19></TD>
                            </TR></TBODY></TABLE></TD>
              </tr>
              <tr>
                      <TD valign="top" background="$IMAGE_DIR/graymidbottom.gif">
<TABLE cellSpacing=5 cellPadding=5 width="100%" border=0>
                    <TBODY>
                    <TR>
                              <TD valign="top">
Server:&nbsp; irc.kernelnewbies.org  #openhpi</TD></TR>
                    </TBODY></TABLE></TD>
              </tr>
              <tr>
                <TD>
                  <TABLE cellSpacing=0 cellPadding=0 width="100%" border=0>
                    <TBODY>
                    <TR>
                              <TD vAlign=top width=21
                      background=$IMAGE_DIR/grayleftbottom.gif><IMG height=21
                                src="$IMAGE_DIR/grayleftbottom.gif"
                                width=21></TD>
                              <TD align=middle
                        background=$IMAGE_DIR/graymidbottom.gif>&nbsp;</TD>
                              <TD vAlign=top width=19
                      background=$IMAGE_DIR/darkgraybg.gif><IMG height=21
                                src="$IMAGE_DIR/grayrightbottom.gif"
                                width=20></TD>
                            </TR></TBODY></TABLE></TD>
              </tr>
              <tr>
                <TD>
                  &nbsp;</TD>
              </tr>
</TBODY></TABLE></TD></TR></TBODY></TABLE></TD></TR>
  <TR>
    <TD>&nbsp;</TD></TR>
  <TR>
    <TD>
      <TABLE cellSpacing=0 cellPadding=0 width="100%" border=0>
        <TBODY>
        <TR>
              <TD width=19><IMG height=53 src="$IMAGE_DIR/footerleft.gif" 
            width=19></TD>
          <TD background="">
            <TABLE width="100%" height=53
              border=0 cellPadding=0 cellSpacing=0 background="$IMAGE_DIR/footerbg.gif">
<TBODY>
              <TR>
                      <TD align=center><STRONG><FONT color=#ffffff><A
                  class=whitelink 
                 href="http://openhpi.sf.net">Home</A> | <A class=whitelink
                  href="http://sourceforge.net/projects/openhpi">Project Page</A> 
                        |
                  <A class=whitelink 
                  href="mailto:rustyl\@users.sourceforge.net">Contact</A></FONT></STRONG></TD>
</TR>
              <TR>
                      <TD align=center>&nbsp;</TD>
</TR></TBODY></TABLE></TD>
              <TD width=19><IMG height=53 src="$IMAGE_DIR/footerright.gif"
            width=19></TD>
            </TR></TBODY></TABLE></TD></TR></TBODY></TABLE>
EOF2
}
