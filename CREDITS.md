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

## Commentaries

Converted by `tools/build-sword-commentary.py` (markup handled by `tools/commentary_html.py`) from
public-domain CrossWire SWORD modules (https://www.crosswire.org/sword/modules/):
`calvin` (CalvinCommentaries), `geneva` (Geneva), `mhc` (MHC), `mhcc` (MHCC), `burkitt` (Burkitt),
`lightfoot` (Lightfoot), `tdavid` (TDavid), `jfb` (JFB), `barnes` (Barnes), `tsk` (TSK).

Additional commentaries:
- `gill`, `poole` — MySword modules by Costas Stergiou (theword.gr), converted by
  `tools/build-mysword-commentary.py`. Gill's text is the Online Bible edition; that edition's
  SWORD release carries a rights notice from Larry Pierce.
- `trapp` — archive.org item `JohnTrappsBibleCommentaries` (one EPUB per book), converted by
  `tools/build-trapp-commentary.py`.
- `gouge` (A41670), `caryl` (A35389, A35438, A35439, A35473, A81199, A35535, A35537, A35538),
  `durham_rev` (A37035), `durham_song` (A37032), `burroughs` (A30572, A77979, A30574, A30575),
  `dickson_ps` (A35941, A35945, A35943), `dickson_matt` (A35949), `dickson_heb` (A20414) and
  `owen_heb` chapters 6–10 (A53678) — EEBO-TCP transcriptions released under CC0
  (https://github.com/textcreationpartnership), converted by `tools/build-tcp-commentary.py`.
- `manton` (manton04.xml, manton05.xml) and `hodge_eph` (hodge/ephesians.xml) — CCEL ThML,
  converted by `tools/build-ccel-commentary.py`.
- `hodge_rom` (archive.org `commentaryon1873hodg`), `hodge_cor` (`expositionoffirs00hodg`,
  `expositionofsecon00hodg`) and `owen_heb` chapters 1–5 (Goold edition, `worksofjohnowend0020owen`,
  `worksofjohnowend0021owen`) — public-domain scans' OCR text, converted by
  `tools/build-ocr-commentary.py`; expect occasional OCR errors.
- `haldane` — godrules.net HTML pages, converted by `tools/build-haldane-commentary.py`.

## Classic Writings

- 101 works by John Owen, Jonathan Edwards, Richard Baxter, John Bunyan, John Flavel, Thomas Watson,
  Stephen Charnock, Thomas Manton, Samuel Rutherford, William Guthrie, Thomas Boston, Thomas Shepard,
  John Howe, Matthew Mead, David Clarkson, John Cotton, Philip Doddridge, John Newton, George
  Whitefield, Samuel Hopkins and John Gill — public-domain ThML editions from the Christian Classics
  Ethereal Library (https://ccel.org), converted by `tools/build-ccel-classic.py`.
- 78 works by Thomas Brooks, Richard Sibbes, Thomas Goodwin, Jeremiah Burroughs, Joseph Alleine,
  William Perkins, William Ames, Samuel Bolton, Isaac Ambrose, George Swinnock, Stephen Charnock,
  Ralph Venning, John Flavel, James Janeway, Richard Baxter, John Preston, William Bridge, William
  Gouge, Christopher Love, Thomas Watson, Samuel Rutherford, James Ussher, Thomas Shepard, Thomas
  Hooker, William Gurnall, Walter Marshall and Thomas Doolittle — original 17th-century editions
  transcribed by EEBO-TCP and released under CC0 (https://github.com/textcreationpartnership),
  converted by `tools/build-tcp-classic.py`. The TCP id of each is shown in the reader.

Puritan Library (puritanlibrary.com) was used only as a reading list: its links lead to
Monergism's copyrighted e-book editions, which are not included.
