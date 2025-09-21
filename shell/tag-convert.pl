#!/usr/bin/perl

use strict;
use warnings;
use Image::ExifTool qw(:Public);

my %keypath;
# csv databaza, prvy stlpec je keywords, zvysne tvoria hierarchiu 
my $dbfile = '/home/pato/tags.txt';
my $dir = $ARGV[0] or die "Usage: $0 <directory>";

sub urob_db {
  my @filerow;
  my $keyval;
  
  open( my $data, '<', $dbfile ) or die "Could not open '$dbfile' \n";
  while (my $line = <$data>) {
    chomp $line;
    @filerow = split( ",",$line);
    $keyval = shift @filerow;
    if (defined($keyval)) {
      $keypath{$keyval} = [ @filerow ];
    }
  }
  close $data;
}

sub dajhodnotu {
  my $keyval = $_[0];
 
  if (defined($keypath{$keyval})) {
    return @{ $keypath{$keyval} };
  }else {
    return undef;
  }
}

sub vytlac_db {
  foreach my $k (keys %keypath) {
    print $k,"=>",join('/',dajhodnotu($k)),"\n";
  }
}

sub zapis {
  my $file = $_[0];
  my $tool = Image::ExifTool->new();
  my $oddHS = '|'; 
  my $oddTL = '/';
  my @hodn;
  my @kwords;

  $tool->Options(List=>1);
  my $res = $tool->ExtractInfo($file);
  if ( $res == 1) {
    my $reflist = $tool->GetInfo('Keywords');
    if ( ref $reflist->{Keywords} eq 'ARRAY') {
      @kwords = @{ $reflist->{Keywords} };
    } else {
      if (defined($reflist->{Keywords})) {
        push ( @kwords, $reflist->{Keywords} );
      }
    }
    my $hsres = 0;
    my $tlres = 0;
    foreach my $i (0..$#kwords) {
      print $file," Keyword=", $kwords[$i];
      @hodn = dajhodnotu($kwords[$i]);
      if (defined($hodn[0])) {
        $hsres += $tool->SetNewValue('XMP:HierarchicalSubject'=> join($oddHS, @hodn), AddValue => 1);
        $tlres += $tool->SetNewValue('TagsList'=> join($oddTL, @hodn), AddValue => 1);
        print " Added=", join($oddTL, @hodn), "\n";
      } else {
        print " Added=<failed>", "\n";
      }
    }
 
    if ( ($hsres == $tlres ) and ($tool->WriteInfo($file) == 1)) {
      print $file," Updated \n";
    } else {
      print $file," Update failed\n";
    }

  } else {
    print $file, " - read failed\n";
  }
}

urob_db();
#vytlac_db();


opendir(my $dh, $dir) or die "Could not open directory '$dir' \n";
my @files = readdir($dh);
close($dh);

foreach my $jpg (@files) {
# skip if starts with dot
  next if($jpg =~ /^\./);
  #print $jpg, "\n";
  zapis($jpg);
}
