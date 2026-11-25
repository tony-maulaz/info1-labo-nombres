"""Affichage des tests en français.

pytest affiche d'habitude le nom des fonctions de test et une trace Python.
Ici, on affiche à la place une ligne par test (OK ou ÉCHEC, ce qui est testé,
la commande), puis le détail des premiers tests en échec.

Les tests eux-mêmes sont dans test_cli.py.
"""

import pytest

# Détailler tous les échecs d'un coup noie l'information : on montre les
# premiers, les suivants apparaissent une fois ceux-ci corrigés.
MAX_DETAILED_FAILURES = 3

LINE_WIDTH = 78
STATUS_WIDTH = 9
SEPARATOR = "─" * LINE_WIDTH

# Le test (Case de test_cli.py) de chaque élément collecté par pytest.
cases = {}
terminal = None


@pytest.hookimpl(trylast=True)
def pytest_sessionstart(session):
    global terminal
    terminal = session.config.pluginmanager.get_plugin("terminalreporter")


def pytest_itemcollected(item):
    callspec = getattr(item, "callspec", None)
    if callspec is not None and "case" in callspec.params:
        cases[item.nodeid] = callspec.params["case"]


def title_and_command(report):
    case = cases.get(report.nodeid)
    if case is None:
        return report.nodeid, ""
    return case.title, case.command


def shortened(text, width):
    return text if len(text) <= width else text[: width - 1] + "…"


def count(passed):
    return f"{passed} test réussi" if passed <= 1 else f"{passed} tests réussis"


def section():
    terminal.write_line("")
    terminal.write_line(SEPARATOR)


@pytest.hookimpl(tryfirst=True)
def pytest_report_teststatus(report):
    # Sans lettre ni mot, pytest n'affiche rien pour ce test : sa ligne est
    # écrite par pytest_runtest_logreport ci-dessous.
    if report.when == "call":
        return report.outcome, "", ""
    return None


def pytest_collection_finish(session):
    terminal.write_line("")
    terminal.write_line(f"Tests du programme ./app ({len(session.items)} tests)", bold=True)
    terminal.write_line(SEPARATOR)


def pytest_runtest_logreport(report):
    if report.when != "call":
        return
    title, command = title_and_command(report)
    title_width = max((len(case.title) for case in cases.values()), default=0)
    command_width = LINE_WIDTH - STATUS_WIDTH - title_width - 2

    if report.passed:
        terminal.write("  OK     ", green=True, bold=True)
    else:
        terminal.write("  ÉCHEC  ", red=True, bold=True)
    terminal.write_line(f"{title:<{title_width}}  {shortened(command, command_width)}".rstrip())


def pytest_terminal_summary(terminalreporter):
    passed = terminalreporter.stats.get("passed", [])
    failed = terminalreporter.stats.get("failed", [])

    for number, report in enumerate(failed[:MAX_DETAILED_FAILURES]):
        title, command = title_and_command(report)
        if number > 0:
            terminal.write_line("")
        terminal.write_line(SEPARATOR)
        terminal.write_line(f"ÉCHEC : {title}", red=True, bold=True)
        if command:
            terminal.write_line(f"Commande : {command}")
        terminal.write_line("")
        terminal.write_line(report.longreprtext)

    hidden = len(failed) - MAX_DETAILED_FAILURES
    if hidden == 1:
        section()
        terminal.write_line("1 autre test en échec n'est pas détaillé.")
    elif hidden > 1:
        section()
        terminal.write_line(f"{hidden} autres tests en échec ne sont pas détaillés.")
    if hidden > 0:
        terminal.write_line("Corrigez d'abord ceux-ci, puis relancez `make test`.")

    if failed:
        terminal.write_line("")
    terminal.write_line(SEPARATOR)
    terminal.write_line(
        f"Résultat : {count(len(passed))} sur {len(passed) + len(failed)}",
        bold=True,
        green=not failed,
        red=bool(failed),
    )
    if failed:
        terminal.write_line("Pour rejouer un test, copiez sa commande dans le terminal.")
        terminal.write_line("Ensuite, `echo $?` affiche le code de retour.")
