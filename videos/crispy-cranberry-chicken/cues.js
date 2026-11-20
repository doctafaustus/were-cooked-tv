// Chef Chub's moves for "Timeline 2 - Ziggy cut" (times in seconds on voice.mp3 = the timeline).
// shows: when he's on screen. He pops up from the bottom edge at `in` and ducks back down by `out`.
//        side L / R = bottom-left / bottom-right corner, C = centre. size = how big (1 = his full
//        height fills the frame); he's framed chest-up. Bottom-left is preferred: TikTok's own
//        buttons sit down the right side.
// looks: he glances at a spot in the frame (x, y from 0..1, top-left origin) for `dur` seconds.
// acts:  wave, kiss, pan, suspicious, surprised, shake, shrug, proud, laugh, point (point aims at the frame centre).
//        kiss takes sparkle: false to skip the sparkle burst (it only happens once in the video).
// He's off screen for the logo, the store pickups, the receipt notes and the busiest shots.
window.CHUB_CUES = {
  shows: [
    { in: -0.6, out: 2.62, side: "L", size: 0.62 },   // already up at frame 0: "A forty-dollar restaurant plate?"
    { in: 4.35, out: 7.20, side: "L", size: 0.56 },   // "dinner for four... under ten bucks", grocery run
    { in: 18.95, out: 23.62, side: "L", size: 0.60 }, // the whole chicken-cutting stretch: "We'll break the leg quarters... costs way more"
    { in: 25.35, out: 30.45, side: "L", size: 0.60 }, // sear ... gorgeous, glaze
    { in: 33.30, out: 38.40, side: "L", size: 0.60 }, // pan sauce, beans, "silkier than my fur"
    { in: 39.30, out: 47.35, side: "L", size: 0.58 }, // plating, "fancy now", "four restaurant plates"
    { in: 47.62, out: 52.58, side: "C", size: 0.70 }  // "Follow for more..." + laugh
  ],
  looks: [
    { t: 0.90, dur: 0.9, x: 0.60, y: 0.45 },   // side-eyes the plate on "restaurant"
    { t: 5.30, dur: 1.0, x: 0.60, y: 0.45 },
    { t: 19.10, dur: 0.7, x: 0.55, y: 0.45 },
    { t: 20.30, dur: 1.2, x: 0.60, y: 0.60 },   // watches the knife cut through the joint
    { t: 25.60, dur: 1.3, x: 0.60, y: 0.40 },
    { t: 29.00, dur: 1.3, x: 0.60, y: 0.45 },
    { t: 33.45, dur: 1.1, x: 0.60, y: 0.45 },
    { t: 35.60, dur: 1.4, x: 0.60, y: 0.40 },
    { t: 39.40, dur: 1.5, x: 0.55, y: 0.45 },
    { t: 41.40, dur: 1.1, x: 0.55, y: 0.45 },
    { t: 44.80, dur: 0.9, x: 0.60, y: 0.40 },
    { t: 48.90, dur: 0.9, x: 0.50, y: 0.40 }
  ],
  acts: [
    { t: 0.20, act: "suspicious" },             // "A forty-dollar restaurant..."
    { t: 1.85, act: "surprised" },              // "...plate?!"
    { t: 4.85, act: "point" },                  // "for under ten bucks"
    { t: 22.45, act: "shrug" },                 // "costs way more"
    { t: 27.55, act: "kiss", sparkle: false },  // "gorgeous"
    { t: 30.00, act: "point" },                 // "sticky cranberry"
    { t: 37.20, act: "proud" },                 // "silkier than my fur"
    { t: 40.10, act: "point" },                 // "chicken on top"
    { t: 43.20, act: "kiss" },                  // "we're fancy now" (the one sparkle)
    { t: 46.00, act: "proud" },                 // "under ten bucks"
    { t: 47.80, act: "wave" },                  // "Follow for more"
    { t: 49.70, act: "shake" },                 // "no, you can't have my drumstick"
    { t: 51.35, act: "laugh" }                  // the laugh
  ]
};
