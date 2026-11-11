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

## Additional Bible versions (November 2026)

Converted by `tools/build-bolls-version.py` from [bolls.life](https://bolls.life) exports:

- `he_wlc` — Westminster Leningrad Codex (Hebrew Old Testament) (Hebrew; bolls code `WLC`)
- `la_vulgate` — Clementine Vulgate (1592) (Latin; bolls code `VULG`)
- `ja_shinkai` — 新改訳 Shinkai-yaku (3rd ed., 2003) (Japanese; bolls code `NJB`)
- `ja_kougo` — 口語訳 Kougo-yaku (1955) (Japanese; bolls code `JPKJV`)
- `id_tb` — Terjemahan Baru (Indonesian; bolls code `TB`)
- `uk_ohienko` — Біблія в перекладі Івана Огієнка (1962) (Ukrainian; bolls code `UBIO`)
- `af_afr53` — Afrikaans 1933/1953 (Afrikaans; bolls code `AFR53`)
- `ml_mov` — സത്യവേദപുസ്തകം Malayalam Old Version (Malayalam; bolls code `MOV`)
- `kn_kncl` — ಕನ್ನಡ ಸತ್ಯವೇದವು Kannada Bible C.L. (BSI) (Kannada; bolls code `KNCL`)
- `ne_nnrv` — Nepali New Revised Version (2012) (Nepali; bolls code `NNRV`)
- `es_lbla` — La Biblia de las Américas (1997) (Spanish; bolls code `LBLA`)
- `es_ntv` — Nueva Traducción Viviente (2009) (Spanish; bolls code `NTV`)
- `fr_lsg` — Louis Segond (1910) (French; bolls code `FRLSG`)
- `fr_nbs` — Nouvelle Bible Segond (2002) (French; bolls code `NBS`)
- `fr_darby` — Bible Darby (1890) (French; bolls code `FRDBY`)
- `fr_bds` — Bible du Semeur (2015) (French; bolls code `BDS`)
- `de_lut1912` — Luther (1912) (German; bolls code `LUT`)
- `de_sch2000` — Schlachter 2000 (German; bolls code `S00`)
- `zh_cuv` — Chinese Union Version (Traditional) 和合本 (Chinese; bolls code `CUV`)
- `ru_synod` — Синодальный перевод (Russian; bolls code `SYNOD`)

Converted by `tools/build-ebible-version.py` from [eBible.org](https://ebible.org) verse-per-line exports,
all marked redistributable by eBible.org; see `https://ebible.org/<id>/` for each translation's copyright and license
(the Biblica® Open texts are CC BY-SA 4.0):

- `yo_ycb` — Bíbélì Mímọ́ Yorùbá Òde Òní (Biblica Open) (Yoruba; eBible id `yor`)
- `ig_icb` — Baịbụlụ Nsọ nʼIgbo Ndị Ugbu a (Biblica Open) (Igbo; eBible id `ibo`)
- `ha_hcb` — Littafi Mai Tsarki, Sabon Rai Don Kowa (Biblica Open) (Hausa; eBible id `hausa`)
- `tw_akuapem` — Akuapem Twi Nkwa Asɛm (Biblica Open) (Twi; eBible id `twi`)
- `tw_asante` — Asante Twi Nkwa Asɛm (Biblica Open) (Twi; eBible id `twiasante`)
- `om_oncv` — Kitaaba Qulqulluu, New Oromo Contemporary Version (Biblica Open) (Oromo; eBible id `gaz`)
- `sn_scb` — Bhaibheri Dzvene MuChiShona Chanhasi (Biblica Open) (Shona; eBible id `sna`)
- `ny_ccl` — Mawu a Mulungu mu Chichewa Chalero (Biblica Open) (Chichewa; eBible id `nya`)
- `lg_lcb` — Bayibuli Entukuvu (Biblica Open) (Luganda; eBible id `lug`)
- `ki_kcb` — Kiugo Gĩtheru Kĩa Ngai Kĩhingũre (Biblica Open) (Kikuyu; eBible id `kik`)
- `ln_lcb` — Mokanda na Bomoi (Biblica Open) (Lingala; eBible id `lin`)
- `so_som` — Kitaabka Quduuska Ah (Somali; eBible id `som`)
- `am_amh` — መጽሐፍ ቅዱስ Amharic New Testament (1962) (Amharic; eBible id `amh`)
- `gu_irvguj` — Indian Revised Version (IRV) Gujarati 2019 (Gujarati; eBible id `guj2017`)
- `or_irvory` — Indian Revised Version (IRV) Odia (Odia; eBible id `ory`)
- `as_irvasm` — Indian Revised Version (IRV) Assamese 2019 (Assamese; eBible id `asmfb`)
- `my_judson` — Judson Bible (1840) (Burmese; eBible id `myajvb`)
- `ceb_apsd` — Ang Pulong sa Dios (Biblica Open) (Cebuano; eBible id `cebocb`)
- `ilo_ulb` — Ti Biblia (Unlocked Literal Bible) (Ilocano; eBible id `iloulb`)
- `ht_bib1985` — Bib La (1985) (Haitian Creole; eBible id `hat`)
- `da_1931` — Bibelen (1931/1907) (Danish; eBible id `dan1931`)
- `hr_sb` — Sveta Biblija (Croatian; eBible id `hrv`)
- `lt_tpv` — Tikinčiųjų paveldo vertimas (Lithuanian; eBible id `lit`)

Many of these translations are under copyright held by their publishers.
