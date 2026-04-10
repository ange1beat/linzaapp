/**
 * Переходы Motion: короче и сильнее демпфирование — меньше «пружины» и лагов на слабых GPU.
 * Уважение prefers-reduced-motion задаётся в MotionConfig (user).
 */
export const springLayout = {
  type: 'spring',
  stiffness: 520,
  damping: 42,
  mass: 0.75,
}

export const springTap = {
  type: 'spring',
  stiffness: 560,
  damping: 38,
}

/** Только лёгкий сдвиг по Y — меньше работы композитора, чем у крупных смещений. */
export const pageEnter = {
  opacity: 0,
  y: 5,
}

export const pageActive = {
  opacity: 1,
  y: 0,
}

export const pageExit = {
  opacity: 0,
  y: -3,
}
