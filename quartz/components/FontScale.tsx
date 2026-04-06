import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
// @ts-ignore
import script from "./scripts/fontscale.inline"
import styles from "./styles/fontscale.scss"
import { classNames } from "../util/lang"

const FontScale: QuartzComponent = ({ displayClass }: QuartzComponentProps) => {
  return (
    <button
      class={classNames(displayClass, "fontscale")}
      type="button"
      aria-label="调整正文字号"
      title="调整正文字号"
    >
      <span class="fontscale-icon">A</span>
      <span class="fontscale-level" aria-hidden="true"></span>
    </button>
  )
}

FontScale.beforeDOMLoaded = script
FontScale.css = styles

export default (() => FontScale) satisfies QuartzComponentConstructor

