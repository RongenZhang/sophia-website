"""
Hand-authored site copy (your voice).

This is the narrative text that is NOT pulled from the CV: the About bio, the
three research-stream descriptions, teaching course descriptions, and the
contact section. Edit freely — rebuilding from a new CV will NOT overwrite this.

The Publications, Awards, and Service *lists* are generated from your CV, so
those refresh automatically. This file is only for prose that changes rarely.
"""

SITE = {
    "name": "Rongen (Sophia) Zhang",
    "short_name": "Sophia Zhang",
    "title": "Assistant Professor of Business Analytics",
    "affiliation": "Hankamer School of Business, Baylor University",
    "email": "Sophia_Zhang@baylor.edu",
    "baylor_profile": "https://hankamer.baylor.edu/person/rongen-sophia-zhang",
    "linkedin": "https://www.linkedin.com/in/rongen-sophia-zhang/",
    "scholar": "https://scholar.google.com/citations?user=bMO81LYAAAAJ&hl=en",
}

# --- About -----------------------------------------------------------------
ABOUT = [
    "Rongen (Sophia) Zhang is an assistant professor in the Information Systems "
    "and Business Analytics Department at Baylor University. She earned her "
    "Ph.D. in Computer Information Systems at Georgia State University.",

    "Her research examines how emerging technologies shape individual "
    "decision-making, with a focus on decentralized governance, AI "
    "explainability, generative AI delegation, and technology-mediated user "
    "engagement. Her work has been published in respected outlets such as "
    "Information Systems Journal, Journal of Medical Internet Research, ACM "
    "Transactions on Management Information Systems, and Frontiers in "
    "Neuroscience. She has been recognized with the Best Associate Editor and "
    "Best Reviewer awards at the International Conference on Information Systems "
    "(ICIS).",

    "Though she strives to explore emerging phenomena with a "
    "methodology-agnostic view, her ongoing projects adopt experiments, "
    "econometric analysis, qualitative comparative analysis, and case study "
    "approaches.",

    "She values teaching as an opportunity to inspire and support students' "
    "success as wholesome individuals through engaging learning experiences.",
]

# --- Research streams ------------------------------------------------------
# 'image' is a file in assets/img/ (optional; leave "" for a text-only card).
RESEARCH_STREAMS = [
    {
        "title": "Decentralized Governance",
        "image": "stream-blockchain.jpg",
        "body":
            "This stream combines fsQCA and econometric analyses to uncover how "
            "platform design choices interact to produce distinct patterns of "
            "governance participation; how cryptocurrency incentive structures "
            "interact with portfolio power and status to influence user "
            "governance engagement; and how multi-dimensional decentralization "
            "shapes governance participation and long-term platform value. The "
            "work links practical design guidance for platform architects, "
            "drawing on theories of decentralization, commons governance, and "
            "value co-creation.",
    },
    {
        "title": "Explainable & Responsible AI",
        "image": "stream-ai.jpg",
        "body":
            "This stream examines how the type of AI explanation influences "
            "algorithm aversion and decision-making, particularly in healthcare "
            "contexts. Work in progress probes AI delegation, AI "
            "quasi-rationality, and AI affordances for cultural intelligence.",
    },
    {
        "title": "Technology, Emotion & Well-being",
        "image": "stream-wellbeing.jpg",
        "body":
            "A third line of work examines the impact of technology on emotion "
            "and well-being, including configurational analyses of technology "
            "engagement across ecological layers and the role of emotion in "
            "information security behaviors.",
    },
]

# --- Teaching (course descriptions; the term list comes from the CV) -------
TEACHING = [
    {
        "code": "MIS 4344 / 5342",
        "name": "Business Intelligence",
        "institution": "Baylor University",
        "body":
            "Business Intelligence (BI) is the discovery of patterns and "
            "relationships hidden in large amounts of data. This hands-on course "
            "provides practical analytical skills that apply in almost any "
            "workplace, exploring techniques for making intelligent business "
            "decisions in data-rich organizations. Students learn the basics of "
            "data manipulation, exploratory visualization, and common analytical "
            "algorithms using the R programming language to analyze real data "
            "sets and inform strategic and operational decisions.",
    },
    {
        "code": "CIS 4730",
        "name": "Unstructured Data Management",
        "institution": "Georgia State University",
        "body":
            "Over 90 percent of digital data is unstructured — much of it locked "
            "away across varied data stores, locations, and formats. This course "
            "discusses the issues and challenges of unstructured data "
            "management, and introduces best practices, underlying principles, "
            "and emerging technologies for storing, retrieving, and analyzing "
            "unstructured data.",
    },
]

# --- Contact ---------------------------------------------------------------
CONTACT = {
    "quote": "Alone we can do so little; together we can do so much.",
    "quote_author": "Helen Keller",
    # Set to a Formspree endpoint (e.g. "https://formspree.io/f/xxxx") to enable
    # a working contact form. Left blank -> a clean "Email me" button is shown.
    "formspree_endpoint": "",
}
