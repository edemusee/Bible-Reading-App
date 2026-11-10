# Credits

## Greek lexical aids (SBL Greek New Testament)

The word-level data in `data/grc_sblgnt_tokens.txt` and `data/grc_sblgnt_lexicon.txt`
(lemmas, Strong's numbers, morphology, glosses, semantic domains, Louw-Nida entries)
is derived from [MACULA Greek Linguistic Datasets](https://github.com/Clear-Bible/macula-greek),
© 2022-2024 Biblica, Inc., licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Semantic domain labels come from the UBS MARBLE
[Semantic Dictionary of Biblical Greek](https://semanticdictionary.org/), as distributed in MACULA.

The data was converted into this app's format by `tools/build-greek-aux.py`.

## Dutch Bibles

`data/nl_hsv.txt` (Herziene Statenvertaling, 2017 edition) and `data/nl_sv.txt`
(Statenvertaling, Jongbloed edition) were converted from the [bolls.life](https://bolls.life)
exports (`HSV17`, `SVRJ`) by `tools/build-bolls-version.py`, with cross-reference markers removed.
The Herziene Statenvertaling is © Stichting HSV; the Statenvertaling text is in the public domain.
