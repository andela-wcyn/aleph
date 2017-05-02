import re
import logging
from dalet import parse_phone

from aleph.analyze.analyzer import Analyzer

log = logging.getLogger(__name__)


class RegexAnalyzer(Analyzer):
    REGEX = None
    FLAG = None

    def prepare(self):
        # TODO: re-think this.
        self.disabled = self.document is not None and \
            self.document.type == self.document.TYPE_TABULAR
        self.matches = []
        self.regex = re.compile(self.REGEX, self.FLAG)

    def on_text(self, text):
        if not self.disabled:
            for mobj in self.regex.finditer(text):
                self.matches.append(mobj)


class EMailAnalyzer(RegexAnalyzer):
    REGEX = '[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}'
    FLAG = re.IGNORECASE

    def finalize(self):
        matches = set([m.group(0) for m in self.matches])
        if len(matches):
            log.info("Found emails: %r", matches)

        for email in matches:
            self.meta.add_email(email)


class URLAnalyzer(RegexAnalyzer):
    # http://www.noah.org/wiki/RegEx_Python
    REGEX = ur'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'  # noqa
    FLAG = re.IGNORECASE

    def finalize(self):
        matches = set([m.group(0) for m in self.matches])
        if len(matches):
            log.info("Found URLs: %r", matches)

        for url in matches:
            self.meta.add_url(url)


class PhoneNumberAnalyzer(RegexAnalyzer):
    REGEX = r'(\+?[\d\-\(\)\/\s]{5,})'
    CHARS = '+0123456789'
    FLAG = re.IGNORECASE

    def finalize(self):
        for match in self.matches:
            match = match.group(0)
            match = ''.join([m for m in match if m in self.CHARS])
            if len(match) < 5:
                continue
            for country in [None] + self.meta.countries:
                num = parse_phone(match, country=country)
                if num is not None:
                    self.meta.add_phone_number(num)
        if len(self.meta.phone_numbers):
            log.info("Found phone numbers: %s", self.meta.phone_numbers)
