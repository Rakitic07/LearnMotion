"""Foundational lesson catalogs for music, theory, and instrument subjects."""

from ._dsl import chain, ex, qa, topic

TRACKS = {
    "guitar": {
        "prefix": "GTR", "label": "guitar", "analogy": "A guitar is a small orchestra: each string is a voice, and the frets let you choose its notes.",
        "groups": [
            ("Instrument & Setup", "sky", ["Parts of the Guitar", "Acoustic, Classical & Electric", "How Strings Make Sound", "String Names: E A D G B E", "Tune by Ear and with a Tuner", "Posture, Strap Height & Balance", "Left-Hand Thumb Position", "Fretting Behind the Fret", "Pick Grip & Pick Angle", "Care, Storage & Changing Strings"]),
            ("Reading & Rhythm", "mint", ["String and Fret Numbers", "Read Guitar Tablature", "Tab Rhythm and Note Lengths", "The Five-Line Staff for Guitar", "Treble Clef and Guitar Octave", "Beat, Tempo & Metronome", "Quarter, Eighth & Sixteenth Notes", "Rests, Ties & Dotted Notes", "Time Signatures in Guitar Parts", "Count In and Keep a Steady Pulse"]),
            ("Chords & Harmony", "peach", ["Open Chord Shapes", "E Major and E Minor", "A Major and A Minor", "D Major and D Minor", "C and G Major Chords", "Change Chords Without Pausing", "Chord Diagrams and Finger Numbers", "Power Chords", "Barre Chord Foundations", "Common I–V–vi–IV Progression"]),
            ("Technique & Vocabulary", "lilac", ["Downstrokes and Upstrokes", "Strumming Patterns", "Mute Unwanted Strings", "Clean Chord Transitions", "Alternate Picking", "Single-Note Riffs", "Major Scale on One String", "Pentatonic Scale Shape", "Hammer-ons and Pull-offs", "Slides, Bends & Vibrato"]),
            ("Musicianship & Performance", "rose", ["Play in Time with a Metronome", "Dynamics: Soft and Loud", "Articulation and Note Length", "Read a Lead Sheet", "Capo and Transposition", "Use a Loop for Practice", "Learn a Song in Sections", "Play with a Backing Track", "Basic Improvisation", "Perform, Record & Review"]),
        ],
    },
    "theory": {
        "prefix": "MTH", "label": "music theory", "analogy": "Music theory is a map of listening patterns: it names the relationships musicians already hear.",
        "groups": [
            ("Sound & Pitch", "sky", ["What Music Theory Describes", "Sound, Frequency & Pitch", "Pitch Names A Through G", "Octaves and Enharmonic Notes", "The Keyboard as a Pitch Map", "Whole Steps and Half Steps", "Accidentals: Sharp, Flat & Natural", "Intervals by Number", "Interval Quality: Major & Perfect", "Hear and Name Simple Intervals"]),
            ("Scales, Keys & Melody", "mint", ["The Major Scale Formula", "Natural Minor Scale", "Major and Relative Minor Keys", "Scale Degrees and Tonic", "Key Signatures", "Circle of Fifths", "Minor Scale Variants", "Modes: A First Look", "Pentatonic and Blues Scales", "Build a Singable Melody"]),
            ("Chords & Harmony", "peach", ["Build a Triad in Thirds", "Major, Minor, Diminished & Augmented", "Inversions and Chord Spelling", "Diatonic Chords in a Major Key", "Roman Numeral Analysis", "Seventh Chords", "Common Chord Progressions", "Tonic, Predominant & Dominant", "Cadences and Musical Punctuation", "Voice Leading Between Chords"]),
            ("Rhythm & Form", "lilac", ["Pulse, Beat & Tempo", "Note Values and Rests", "Simple Meter: 2/4, 3/4 & 4/4", "Compound Meter: 6/8", "Subdivision and Syncopation", "Ties, Dots & Tuplets", "Anacrusis and Pickup Notes", "Motif, Phrase & Period", "Binary, Ternary & Rondo Forms", "Repetition, Contrast & Development"]),
            ("Expression & Listening", "rose", ["Dynamics and Gradual Change", "Articulation and Phrasing", "Timbre and Instrument Families", "Texture: Monophonic to Polyphonic", "Consonance, Dissonance & Tension", "Harmonic Rhythm", "Melody and Bass Relationships", "Transposition and Concert Pitch", "Listen for Form and Harmony", "Analyze a Short Piece by Ear"]),
        ],
    },
    "drums": {
        "prefix": "DRM", "label": "drums", "analogy": "The drum kit is a team of voices: each limb keeps an independent part while sharing one pulse.",
        "groups": [
            ("Kit, Safety & Setup", "sky", ["Parts of a Drum Kit", "Set Up the Kit for Your Body", "Drumstick Types and Balance", "Matched Grip Foundations", "Traditional Grip Overview", "Safe Volume and Hearing Protection", "Tune a Snare and Toms", "Kick Pedal Setup", "Cymbal Height and Angle", "Care for Heads, Sticks & Hardware"]),
            ("Pulse, Reading & Coordination", "mint", ["Find the Pulse and Count Aloud", "Quarter-Note Rock Beat", "Read a Basic Drum Chart", "Drum Notation: Lines and Spaces", "Count Eighth-Note Subdivisions", "Sixteenth-Note Counting", "Simple Meter and Bar Lines", "Rests and Tied Notes", "Keep Time with a Metronome", "Coordinate Hands and Feet Slowly"]),
            ("Strokes & Rudiments", "peach", ["Full, Down, Tap & Up Strokes", "Single-Stroke Roll", "Double-Stroke Roll", "Single Paradiddle", "Flam and Grace Notes", "Drag and Multiple Bounce", "Accent and Tap Control", "Moeller Motion Introduction", "Practice Rudiments Around the Kit", "Build Speed Without Tension"]),
            ("Grooves, Fills & Styles", "lilac", ["Kick, Snare & Hi-Hat Roles", "The Backbeat on Two and Four", "Open and Closed Hi-Hat", "Add the Bass Drum to a Groove", "Sixteenth-Note Hi-Hat Patterns", "Ghost Notes and Dynamics", "Simple Rock Fills", "Move Fills Across Toms", "Shuffle and Triplet Feel", "Funk, Pop, Jazz & Latin Overview"]),
            ("Musicianship & Performance", "rose", ["Count In and End a Song", "Play with a Click Track", "Follow a Bandleader", "Listen for Verse and Chorus", "Dynamic Shape Across a Song", "Use Space and Avoid Overplaying", "Recover Smoothly After a Mistake", "Practice with a Backing Track", "Record and Evaluate Your Time", "Build a Balanced Practice Session"]),
        ],
    },
    "violin": {
        "prefix": "VIO", "label": "violin", "analogy": "The violin turns small changes in bow speed, pressure, and contact point into expressive sound.",
        "groups": [
            ("Instrument & Healthy Setup", "sky", ["Parts of the Violin and Bow", "Violin, Viola & String Family", "Fit the Shoulder Rest", "Balanced Standing and Sitting Posture", "Hold the Violin Without Squeezing", "Bow Parts: Hair, Stick & Frog", "Rosin and Bow Care", "Name the Four Strings", "Tune Safely with Fine Tuners", "Store and Carry the Instrument"]),
            ("Bow, Sound & Rhythm", "mint", ["Hold the Bow with a Relaxed Hand", "Open-String Bow Strokes", "Straight Bow and Contact Point", "Bow Speed, Weight & Sound", "Whole, Half & Quarter Bows", "Down-Bow and Up-Bow Symbols", "Count Pulse While Playing", "Read Basic Violin Rhythms", "Rests, Ties & Dotted Notes", "Metronome Practice for Beginners"]),
            ("Fingering & Reading", "peach", ["Open Strings: G D A E", "Left-Hand Shape and Frame", "Finger Numbers 1 Through 4", "First-Position Finger Patterns", "Place Fingers by Listening", "Read the Treble Clef", "Find Notes on the Staff", "Natural, Sharp & Flat Notes", "Simple One-Octave Scales", "Intonation and Drone Practice"]),
            ("Technique & Repertoire", "lilac", ["Smooth String Crossings", "Detaché Bowing", "Legato and Slur Groups", "Staccato at a Comfortable Tempo", "Two-Octave Scale Foundations", "Arpeggios and Broken Chords", "Vibrato: Preparation and Release", "Shifting Beyond First Position", "Sight-Read a Short Phrase", "Learn a Piece in Small Sections"]),
            ("Musicianship & Performance", "rose", ["Dynamics and Bow Distribution", "Shape a Musical Phrase", "Listen and Tune with a Drone", "Play with a Piano or Recording", "Ensemble Listening and Blend", "Follow a Conductor", "Tune Before a Rehearsal", "Manage Nerves and Start Clearly", "Record a Practice Take", "Maintain a Safe Practice Routine"]),
        ],
    },
    "piano": {
        "prefix": "PNO", "label": "piano", "analogy": "The piano lays melody and harmony under both hands, making musical structure visible across the keys.",
        "groups": [
            ("Keyboard & Setup", "sky", ["Parts of an Acoustic and Digital Piano", "Keyboard Groups of Two and Three Black Keys", "Find Middle C and Octave C's", "Bench Height and Distance", "Relaxed Shoulders and Arm Weight", "Finger Numbers for Both Hands", "Curved Fingers and Hand Shape", "Pedal Names and Basic Foot Position", "Touch, Key Weight & Sound", "Care, Volume & Listening Safety"]),
            ("Notation, Pulse & Reading", "mint", ["The Grand Staff", "Treble Clef Note Names", "Bass Clef Note Names", "Middle C Across the Staves", "Ledger Lines and Landmark Notes", "Note Values and Rests", "Time Signatures and Bar Lines", "Count Eighth Notes and Subdivisions", "Ties, Dots & Slurs", "Sight-Read with a Steady Pulse"]),
            ("Scales, Chords & Harmony", "peach", ["C Major Five-Finger Pattern", "Major Scale: Whole and Half Steps", "Natural Minor Scale", "Key Signatures at the Keyboard", "Build Major and Minor Triads", "Chord Inversions", "Primary Chords: I, IV & V", "Broken Chords and Arpeggios", "Seventh Chords Introduction", "Left-Hand Bass Patterns"]),
            ("Technique & Coordination", "lilac", ["Play Hands Separately First", "Coordinate Simple Hands-Together Parts", "Finger Independence and Control", "Legato and Detached Touch", "Scale Fingering Choices", "Crossing the Thumb Smoothly", "Pedal Changes with Harmony", "Balance Melody Above Accompaniment", "Repeated Notes Without Tension", "Practice Slow, Even Repetition"]),
            ("Musicianship & Repertoire", "rose", ["Phrase Shape and Breathing", "Dynamics from Piano to Forte", "Articulation and Musical Style", "Listen for Melody and Bass", "Read a Lead Sheet", "Accompany a Singer or Instrument", "Learn a Piece in Sections", "Memory and Performance Preparation", "Improvise on a Five-Finger Scale", "Record and Reflect on a Performance"]),
        ],
    },
    "voice": {
        "prefix": "VOC", "label": "singing and voice", "analogy": "Vocal technique is like balancing breath, vibration, and resonance: small, comfortable adjustments change the sound without forcing it.",
        "groups": [
            ("Voice Foundations & Healthy Practice", "sky", ["How the Singing Voice Works", "Chest Voice: Sensation and Sound", "Head Voice: Sensation and Sound", "Chest Voice and Head Voice Compared", "Breath Flow and Phrase Length", "Gentle Vocal Warm-Ups", "Posture Without Stiffness", "Pitch Matching by Ear", "Vowels and Clear Diction", "Rest, Hydration and Vocal Load"]),
            ("Registers, Range & Resonance", "mint", ["Mixed Voice: A Coordinated Transition", "Passaggio: Moving Between Registers", "Register Breaks and Smooth Transitions", "Resonance Versus Vocal Placement", "Falsetto and Head Voice: A Careful Comparison", "Explore Range Without Pushing", "Descending and Ascending Sirens", "Sustain a Comfortable Note", "Dynamic Control at Soft Volume", "When to Pause and Seek Vocal Guidance"]),
            ("Reading, Expression & Performance", "peach", ["Read a Simple Vocal Melody", "Solfège: Do Re Mi", "Sing a Major Scale in Tune", "Shape a Phrase with Breath", "Legato and Clear Consonants", "Practice with a Piano Reference", "Harmony and Simple Vocal Parts", "Microphone Distance and Dynamics", "Warm Up for a Short Performance", "Reflect on a Practice Recording"]),
        ],
    },
}


