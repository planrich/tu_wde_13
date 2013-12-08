#!/usr/bin/perl

# Author: Florian Kromp, Richard Plangger
# 08.12.2013

# Jaro Winkler metric; based on the implementation of SimMetrics:
# * Copyright (C) 2005 Sam Chapman - Open Source Release v1.1
# * email:       s.chapman@dcs.shef.ac.uk
# * www:         http://www.dcs.shef.ac.uk/~sam/
# * www:         http://www.dcs.shef.ac.uk/~sam/stringmetrics.html
# *
# * address:     Sam Chapman,
# *              Department of Computer Science,
# *              University of Sheffield,
# *              Sheffield,
# *              S. Yorks,
# *              S1 4DP
# *              United Kingdom,

my $string1;
my $string2;
my $threshold;

if (!($ARGV[2]))
{
	print "Aufruf: ./jaro.pl string1 string2 threshold \n";
	exit;
}

$string1 = $ARGV[0];
$string2 = $ARGV[1];
$threshold = $ARGV[2];
print "String1: $string1\n";
print "String2: $string2\n";
print "Threshold: $threshold\n";
$similarity = getSimilarity($string1,$string2,2);
print "Similarity: $similarity \n";

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
    my $halflen = (min(length($string1), length($string2)) / 2) + 1;

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
    $transpositions = $transpositions / 2;
    return ($laengeCommon1 / length($string1) + $laengeCommon2 / (length($string2) + ($laengeCommon1 - $transpositions) / $laengeCommon1) / 3);    
}
