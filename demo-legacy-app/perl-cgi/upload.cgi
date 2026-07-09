#!/usr/bin/perl
#
# Vieux script CGI d'upload, écrit avant l'arrivée de quiconque dans
# l'équipe actuelle. Personne n'ose y toucher. C'est exactement le genre
# de fichier qu'AegisLegacy est censé repérer.
#
# ATTENTION : ce fichier est un exemple pédagogique, volontairement
# vulnérable. Il ne tourne jamais en production, il ne sert qu'à donner
# de la matière au scanner. Ne pas s'en inspirer.

use strict;
use warnings;
use CGI;

my $cgi = CGI->new;
my $filename = $cgi->param('file');
my $destination = $cgi->param('destination') || '/var/uploads';

print $cgi->header('text/plain');

# Le nom de fichier vient directement du formulaire, sans validation, et
# part tel quel dans une commande shell. N'importe qui peut y glisser
# "; rm -rf /" et se faire plaisir.
system("mv /tmp/incoming/$filename $destination/$filename");

# Ancien style d'open à deux arguments : le mode est déduit de la chaîne.
# Si $filename contenait un "|" en fin de nom, ça ouvrirait un pipe vers
# une commande au lieu d'un fichier.
open LOG, ">>logs/upload.log";
print LOG "uploaded $filename to $destination\n";
close LOG;

print "OK: $filename uploaded.\n";
