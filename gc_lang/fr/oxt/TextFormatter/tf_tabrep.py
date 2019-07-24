# Regular expressions for the text formatter of LO
# working with ICU (bag of bugs)


# ICU: & is $0 in replacement field

# NOTE: A LOT OF REGEX COULD BE MERGED IF ICU ENGINE WAS NOT SO BUGGY
# "([;?!…])(?=[:alnum:])" => "$1 " doesn’t work properly
# "(?<=[:alnum:])([;?!…])" => " $1 " doesn’t work properly



#
#                   String to replace                   replacement     regex?  case sensitive?
#

dTableRepl = {
    # Restructuration
    "struct1": [
                    ("\\n",                             "\\n",          True,   True)   # end of line => end of paragraph
    ],
    "struct2": [
                    ("([:alpha:])- *\n([:alpha:])",     "$1$2",         True,   False)  # EOL
    ],

    # espaces surnuméraires
    "ssp1": [
                    ("^[  ]+",                          "",             True,   True)
    ],
    "ssp2": [
                    ("  ",                              " ",            False,  True),  # espace + espace insécable -> espace
                    ("  ",                              " ",            False,  True),  # espace insécable + espace -> espace
                    ("  +",                             " ",            True,   True),  # espaces surnuméraires
                    ("  +",                             " ",            True,   True)   # espaces insécables surnuméraires
    ],
    "ssp3": [
                    ("[  ]+$",                          "",             True,   True)
    ],
    "ssp4": [
                    (" +(?=[.,…])",                     "",             True,   True)
    ],
    "ssp5": [
                    ("\\([  ]+",                        "(",            True,   True),
                    ("[  ]+\\)",                        ")",            True,   True)
    ],
    "ssp6": [
                    ("\\[[  ]+",                        "[",            True,   True),
                    ("[  ]+\\]",                        "]",            True,   True)
    ],
    "ssp7": [
                    ("“[  ]+",                          "“",            True,   True),
                    ("[  ]”",                           "”",            True,   True)
    ],

    # espaces insécables
    "nbsp1": [
                    ("(?<=[:alnum:]):[   ]",            " : ",          True,   False),
                    ("(?<=[:alnum:]):$",                " :",           True,   False),
                    ("(?<=[:alnum:]);",                 " ;",           True,   False),
                    ("(?<=[:alnum:])[?][   ]",          " ? ",          True,   False),
                    ("(?<=[:alnum:])[?]$",              " ?",           True,   False),
                    ("(?<=[:alnum:])!",                 " !",           True,   False),
                    ("(?<=[]…)»}]):",                   " :",           True,   False),
                    ("(?<=[]…)»}]);",                   " ;",           True,   False),
                    ("(?<=[]…)»}])[?][   ]",            " ? ",          True,   False),
                    ("(?<=[]…)»}])[?]$",                " ?",           True,   False),
                    ("(?<=[]…)»}])!",                   " !",           True,   False),
                    ("[  ]+([:;?!])",                   " $1",          True,   False)
    ],
    "nnbsp1": [
                    ("(?<=[:alnum:]);",                 " ;",           True,   False),
                    ("(?<=[:alnum:])[?][   ]",          " ? ",          True,   False),
                    ("(?<=[:alnum:])[?]$",              " ?",           True,   False),
                    ("(?<=[:alnum:])!",                 " !",           True,   False),
                    ("(?<=[]…)»}]);",                   " ;",           True,   False),
                    ("(?<=[]…)»}])[?][   ]",            " ? ",          True,   False),
                    ("(?<=[]…)»}])[?]$",                " ?",           True,   False),
                    ("(?<=[]…)»}])!",                   " !",           True,   False),
                    ("[  ]+([;?!])",                    " $1",          True,   False),
                    ("(?<=[:alnum:]):[   ]",            " : ",          True,   False),
                    ("(?<=[:alnum:]):$",                " :",           True,   False),
                    ("(?<=[]…)»}]):",                   " :",           True,   False),
                    ("[  ]+:",                          " :",           True,   False)
    ],
    "nbsp1_fix": [
                    ("([[(])[   ]([!?:;])",             "$1$2",         True,   False),
                    ("(?<=http)[   ]://",               "://",          True,   False),
                    ("(?<=https)[   ]://",              "://",          True,   False),
                    ("(?<=ftp)[   ]://",                "://",          True,   False),
                    ("(?<=&)amp[   ];",                 "amp;",         True,   False),
                    ("(?<=&)nbsp[   ];",                "nbsp;",        True,   False),
                    ("(?<=&)lt[   ];",                  "lt;",          True,   False),
                    ("(?<=&)gt[   ];",                  "gt;",          True,   False),
                    ("(?<=&)apos[   ];",                "apos;",        True,   False),
                    ("(?<=&)quot[   ];",                "quot;",        True,   False),
                    ("(?<=&)thinsp[   ];",              "thinsp;",      True,   False)
    ],
    "nbsp2": [
                    ("«(?=[:alnum:])",                  "« ",           True,   False),
                    ("«[  ]+",                          "« ",           True,   False),
                    ("(?<=[:alnum:]|[.!?])»",           " »",           True,   False),
                    ("[  ]+»",                          " »",           True,   False)
    ],
    "nnbsp2": [
                    ("«(?=[:alnum:])",                  "« ",           True,   False),
                    ("«[  ]+",                          "« ",           True,   False),
                    ("(?<=[:alnum:]|[.!?])»",           " »",           True,   False),
                    ("[  ]+»",                          " »",           True,   False)
    ],
    "nbsp3": [
                    ("([:digit:])([%‰€$£¥˚℃])",         "$1 $2",        True,   True),
                    ("([:digit:]) ([%‰€$£¥˚℃])",        "$1 $2",        True,   True),
    ],
    "nbsp4": [
                    ("([:digit:])[  ]([:digit:])",      "$1 $2",        True,   True)
    ],
    "nnbsp4": [
                    ("([:digit:])[  ]([:digit:])",      "$1 $2",        True,   True)
    ],
    "nbsp5": [
                    ("(?<=[0-9⁰¹²³⁴⁵⁶⁷⁸⁹]) ?([kcmµnd]?(?:[slgJKΩΩℓ]|m[²³]?|Wh?|Hz|dB)|[%‰]|°C)\\b", " $1", True, True)
    ],
    "nbsp6": [
                    ("M(mes?|ᵐᵉˢ?|grs?|ᵍʳˢ?|lles?|ˡˡᵉˢ?|rs?|ʳˢ?|M\\.) ", "M$1 ",     True,   True),
                    ("D(re?s?|ʳᵉ?ˢ?) ",                                  "D$1 ",     True,   True),
                    ("P(re?s?|ʳᵉ?ˢ?) ",                                  "P$1 ",     True,   True),
                    ("V(ves?|ᵛᵉˢ?) ",                                    "V$1 ",     True,   True),
    ],

    # espaces manquants
    "space1": [
                    (";(?=[:alnum:])",                  "; ",           True,   True),
                    ("\\?(?=[A-ZÉÈÊÂÀÎ])",              "? ",           True,   True),
                    ("!(?=[:alnum:])",                  "! ",           True,   True),
                    ("…(?=[:alnum:])",                  "… ",           True,   True),
                    ("\\.(?=[A-ZÉÈÎ][:alpha:])",        ". ",           True,   True),
                    ("\\.(?=À)",                        ". ",           True,   True),
                    (",(?=[:alpha:])",                  ", ",           True,   True),
                    ("([:alpha:]),([0-9])",             "$1, $2",       True,   True),
                    (":(?=[:alpha:])",                  ": ",           True,   True)
    ],
    "space1_fix": [
                    ("(?<=DnT), w\\b",                  ",w",           True,   True),
                    ("(?<=DnT), A\\b",                  ",A",           True,   True)
    ],
    "space2": [
                    (" -(?=[:alpha:]|[\"«“'‘])",        " - ",          True,   False),
                    (" –(?=[:alpha:]|[\"«“'‘])",        " – ",          True,   False), # demi-cadratin
                    (" —(?=[:alpha:]|[\"«“'‘])",        " — ",          True,   False), # cadratin
                    ("(?<=[:alpha:])– ",                " – ",          True,   False),
                    ("(?<=[:alpha:])— ",                " — ",          True,   False),
                    ("(?<=[:alpha:])- ",                " - ",          True,   False),
                    ("(?<=[\"»”'’])– ",                 " – ",          True,   False),
                    ("(?<=[\"»”'’])— ",                 " — ",          True,   False),
                    ("(?<=[\"»”'’])- ",                 " - ",          True,   False)
    ],

    # Suppressions
    "delete1": [
                    ("­",                               "",             False,  True)
    ],

    # Signes typographiques
    "typo1": [
                    ("\\bl['´‘′`](?=[:alnum:])",        "l’",           True,   True),
                    ("\\bj['´‘′`](?=[:alnum:])",        "j’",           True,   True),
                    ("\\bm['´‘′`](?=[:alnum:])",        "m’",           True,   True),
                    ("\\bt['´‘′`](?=[:alnum:])",        "t’",           True,   True),
                    ("\\bs['´‘′`](?=[:alnum:])",        "s’",           True,   True),
                    ("\\bc['´‘′`](?=[:alnum:])",        "c’",           True,   True),
                    ("\\bd['´‘′`](?=[:alnum:])",        "d’",           True,   True),
                    ("\\bn['´‘′`](?=[:alnum:])",        "n’",           True,   True),
                    ("\\bç['´‘′`](?=[:alnum:])",        "ç’",           True,   True),
                    ("\\bL['´‘′`](?=[:alnum:])",        "L’",           True,   True),
                    ("\\bJ['´‘′`](?=[:alnum:])",        "J’",           True,   True),
                    ("\\bM['´‘′`](?=[:alnum:])",        "M’",           True,   True),
                    ("\\bT['´‘′`](?=[:alnum:])",        "T’",           True,   True),
                    ("\\bS['´‘′`](?=[:alnum:])",        "S’",           True,   True),
                    ("\\bC['´‘′`](?=[:alnum:])",        "C’",           True,   True),
                    ("\\bD['´‘′`](?=[:alnum:])",        "D’",           True,   True),
                    ("\\bN['´‘′`](?=[:alnum:])",        "N’",           True,   True),
                    ("\\bÇ['´‘′`](?=[:alnum:])",        "Ç’",           True,   True),
                    ("(qu|jusqu|lorsqu|puisqu|quoiqu|quelqu|presqu|entr|aujourd|prud)['´‘′`]", "$1’", True, False)
    ],
    "typo2": [
                    ("...",                             "…",            False,  True),
                    ("(?<=…)[.][.]",                    "…",            True,   True),
                    ("…[.](?![.])",                     "…",            True,   True)
    ],
    "typo3a": [     # cadratin
                    (" - ",                             " — ",          False,  True),
                    (" – ",                             " — ",          False,  True),
                    (" -,",                             " —,",          False,  True),
                    (" –,",                             " —,",          False,  True)
    ],
    "typo3b": [     # demi-cadratin
                    (" - ",                             " – ",          False,  True),
                    (" — ",                             " – ",          False,  True),
                    (" -,",                             " –,",          False,  True),
                    (" —,",                             " –,",          False,  True)
    ],
    "typo4a": [     # cadratin
                    ("^-[  ]",                          "— ",           True,   True),
                    ("^–[  ]",                          "— ",           True,   True),
                    ("^— ",                             "— ",           True,   True),
                    ("^«[  ][—–-][  ]",                 "« — ",         True,   True),
                    ("^[-–—](?=[:alnum:])",             "— ",           True,   False),
                    ("^[-–—](?=[.…])",                  "— ",           True,   True)
    ],
    "typo4b": [     # demin-cadratin
                    ("^-[  ]",                          "– ",           True,   True),
                    ("^—[  ]",                          "– ",           True,   True),
                    ("^– ",                             "– ",           True,   True),
                    ("^«[  ][—–-][  ]",                 "« – ",         True,   True),
                    ("^[-–—](?=[:alnum:])",             "– ",           True,   False),
                    ("^[-–—](?=[.…])",                  "– ",           True,   True)
    ],
    "typo5": [
                    ('"([:alpha:]+)"',                      "“$1”",         True,   False),
                    ("''([:alpha:]+)''",                    "“$1”",         True,   False),
                    ("'([:alpha:]+)'",                      "“$1”",         True,   False),
                    ('^"(?=[:alnum:])',                     "« ",           True,   False),
                    ("^''(?=[:alnum:])",                    "« ",           True,   False),
                    (' "(?=[:alnum:])',                     " « ",          True,   False),
                    (" ''(?=[:alnum:])",                    " « ",          True,   False),
                    ('\\("(?=[:alnum:])',                   "(« ",          True,   False),
                    ("\\(''(?=[:alnum:])",                  "(« ",          True,   False),
                    ('(?<=[:alnum:])"$',                    " »",           True,   False),
                    ("(?<=[:alnum:])''$",                   " »",           True,   False),
                    ('(?<=[:alnum:])"(?=[] ,.:;?!…)])',     " »",           True,   False),
                    ("(?<=[:alnum:])''(?=[] ,.:;?!…)])",    " »",           True,   False),
                    ('(?<=[.!?…])" ',                       " » ",          True,   False),
                    ('(?<=[.!?…])"$',                       " »",           True,   False)
    ],
    "typo6": [
                    ("\\bN\\.([ms])\\b",                    "N·$1",         True,   True),  # N·m et N·m-1, N·s
                    ("\\bW\\.h\\b",                         "W·h",          True,   True),
                    ("\\bPa\\.s\\b",                        "Pa·s",         True,   True),
                    ("\\bA\\.h\\b",                         "A·h",          True,   True),
                    ("\\bΩ\\.m\\b",                         "Ω·m",          True,   True),
                    ("\\bS\\.m\\b",                         "S·m",          True,   True),
                    ("\\bg\\.s(?=-1)\\b",                   "g·s",          True,   True),
                    ("\\bm\\.s(?=-[12])\\b",                "m·s",          True,   True),
                    ("\\bg\\.m(?=2|-3)\\b",                 "g·m",          True,   True),
                    ("\\bA\\.m(?=-1)\\b",                   "A·m",          True,   True),
                    ("\\bJ\\.K(?=-1)\\b",                   "J·K",          True,   True),
                    ("\\bW\\.m(?=-2)\\b",                   "W·m",          True,   True),
                    ("\\bcd\\.m(?=-2)\\b",                  "cd·m",         True,   True),
                    ("\\bC\\.kg(?=-1)\\b",                  "C·kg",         True,   True),
                    ("\\bH\\.m(?=-1)\\b",                   "H·m",          True,   True),
                    ("\\bJ\\.kg(?=-1)\\b",                  "J·kg",         True,   True),
                    ("\\bJ\\.m(?=-3)\\b",                   "J·m",          True,   True),
                    ("\\bm[2²]\\.s\\b",                     "m²·s",         True,   True),
                    ("\\bm[3³]\\.s(?=-1)\\b",               "m³·s",         True,   True),
                    #("\\bJ.kg-1.K-1\\b",                   "J·kg-1·K-1",   True,   True),
                    #("\\bW.m-1.K-1\\b",                    "W·m-1·K-1",    True,   True),
                    #("\\bW.m-2.K-1\\b",                    "W·m-2·K-1",    True,   True),
                    ("(Y|Z|E|P|T|G|M|k|h|da|d|c|m|µ|n|p|f|a|z|y)Ω", "$1Ω", True, True)
    ],
    "typo7": [
                    # ligatures: pas de majuscules
                    ("coeur",                               "cœur",         False,  True),
                    ("coel([aeio])",                        "cœl$1",        True,   True),
                    ("choeur",                              "chœur",        False,  True),
                    ("foet",                                "fœt",          False,  True),
                    ("oeil",                                "œil",          False,  True),
                    ("oeno",                                "œno",          False,  True),
                    ("oesoph",                              "œsoph",        False,  True),
                    ("oestro",                              "œstro",        False,  True),
                    ("oeuf",                                "œuf",          False,  True),
                    ("oeuvr",                               "œuvr",         False,  True),
                    ("moeur",                               "mœur",         False,  True),
                    ("noeu",                                "nœu",          False,  True),
                    ("soeur",                               "sœur",         False,  True),
                    ("voeu",                                "vœu",          False,  True),
                    ("aequo",                               "æquo",         False,  True),
                    # ligatures: majuscules
                    ("Coeur",                               "Cœur",         False,  True),
                    ("Coel([aeio])",                        "Cœl$1",        True,   True),
                    ("Choeur",                              "Chœur",        False,  True),
                    ("Foet",                                "Fœt",          False,  True),
                    ("Oeil",                                "Œil",          False,  True),
                    ("Oeno",                                "Œno",          False,  True),
                    ("Oesoph",                              "Œsoph",        False,  True),
                    ("Oestro",                              "Œstro",        False,  True),
                    ("Oeuf",                                "Œuf",          False,  True),
                    ("Oeuvr",                               "Œuvr",         False,  True),
                    ("Moeur",                               "Mœur",         False,  True),
                    ("Noeu",                                "Nœu",          False,  True),
                    ("Soeur",                               "Sœur",         False,  True),
                    ("Voeu",                                "Vœu",          False,  True),
                    ("Aequo",                               "Æquo",         False,  True),
                    # mots communs avec diacritiques manquants
                    ("\\bCa\\b",                            "Ça",           True,   True),
                    (" ca\\b",                              " ça",          True,   True),
                    ("\\bdej[aà]\\b",                       "déjà",         True,   True),
                    ("\\bDej[aà]\\b",                       "Déjà",         True,   True),
                    ("\\bplutot\\b",                        "plutôt",       True,   True),
                    ("\\bPlutot\\b",                        "Plutôt",       True,   True),
                    ("\\b(ce(?:ux|lles?|lui))-la\\b",       "$1-là",        True,   True),
                    ("\\b(Ce(?:ux|lles?|lui))-la\\b",       "$1-là",        True,   True),
                    ("\\bmalgre\\b",                        "malgré",       True,   True),
                    ("\\bMalgre\\b",                        "Malgré",       True,   True),
                    ("\\betre\\b",                          "être",         True,   True),
                    ("\\bEtre\\b",                          "Être",         True,   True),
                    ("\\btres\\b",                          "très",         True,   True),
                    ("\\bTres\\b",                          "Très",         True,   True),
                    ("\\bEtai([ts]|ent)\\b",                "Étai$1",       True,   True),
                    ("\\bE(tat|cole|crit|poque|tude|ducation|glise|conomi(?:qu|)e|videmment|lysée|tienne|thiopie|cosse|gypt(?:e|ien)|rythrée|pinal|vreux)", "É$1", True, True)
    ],
    # faire ligatures
    "typo_ffi_do": [
                    ("ffi",                                 "ﬃ",            False,  True)
    ],
    "typo_ffl_do": [
                    ("ffl",                                 "ﬄ",            False,  True)
    ],
    "typo_fi_do": [
                    ("fi",                                  "ﬁ",            False,  True)
    ],
    "typo_fl_do": [
                    ("fl",                                  "ﬂ",            False,  True)
    ],
    "typo_ff_do": [
                    ("ff",                                  "ﬀ",            False,  True)
    ],
    "typo_ft_do": [
                    ("ft",                                  "ﬅ",            False,  True)
    ],
    "typo_st_do": [
                    ("st",                                  "ﬆ",            False,  True)
    ],
    # défaire ligatures
    "typo_fi_undo": [
                    ("ﬁ",                                   "fi",           False,  True)
    ],
    "typo_fl_undo": [
                    ("ﬂ",                                   "fl",           False,  True)
    ],
    "typo_ff_undo": [
                    ("ﬀ",                                   "ff",           False,  True)
    ],
    "typo_ff_undo": [
                    ("ﬃ",                                   "ffi",          False,  True)
    ],
    "typo_ff_undo": [
                    ("ﬄ",                                   "ffl",          False,  True)
    ],
    "typo_ft_undo": [
                    ("ﬅ",                                   "ft",           False,  True)
    ],
    "typo_st_undo": [
                    ("ﬆ",                                   "st",           False,  True)
    ],

    # Divers
    "misc1a": [
                    ("(?<=\\b[0-9][0-9][0-9][0-9])(i?[èe]me|è|e)\\b",           "ᵉ",    True, False),
                    ("(?<=\\b[0-9][0-9][0-9])(i?[èe]me|è|e)\\b",                "ᵉ",    True, False),
                    ("(?<=\\b[0-9][0-9])(i?[èe]me|è|e)\\b",                     "ᵉ",    True, False),
                    ("(?<=\\b[0-9])(i?[èe]me|è|e)\\b",                          "ᵉ",    True, False),
                    ("(?<=\\b[XVICL][XVICL][XVICL][XVICL])(i?[èe]me|è|e)\\b",   "ᵉ",    True, True),
                    ("(?<=\\b[XVICL][XVICL][XVICL])(i?[èe]me|è|e)\\b",          "ᵉ",    True, True),
                    ("(?<=\\b[XVICL][XVICL])(i?[èe]me|è|e)\\b",                 "ᵉ",    True, True),
                    ("(?<=\\b[XVICL])(i?[èe]me|è)\\b",                          "ᵉ",    True, True),
                    ("(?<=\\b(au|l[ea]|du) [XVICL])e\\b",                       "ᵉ",    True, True),
                    ("(?<=\\b[XVI])e(?= siècle)",                               "ᵉ",    True, True),
                    ("(?<=\\b[1I])er\\b",                                       "ᵉʳ",   True, True),
                    ("(?<=\\b[1I])re\\b",                                       "ʳᵉ",   True, True)
    ],
    "misc1b": [
                    ("(?<=\\b[0-9][0-9][0-9][0-9])(i?[èe]me|è|ᵉ)\\b",           "e",    True, False),
                    ("(?<=\\b[0-9][0-9][0-9])(i?[èe]me|è|ᵉ)\\b",                "e",    True, False),
                    ("(?<=\\b[0-9][0-9])(i?[èe]me|è|ᵉ)\\b",                     "e",    True, False),
                    ("(?<=\\b[0-9])(i?[èe]me|è|ᵉ)\\b",                          "e",    True, False),
                    ("(?<=\\b[XVICL][XVICL][XVICL][XVICL])(i?[èe]me|è|ᵉ)\\b",   "e",    True, True),
                    ("(?<=\\b[XVICL][XVICL][XVICL])(i?[èe]me|è|ᵉ)\\b",          "e",    True, True),
                    ("(?<=\\b[XVICL][XVICL])(i?[èe]me|è|ᵉ)\\b",                 "e",    True, True),
                    ("(?<=\\b[XVICL])(i?[èe]me|è|ᵉ)\\b",                        "e",    True, True),
                    ("(?<=\\b[1I])ᵉʳ\\b",                                       "er",   True, True),
                    ("(?<=\\b[1I])ʳᵉ\\b",                                       "re",   True, True)
    ],
    "misc2": [
                    ("etc(…|[.][.][.]?)",                       "etc.",         True,   True),
                    ("(?<!,) etc[.]",                           ", etc.",       True,   True)
    ],
    "misc3": [
                    ("[ -]t[’'](?=il\\b|elle|on\\b)",           "-t-",          True,   True),
                    (" t-(?=il|elle|on)",                       "-t-",          True,   True),
                    ("[ -]t[’'-](?=ils|elles)",                 "-",            True,   True),
                    ("(?<=[td])-t-(?=il|elle|on)",              "-",            True,   True),
                    (" ce(lles?|lui|ux) (ci|là)\\b",            " ce$1-$2",     True,   True),
                    ("Ce(lles?|lui|ux) (ci|là)\\b",             "Ce$1-$2",      True,   True),
                    (" dix (sept|huit|neuf)",                   " dix-$1",      True,   True),
                    ("Dix (sept|huit|neuf)",                    "Dix-$1",       True,   True),
                    ("quatre vingt",                            "quatre-vingt", False,  True),
                    ("Quatre vingt",                            "Quatre-vingt", False,  True),
                    ("(soixante|quatre-vingt) (deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|treize|quatorze|quinze|seize|dix-sept|dix-huit|dix-neuf)", "$1-$2", True, False),
                    ("(vingt|trente|quarante|cinquante) (deux|trois|quatre|cinq|six|sept|huit|neuf)", "$1-$2", True, False),
                    (" ci (joint|desso?us|contre|devant|avant|après|incluse|g[îi]t|gisent)", " ci-$1", True, True),
                    ("Ci (joint|desso?us|contre|devant|avant|après|incluse|g[îi]t|gisent)", "Ci-$1", True, True),
                    (" vis à vis\\b",                           "vis-à-vis",    False,  True),
                    ("Vis à vis\\b",                            "Vis-à-vis",    False,  True),
                    ("week end",                                "week-end",     False,  True),
                    ("Week end",                                "Week-end",     False,  True),
                    ("(plus|moins) value",                      "$1-value",     True,   False),
    ],
    "misc5a": [
                    ("(qu|lorsqu|puisqu|quoiqu|presqu|jusqu|aujourd|entr|quelqu) ", "$1’", True, True),
    ],
    "misc5b": [
                    ("\\bj (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "j’",           True,   True),
                    ("\\bn (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "n’",           True,   True),
                    ("\\bm (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "m’",           True,   True),
                    ("\\bt (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "t’",           True,   True),
                    ("\\bs (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "s’",           True,   True),
                    ("\\bc (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "c’",           True,   True),
                    ("\\bç (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "ç’",           True,   True),
                    ("\\bl (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "l’",           True,   True),
                    ("\\bd (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "d’",           True,   True)
    ],
    "misc5c": [
                    ("\\bJ (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "J’",           True,   True),
                    ("\\bN (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "N’",           True,   True),
                    ("\\bM (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "M’",           True,   True),
                    ("\\bT (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "T’",           True,   True),
                    ("\\bS (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "S’",           True,   True),
                    ("\\bC (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "C’",           True,   True),
                    ("\\bÇ (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "Ç’",           True,   True),
                    ("\\bL (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "L’",           True,   True),
                    ("\\bD (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])",     "D’",           True,   True)
    ]
}