def build_music_subject(subject_id: str):
    spec = TRACKS[subject_id]
    categories = []
    topics = []
    for group_i, (title, color, names) in enumerate(spec["groups"]):
        category_id = f"unit-{group_i + 1}"
        categories.append({"id": category_id, "title": title, "color": color,
                           "blurb": f"A guided {spec['label']} learning path: concepts, focused practice, and musical application."})
        for item_i, name in enumerate(names):
            number = group_i * 10 + item_i + 1
            level = "basic" if number <= 18 else "intermediate" if number <= 38 else "advanced"
            explanation = (f"{name} is part of learning {spec['label']}. Work on one clear musical goal at a time, notice what you hear and feel, "
                           "and connect the technique to a short piece of music. Relaxed, accurate repetitions build a more dependable skill than rushing.")
            if subject_id == "voice":
                voice_explanations = {
                    "Chest Voice: Sensation and Sound": "Chest voice commonly describes a lower or speech-like register with a fuller sensation of vibration. The feeling varies by singer; it is not sound literally coming from the chest. Try a gentle speaking pitch, then sustain it comfortably without pressing.",
                    "Head Voice: Sensation and Sound": "Head voice commonly describes a lighter upper register with a sensation of resonance around the head or face. The feeling varies by singer. Explore a soft, easy note above your speaking range; do not push for loudness or high notes.",
                    "Chest Voice and Head Voice Compared": "Chest and head voice are useful names for different register sensations and coordination. They describe how the voice is being coordinated, not two separate instruments. Compare easy notes in each range and avoid forcing a transition.",
                    "Mixed Voice: A Coordinated Transition": "Mixed voice is a teaching term for coordinating register qualities through a transition. There is no single mix that sounds the same for everyone. Work softly across a small comfortable range and get individual feedback from a qualified voice teacher.",
                    "Passaggio: Moving Between Registers": "Passaggio refers to transition areas where singers often adjust coordination as pitch rises or falls. Its location varies. Use gentle slides and vowels rather than pushing chest voice upward; stop if the throat feels strained.",
                    "Falsetto and Head Voice: A Careful Comparison": "Falsetto and head voice labels are used differently across traditions and voice types. They can refer to distinct or overlapping vocal coordinations. Compare gentle sounds, but use a teacher to identify what you are doing safely.",
                    "When to Pause and Seek Vocal Guidance": "Pause if singing causes pain, persistent hoarseness, or loss of voice. Rest and consult a qualified voice teacher or clinician if symptoms persist. Do not try to solve vocal discomfort by adding pressure or volume.",
                }
                explanation = voice_explanations.get(name, explanation)
            exercise = f"Practice {name.lower()} slowly for a few minutes. Keep the sound even, pause when tension appears, and repeat it in a short musical phrase."
            q = f"How should a beginner practice {name.lower()}?"
            a = f"Start at a comfortable tempo with a small example. Listen for accuracy and steady timing, keep the body relaxed, and increase difficulty only when the sound stays controlled."
            topics.append(topic(
                f"{subject_id}-{number:02d}", name, category_id, level, spec["prefix"],
                f"Understand and practice {name.lower()}.", spec["analogy"], explanation,
                [f"Use {name.lower()} while learning songs and exercises.", "Build coordination, listening, and confident practice habits."],
                [f"Name the musical goal in {name.lower()}.", "Practice slowly, listen closely, and check for comfort and consistency."],
                [ex("Focused practice", level, "A short exercise to try at your instrument.", "text", exercise, runnable=False)],
                [exercise, "Then try the same idea in a short song or musical phrase."],
                ["Do not increase speed or force when accuracy or comfort is dropping; simplify the passage and rebuild it."],
                [qa(level, q, a)], [],
                chain(("Listen", "sound + pulse", "Hear the goal", f"Listen for the result you want from {name.lower()}."),
                      ("Practice", "small example", "Repeat with control", exercise),
                      ("Apply", "short phrase", "Make it musical", "Use the skill in context and reflect on what changed.")),
            ))
    scenarios = [{"level": "basic", "topic": topics[0]["id"],
                  "q": f"A learner gets tense while practicing {topics[0]['title'].lower()}. What should they change first?",
                  "a": "Slow down, reduce the passage to a comfortable size, and check posture and relaxed movement before adding speed."}]
    return categories, topics, scenarios
