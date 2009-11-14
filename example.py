import time
from swedishbanks import Swedbank, Nordea

templ = {'irc': {
            'time': '[%s]',
            'title': '[\x02%s\x02]',
            'account': '%s: \x02%s\x02;',
            'sum': 'Summa: \x02\x1f%s'
            },
         'plain': {
            'title': '[%s]',
            'account': '%s: %s;',
            'sum': 'Summa: %s'
            }
        }
def printaccount(bank, name="BANK", template="plain"):
    if 'time' in templ[template]:
        print templ[template]['time'] % time.asctime().split()[3],
    if 'title' in templ[template]:
        print templ[template]['title'] % name,
    for acc in bank.accounts:
        print templ[template]['account'] % (acc[0].capitalize(), acc[1]),
    if 'sum' in templ[template]:
        print templ[template]['sum'] % sum([a[1] for a in bank.accounts])

if __name__ == "__main__":
    b = Swedbank("19760518XXXX", "password")
    printaccount(b, "SWEDBANK", "irc")
    b = Nordea("19760518-XXXX", "password")
    printaccount(b, "NORDEA", "plain")
