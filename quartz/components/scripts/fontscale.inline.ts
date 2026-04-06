const STORAGE_KEY = "font-scale-index"
const SCALES = [0.9, 1, 1.15, 1.3] as const
const LABELS = ["小", "中", "大", "特大"]

function applyScale(index: number) {
  const clamped = ((index % SCALES.length) + SCALES.length) % SCALES.length
  const scale = SCALES[clamped]
  document.documentElement.style.setProperty("--font-scale", String(scale))
  localStorage.setItem(STORAGE_KEY, String(clamped))

  for (const el of document.getElementsByClassName("fontscale-level")) {
    el.textContent = LABELS[clamped]
  }
}

document.addEventListener("nav", () => {
  const stored = Number.parseInt(localStorage.getItem(STORAGE_KEY) ?? "", 10)
  const initialIndex = Number.isFinite(stored) ? stored : 1
  applyScale(initialIndex)

  const handleClick = () => {
    const current = Number.parseInt(localStorage.getItem(STORAGE_KEY) ?? String(initialIndex), 10)
    applyScale((Number.isFinite(current) ? current : initialIndex) + 1)
  }

  for (const btn of document.getElementsByClassName("fontscale")) {
    btn.addEventListener("click", handleClick)
    window.addCleanup(() => btn.removeEventListener("click", handleClick))
  }
})

