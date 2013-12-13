#!/usr/bin/perl

# Author: Florian Kromp, Richard Plangger
# 08.12.2013

# Jaro metric; based on the implementation of SimMetrics:
# We have later implemented it according to
# http://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance
# because the impl. in the java
#
# Jaro winkler is implemented according to the wiki link above

my $string1;
my $string2;
my $threshold;

if (!($ARGV[1]))
{
    print "Aufruf: ./jaro.pl string1 string2 winkler_prefix_scale \n";
    exit;
}

$string1 = $ARGV[0];
$string2 = $ARGV[1];
$prefix_scale = $ARGV[2];
if ($prefix_scale eq undef) {
    $prefix_scale = 0.1; 
}
print "String1: $string1\n";
print "String2: $string2\n";
#print "Threshold: $threshold\n";
$similarity = getSimilarity($string1,$string2,2);
print "\n";
print "Jaro $similarity \n";
print "\n";
$winkler = jaro_winkler($string1, $string2, $prefix_scale);
print "Jaro Winkler (scale: $prefix_scale) $winkler\n";

sub jaro_winkler {
  my @string1 = split('',shift);
  my @string2 = split('',shift);
  my $prefix_scale = shift;

  my $prefix_len = 0;
  LOOP: {
    for (my $i = 0; $i < length($string1) && $i < length($string2); $i++) 
    {
      my $char1 = $string1[$i];
      my $char2 = $string2[$i];
      if ($char1 ne $char2) {
          last LOOP;
      }

      $prefix_len = $prefix_len + 1;
    }
  }

  my $jaro = getSimilarity($string1, $string2);

  return $jaro + ($prefix_len * $prefix_scale * (1 - $jaro));
}

sub max {
 my $a = shift;
 my $b = shift;
 return $a > $b ? $a : $b;
}

sub min {
 my $a = shift;
 my $b = shift;
 return $a < $b ? $a : $b;
}

sub getCommonCharacters
{
    # extracts CommonCharacters in a defined range passed to the variable $maxDistance
    my $string1 = shift;
    my $string2 = shift;
    my $maxDistance = shift;
    my @characters = ();
    my @string1 = split('',$string1);
    my @copy = split('',$string2);

    for ($i = 0; $i < length($string1); $i++) 
    {
        my $actual_char = $string1[$i];
        my $foundIt = 0;
        for ($j = max(0, $i - $maxDistance); (!($foundIt) && ($j < min($i + $maxDistance, length($string2)))); $j++) 
        {
            if ($copy[$j] eq $actual_char) 
            {
                $foundIt = 1;
                push @characters,$actual_char;
                $copy[$j] = '#';
            }
        }
    }
    return @characters;
}

sub getSimilarity
{
    # computes the Jaro-Winkler distance metric based on Common Characters and Transpositions
    my $string1 = shift;
    my $string2 = shift;
    my $halflen = int((min(length($string1), length($string2)) / 2) + 1);

    my @string1Common = getCommonCharacters($string1, $string2, $halflen);
    my @string2Common = getCommonCharacters($string2, $string1, $halflen);
    my $laengeCommon1 = @string1Common;
    my $laengeCommon2 = @string2Common;

    if (($laengeCommon1 == 0) || ($laengeCommon2 == 0)) 
    {
        return 0.0;
    }

    if ($laengeCommon1 != $laengeCommon2) 
    {
        return 0.0;
    }
    $transpositions = 0;
    for ($i = 0; $i < $laengeCommon1; $i++) 
    {
        if ($string1Common[$i] ne $string2Common[$i])
        {
            $transpositions++;
        }
    }
    my $inner = ($laengeCommon1 / length($string1)) + 
                ($laengeCommon2 / length($string2)) + 
                (($laengeCommon1 - $transpositions) / ($laengeCommon1));
    return $inner / 3;
}