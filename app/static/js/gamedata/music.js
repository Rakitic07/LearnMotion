export const WORDS = [
  { answer: "RHYTHM", term: "Rhythm", clue: "Pattern of sounds and silences in time" },
  { answer: "MELODY", term: "Melody", clue: "A sequence of pitches heard as a tune" },
  { answer: "TEMPO", term: "Tempo", clue: "How fast or slow the pulse moves" },
  { answer: "PULSE", term: "Pulse", clue: "The steady beat you can tap along with" },
  { answer: "SCALE", term: "Scale", clue: "Notes arranged in a pitch pattern" },
  { answer: "CHORD", term: "Chord", clue: "Several pitches sounding together" },
  { answer: "OCTAVE", term: "Octave", clue: "The interval between matching pitch names" },
  { answer: "TIMBRE", term: "Timbre", clue: "The tone color that distinguishes sounds" },
  { answer: "BAR", term: "Bar", clue: "A group of beats shown between bar lines" },
  { answer: "REST", term: "Rest", clue: "A written duration of silence" },
];
export const RUSH = [
  { task: "A steady underlying beat", answer: "Pulse", wrong: ["Timbre", "Harmony", "Cadence"] },
  { task: "How fast the beat moves", answer: "Tempo", wrong: ["Dynamics", "Texture", "Register"] },
  { task: "Several notes sounding together", answer: "Chord", wrong: ["Bar", "Rest", "Staff"] },
];
export const BUGS = [];
export const META = { rushLabel: "Music Rush", rushIntro: "Choose the musical idea that matches each clue.", bugLabel: "Listening Challenge", bugNoun: "match" };
