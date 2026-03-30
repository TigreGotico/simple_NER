"""OVOS Intent Transformer plugin using simple_NER.

Runs after intent matching; extracts named entities from the matched utterance
and injects them into ``intent.match_data`` so skill handlers receive them
without needing to run NER themselves.

Plugin Type: opm.transformer.intent
Plugin ID: simple-ner.transformer

Configuration (mycroft.conf):
    {
        "intent_transformers": {
            "simple-ner.transformer": {
                "annotators": ["email", "names", "locations", "temporal", "numbers"],
                "confidence_threshold": 0.5,
                "lang": "en-us"
            }
        }
    }

    ``lang`` is the fallback language when no OVOS session is available.
    At runtime the active session language is used automatically, so the pipeline
    rebuilds its language-sensitive annotators whenever the session language changes.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ovos_plugin_manager.templates.pipeline import IntentHandlerMatch
from ovos_plugin_manager.templates.transformers import IntentTransformer
from ovos_utils.log import LOG

try:
    from ovos_utils.session import SessionManager as _SessionManager
except ImportError:
    _SessionManager = None  # type: ignore[assignment]

from simple_NER.annotators.factory import create_pipeline
from simple_NER.pipeline import NERPipeline

# Entity type → match_data key mapping
_TYPE_MAP: Dict[str, str] = {
    "email": "email",
    "person": "person",
    "noun": "person",
    "country": "location",
    "capital city": "location",
    "city": "location",
    "location": "location",
    "relative_date": "date_time",
    "date": "date_time",
    "duration": "duration",
    "written_number": "number",
    "organization": "organization",
    "url": "url",
    "phone_number": "phone",
    "money": "currency",
}


class SimpleNERIntentTransformer(IntentTransformer):
    """Intent Transformer that enriches match_data with simple_NER entities.

    Runs NER on the matched utterance and injects extracted entities into
    ``intent.match_data``, keyed by their mapped entity type.
    Existing keys in ``match_data`` are never overwritten.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialise the transformer.

        Args:
            config: Optional config dict (overrides mycroft.conf lookup).
        """
        super().__init__("simple-ner-transformer", 50, config)
        self._annotator_names: List[str] = self.config.get(
            "annotators",
            ["email", "names", "locations", "temporal", "numbers"],
        )
        self._confidence_threshold: float = self.config.get("confidence_threshold", 0.5)
        self._default_lang: str = self.config.get("lang", "en-us")
        self._pipeline: Optional[NERPipeline] = None
        self._pipeline_lang: Optional[str] = None
        LOG.info(f"SimpleNER Intent Transformer initialised with annotators: {self._annotator_names}")

    def _get_pipeline(self, lang: str) -> NERPipeline:
        """Return (or rebuild) the NER pipeline for the given language.

        The pipeline is rebuilt only when the language changes, so per-request
        overhead is negligible for the common case where all utterances share
        one language.

        Args:
            lang: BCP-47 language tag.

        Returns:
            A ready ``NERPipeline`` instance.
        """
        if self._pipeline is None or self._pipeline_lang != lang:
            try:
                self._pipeline = create_pipeline(
                    self._annotator_names,
                    dedup_strategy="keep_higher_confidence",
                    lang=lang,
                )
                self._pipeline_lang = lang
            except Exception as exc:
                LOG.error(f"Failed to create NER pipeline (lang={lang}): {exc}")
                self._pipeline = NERPipeline([])
                self._pipeline_lang = lang
        return self._pipeline

    def transform(self, intent: IntentHandlerMatch) -> IntentHandlerMatch:
        """Inject NER entities into ``intent.match_data``.

        Args:
            intent: The matched intent from the pipeline.

        Returns:
            The same intent with NER entities added to ``match_data``.
        """
        try:
            # Resolve language from session → config default
            lang = self._default_lang
            sess = getattr(intent, "updated_session", None)
            if sess is None and _SessionManager is not None:
                try:
                    sess = _SessionManager.get()
                except Exception:
                    pass
            if sess is not None:
                lang = getattr(sess, "lang", lang) or lang

            pipeline = self._get_pipeline(lang)
            entities = [
                e for e in pipeline.process(intent.utterance)
                if e.confidence >= self._confidence_threshold
            ]
            for entity in entities:
                key = _TYPE_MAP.get(entity.entity_type.lower(), entity.entity_type.lower())
                # Do not overwrite entities already extracted by the intent engine
                if key not in intent.match_data:
                    intent.match_data[key] = entity.value
            if entities:
                LOG.debug(f"Injected {len(entities)} NER entities into match_data for: {intent.utterance[:60]}")
        except Exception as exc:
            LOG.error(f"Error in SimpleNERIntentTransformer.transform: {exc}")
        return intent
