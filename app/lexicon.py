# app/lexicon.py

# English baseline
POS_WORDS = {
    "good","great","love","excellent","amazing","happy","like","awesome","nice","fantastic",
    "cool","dope","lit","fire","wonderful","satisfied","recommend","perfect","superb","fast","smooth",
    "delicious","tasty","fresh","crispy","affordable","clean"
}
NEG_WORDS = {
    "bad","terrible","hate","awful","sad","angry","dislike","poor","worst","boring",
    "trash","lame","broken","buggy","useless","disappointed","refund","slow","noisy","overpriced",
    "bland","stale","overcooked","dirty","rude","cold"
}

# Turkish minimal baseline 
POS_TR = {
    "iyi","harika","mükemmel","mukemmel","sevdim","bayıldım","bayildim","güzel","guzel","mutlu",
    "hızlı","hizli","temiz","lezzetli","taze","tavsiye","muhteşem","muhtesem","süper","super"
}
NEG_TR = {
    "kötü","kotu","berbat","nefret","rezalet","fena","yavaş","yavas","kirli","bayat",
    "pahalı","pahali","bozuk","kırık","kirik","gürültülü","gurultulu","iğrenç","igrenc"
}

# Language profiles: map short code to (POS, NEG) tuples
PROFILES = {
    "en": (POS_WORDS, NEG_WORDS),
    "tr": (POS_TR,   NEG_TR),
}
