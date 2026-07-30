"""Organization and company name extraction.

This module provides extraction of organization names from text.
"""
from __future__ import annotations

import re
from typing import Generator

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator


class OrganizationAnnotator(BaseAnnotator):
    """Extract organization and company names from text.

    Language support: English suffixes (Inc, LLC, Corp, Ltd, University…) plus
    common international legal forms: German (GmbH, AG), French (SA, SAS,
    SARL, EURL), Spanish/Portuguese (SA, SRL, Ltda), Italian (SpA, SRL, Srl),
    Dutch (BV, NV), and pan-European (SE, SCE).

    This annotator identifies organization names using explicit markers:
    - Company suffixes: Inc, LLC, Corp, Ltd, Co
    - Organization words: University, College, Institute, Hospital

    Only matches high-confidence patterns to avoid false positives.

    Example:
        ```python
        from simple_NER.annotators.organization_ner import OrganizationAnnotator

        ner = OrganizationAnnotator()
        text = "Apple Inc and Microsoft Corp partnered with MIT"
        for ent in ner.extract_entities(text):
            print(f"{ent.value} -> {ent.entity_type}")
        ```
    """

    # Company legal-form suffixes — English + common international forms
    _COMPANY_SUFFIXES = (
        # English
        r'Inc\.?|LLC|Corp\.?|Corporation|Ltd\.?|Limited|Co\.?|Company|Group|'
        r'PLC|LLP|LP|Partnership|'
        # German / Austrian / Swiss
        r'GmbH|AG|KG|OHG|UG|e\.V\.|'
        # French
        r'SA|SAS|SARL|EURL|SNC|SCI|'
        # Spanish / Portuguese / Italian
        r'SRL|Srl|SpA|SPA|Ltda|LTDA|'
        # Dutch / Belgian
        r'BV|NV|VOF|'
        # Pan-European
        r'SE|SCE'
    )
    _WORD = r'[A-Z\u00C0-\u024F][a-zA-Z\u00C0-\u024F\-]+'

    # Conservative, high-confidence patterns only
    ORG_PATTERNS = [
        # Name followed by legal-form suffix
        rf'\b{_WORD}(?:\s+{_WORD})*\s+(?:{_COMPANY_SUFFIXES})\b',
        # Educational/Research
        rf'\b{_WORD}(?:\s+{_WORD})*\s+(?:University|College|Institute|Laboratory|School|Université|Universidad|Universidade|Università|Universität|Hochschule)\b',
        # Medical
        rf'\b{_WORD}(?:\s+{_WORD})*\s+(?:Hospital|Clinic|Medical\s+Center|Clinique|Clínica|Clinica|Krankenhaus)\b',
    ]

    def __init__(
        self,
        confidence: float = 0.85,
        strict_mode: bool = True,
    ) -> None:
        """Initialize OrganizationAnnotator.

        Args:
            confidence: Default confidence score.
            strict_mode: Only match explicit organization markers.
        """
        super().__init__(confidence=confidence)
        self._strict_mode = strict_mode

        # Try loading patterns from locale; fall back to class-level ORG_PATTERNS
        locale_patterns = self._load_rx("organization")
        if locale_patterns:
            if strict_mode:
                self._compiled_patterns = locale_patterns[:2]
            else:
                self._compiled_patterns = locale_patterns
        else:
            if strict_mode:
                self._compiled_patterns = [
                    re.compile(p) for p in self.ORG_PATTERNS[:2]
                ]
            else:
                self._compiled_patterns = [
                    re.compile(p) for p in self.ORG_PATTERNS
                ]

    @property
    def name(self) -> str:
        """Return annotator name."""
        return "organization"

    def annotate(self, text: str) -> Generator[Entity, None, None]:
        """Extract organization names from text.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects for detected organizations.
        """
        seen = set()

        for pattern in self._compiled_patterns:
            for match in pattern.finditer(text):
                org = match.group().strip()

                # Skip duplicates and very short matches
                if org in seen or len(org) < 4:
                    continue
                seen.add(org)

                # Determine organization type
                org_type = self._classify_org(org)

                yield Entity(
                    value=org,
                    entity_type="organization",
                    source_text=text,
                    confidence=self.confidence,
                    data={
                        "org_type": org_type,
                        "start": match.start(),
                        "end": match.end(),
                    }
                )

    def _classify_org(self, org: str) -> str:
        """Classify organization type.

        Args:
            org: Organization string.

        Returns:
            Organization type classification.
        """
        org_lower = org.lower()

        company_markers = [
            'inc', 'llc', 'corp', 'ltd', 'co', 'plc', 'llp',
            'gmbh', 'ag', 'kg', 'ug',
            'sa', 'sas', 'sarl', 'eurl',
            'srl', 'spa', 'ltda',
            'bv', 'nv', 'se', 'sce',
        ]
        edu_markers = [
            'university', 'college', 'institute', 'school', 'laboratory',
            'université', 'universidad', 'universidade', 'università',
            'universität', 'hochschule',
        ]
        medical_markers = [
            'hospital', 'clinic', 'medical',
            'clinique', 'clínica', 'clinica', 'krankenhaus',
        ]

        if any(s in org_lower for s in company_markers):
            return "company"
        elif any(s in org_lower for s in edu_markers):
            return "educational"
        elif any(s in org_lower for s in medical_markers):
            return "medical"
        else:
            return "other"


if __name__ == "__main__":
    ner = OrganizationAnnotator()
    text = """
    Apple Inc and Microsoft Corp announced partnership.
    Google LLC will work with MIT and Stanford University.
    The FDA approved treatment at Johns Hopkins Hospital.
    """

    print(f"Text: {text.strip()}")
    print("-" * 60)

    for ent in ner.extract_entities(text):
        data = ent.data
        print(f"{ent.value:30} -> {data['org_type']} (conf: {ent.confidence:.2f})")
