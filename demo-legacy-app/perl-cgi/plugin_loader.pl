#!/usr/bin/perl
#
# Petit système de "plugins" maison, écrit à l'arrache pour un besoin
# ponctuel il y a des années. Toujours en prod. Encore un candidat
# parfait pour AegisLegacy.
#
# ATTENTION : fichier d'exemple, volontairement vulnérable, jamais
# exécuté en dehors des démos du scanner.

use strict;
use warnings;

sub load_plugin {
    my ($plugin_name, $config) = @_;

    # On construit du code Perl sous forme de chaîne à partir d'un nom
    # de plugin fourni par l'utilisateur, puis on l'exécute avec eval.
    # Si $plugin_name contient autre chose qu'un nom de fichier, c'est
    # de l'exécution de code arbitraire, point final.
    my $code = "require 'plugins/$plugin_name.pl'; ${plugin_name}::run(\$config)";
    eval "$code";
    if ($@) {
        warn "Impossible de charger le plugin $plugin_name: $@";
    }
}

1;
