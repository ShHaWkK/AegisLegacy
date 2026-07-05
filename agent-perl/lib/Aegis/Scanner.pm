package Aegis::Scanner;

use strict;
use warnings;
use utf8;
use v5.16;

use Exporter qw(import);

our @EXPORT_OK = qw(scan_file rules);

=head1 NAME

Aegis::Scanner - Détection de patterns simples, ligne par ligne.

=head1 DESCRIPTION

Contrairement au moteur Python (backend/app/rules), cet agent n'a
volontairement PAS de dépendance YAML : la liste des dépendances Perl du
projet (voir cpanfile) se limite à des modules cœur (File::Find, JSON::PP,
Digest::SHA, HTTP::Tiny, Getopt::Long, Test::More). Le jeu de règles
ci-dessous est donc un sous-ensemble volontairement léger de règles à
haute valeur, pas une réimplémentation complète du moteur de règles
Python — la source de vérité pour la détection exhaustive reste
backend/app/rules avec ses règles YAML.

=cut

our @RULES = (
    {
        id             => 'AGENT-CMD-001',
        language       => 'perl',
        severity       => 'critical',
        category       => 'command-injection',
        title          => 'Appel système potentiellement dangereux',
        pattern        => qr/system\s*\(|`[^`]+`/,
        description    => "system(), les backticks ou exec() exécutent une commande externe. "
                         . "Si une partie de la commande vient d'une entrée utilisateur, "
                         . "c'est une injection de commande potentielle.",
        recommendation => "Utiliser system(LIST) sans interpolation shell, valider/whitelister "
                         . "toute entrée utilisée dans la commande.",
    },
    {
        id             => 'AGENT-EVAL-001',
        language       => 'perl',
        severity       => 'high',
        category       => 'unsafe-eval',
        title          => "Utilisation de eval sous forme de chaîne",
        pattern        => qr/eval\s*\(?\s*["']|eval\s+\$/,
        description    => "eval() sous forme de chaîne compile et exécute du code Perl "
                         . "arbitraire à l'exécution.",
        recommendation => "Remplacer par eval { ... } (bloc) pour la gestion d'erreurs, "
                         . "éviter la génération de code dynamique.",
    },
    {
        id             => 'AGENT-SUBPROC-001',
        language       => 'python',
        severity       => 'critical',
        category       => 'command-injection',
        title          => 'Appel subprocess avec shell=True',
        pattern        => qr/subprocess\.(?:run|call|Popen|check_call|check_output)\(
                              (?:[^()]|\([^()]*\))*shell\s*=\s*True
                              | os\.(?:system|popen)\s*\(/x,
        description    => "shell=True (ou os.system/os.popen) exécute la commande via le shell "
                         . "système : toute donnée non fiable dans la commande peut injecter "
                         . "des commandes shell arbitraires.",
        recommendation => "Passer la commande sous forme de liste, avec shell=False (le défaut).",
    },
    {
        id             => 'AGENT-SECRET-001',
        language       => 'any',
        severity       => 'critical',
        category       => 'hardcoded-secret',
        title          => 'Identifiant ou clé API en dur',
        pattern        => qr/(?i)(api[_-]?key|secret|password|passwd|token)\s*[:=]\s*
                              ["'][A-Za-z0-9\/_.\-]{8,}["']/x,
        description    => "Une chaîne assignée à une variable/clé nommée comme un identifiant "
                         . "(password, secret, api_key, token, ...).",
        recommendation => "Déplacer la valeur vers une variable d'environnement ou un gestionnaire "
                         . "de secrets, et faire tourner l'identifiant exposé.",
    },
);

sub _language_for_extension {
    my ($ext) = @_;
    return 'perl'   if $ext =~ /^\.(?:pl|pm|cgi)$/i;
    return 'python' if $ext =~ /^\.py$/i;
    return 'any';
}

sub rules { return @RULES }

# scan_file(\%file_meta, $content) -> liste de hashrefs finding
#   { rule_id, severity, title, category, language, file, line, matched_text,
#     description, recommendation }
sub scan_file {
    my ($file_meta, $content) = @_;
    return () unless defined $content;

    my $language = _language_for_extension($file_meta->{extension} // '');
    my @applicable = grep { $_->{language} eq 'any' || $_->{language} eq $language } @RULES;
    return () unless @applicable;

    my @findings;
    my @lines = split /\n/, $content, -1;

    for my $rule (@applicable) {
        for my $i (0 .. $#lines) {
            my $line = $lines[$i];
            while ($line =~ /$rule->{pattern}/g) {
                push @findings, {
                    rule_id        => $rule->{id},
                    severity       => $rule->{severity},
                    title          => $rule->{title},
                    category       => $rule->{category},
                    language       => $language,
                    file           => $file_meta->{relative_path},
                    line           => $i + 1,
                    matched_text   => $&,
                    description    => $rule->{description},
                    recommendation => $rule->{recommendation},
                };
            }
        }
    }

    return @findings;
}

1;
