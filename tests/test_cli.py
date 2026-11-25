"""Tests fonctionnels de ./app, d'après le cahier des charges de README.md.

Chaque ligne de la liste TESTS lance le programme avec des arguments, puis
contrôle ce qu'il affiche et son code de retour.

Pour lancer les tests :

    make test

Pour rejouer un test à la main, copiez sa commande dans le terminal, puis
affichez le code de retour :

    ./app -n -o 12,23,4
    echo $?
"""

import resource
import shlex
import signal
import subprocess
import tempfile
from pathlib import Path

import pytest

EXEC = Path(__file__).resolve().parents[1] / "app"

# Un programme qui boucle à l'infini est arrêté : on limite son temps
# d'exécution et la taille de ce qu'il affiche.
TIMEOUT_SECONDS = 1
MAX_OUTPUT_BYTES = 1024 * 1024

# Nombre de lignes montrées au maximum quand un affichage est faux.
MAX_SHOWN_LINES = 25

CODE_OK = 0
CODE_ERROR = 1

TWENTY_NUMBERS = ",".join(str(number) for number in range(1, 21))
TWENTY_ONE_NUMBERS = TWENTY_NUMBERS + ",21"


class Case:
    """Un test : les arguments donnés à ./app et ce qui est attendu."""

    def __init__(self, title, arguments, code, lines=None, shows_something=False):
        self.title = title
        self.arguments = arguments.split()
        self.code = code
        self.lines = lines  # None : l'affichage n'est pas contrôlé
        self.shows_something = shows_something

    @property
    def command(self):
        return shlex.join(["./app", *self.arguments])


def displays(title, arguments, lines):
    """Le programme affiche exactement ces lignes et retourne 0."""
    return Case(title, arguments, CODE_OK, lines=lines)


def version(title, arguments):
    """Le programme affiche un message (libre) et retourne 0."""
    return Case(title, arguments, CODE_OK, shows_something=True)


def error(title, arguments):
    """Le programme retourne 1, son affichage n'est pas contrôlé."""
    return Case(title, arguments, CODE_ERROR)


TESTS = [
    # ------------------------------------------------------------ affichage
    displays("affiche un nombre par ligne", "12,23,45,1", ["12", "23", "45", "1"]),
    displays(
        "option -n : numéro devant chaque nombre",
        "-n 12,23,45,1",
        ["1) 12", "2) 23", "3) 45", "4) 1"],
    ),
    displays("option -o : ordre décroissant", "-o 12,23,4", ["23", "12", "4"]),
    displays(
        "option -o avec un 0 et un doublon",
        "-o 5,0,12,5",
        ["12", "5", "5", "0"],
    ),
    displays(
        "options -n et -o ensemble",
        "-n -o 12,23,4",
        ["1) 23", "2) 12", "3) 4"],
    ),
    displays("options placées après les nombres", "12,23 -o -n", ["1) 23", "2) 12"]),
    displays(
        "20 nombres sont acceptés",
        TWENTY_NUMBERS,
        [str(number) for number in range(1, 21)],
    ),
    # -------------------------------------------------------------- version
    version("option -v : affiche la version", "-v"),
    version("option --version, même avec une erreur", "1,,2 --version"),
    # --------------------------------------------------------------- erreurs
    error("aucun nombre : code 1", ""),
    error("deux virgules qui se suivent : code 1", "1,,2"),
    error("lettre dans la liste : code 1", "1,a,3"),
    error("plus de 20 nombres : code 1", TWENTY_ONE_NUMBERS),
    error("option inconnue : code 1", "-x 1,2"),
]


def limit_output():
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT_BYTES, MAX_OUTPUT_BYTES))


def run(arguments):
    """Lance ./app et retourne (code de retour, affichage)."""
    if not EXEC.exists():
        pytest.fail("Le programme ./app n'existe pas : lancez `make`.", pytrace=False)

    with tempfile.TemporaryFile() as output:
        try:
            process = subprocess.run(
                [str(EXEC), *arguments],
                stdin=subprocess.DEVNULL,
                stdout=output,
                stderr=subprocess.DEVNULL,
                timeout=TIMEOUT_SECONDS,
                preexec_fn=limit_output,
            )
        except subprocess.TimeoutExpired:
            pytest.fail(
                "Votre programme ne se termine pas : y a-t-il une boucle infinie ?",
                pytrace=False,
            )
        output.seek(0)
        stdout = output.read().decode(errors="replace")

    if process.returncode == -signal.SIGXFSZ:
        pytest.fail(
            "Votre programme affiche sans s'arrêter : y a-t-il une boucle infinie ?",
            pytrace=False,
        )
    if process.returncode < 0:
        name = signal.Signals(-process.returncode).name
        pytest.fail(
            f"Votre programme a planté (signal {name}).\n"
            "Cause fréquente : lire ou écrire en dehors d'un tableau.",
            pytrace=False,
        )
    return process.returncode, stdout


def displayed_lines(stdout):
    """Les lignes affichées, sans les espaces en fin de ligne ni les lignes
    vides à la fin : ces différences invisibles ne sont pas sanctionnées."""
    lines = [line.rstrip() for line in stdout.splitlines()]
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def block(lines):
    """Des lignes indentées, prêtes à être montrées dans un message."""
    if not lines:
        return "    (rien)"
    shown = [f"    {line}" for line in lines[:MAX_SHOWN_LINES]]
    if len(lines) > MAX_SHOWN_LINES:
        shown.append(f"    ... ({len(lines) - MAX_SHOWN_LINES} lignes de plus)")
    return "\n".join(shown)


def first_difference(expected, actual):
    """Le numéro (dès 1) de la première ligne qui diffère."""
    for number, (expected_line, actual_line) in enumerate(zip(expected, actual), 1):
        if expected_line != actual_line:
            return number
    return min(len(expected), len(actual)) + 1


@pytest.mark.parametrize("case", TESTS, ids=[case.title for case in TESTS])
def test_app(case):
    code, stdout = run(case.arguments)
    actual = displayed_lines(stdout)
    problems = []

    if case.lines is not None and actual != case.lines:
        problems.append(
            "Affichage attendu :\n"
            f"{block(case.lines)}\n"
            "Affichage de votre programme :\n"
            f"{block(actual)}\n"
            f"La première différence est à la ligne {first_difference(case.lines, actual)}."
        )

    if case.shows_something and not actual:
        problems.append("Le programme devrait afficher un message, mais il n'affiche rien.")

    if code != case.code:
        problems.append(
            f"Code de retour attendu : {case.code}\n"
            f"Code de retour de votre programme : {code}"
        )

    if problems:
        pytest.fail("\n\n".join(problems), pytrace=False)
