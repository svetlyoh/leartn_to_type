import { FINGER_MAP } from "../../generated/finger-map.generated";
export function HandGuide({
  target,
  show,
  reduceMotion,
  onHide,
}: {
  target: string;
  show: boolean;
  reduceMotion: boolean;
  onHide: () => void;
}) {
  if (!show) return null;
  const key = target.toLowerCase();
  const info = FINGER_MAP.keys.find((item) => item.key === key);
  const label = target === " " ? "space" : target.toUpperCase();
  return (
    <div className={`hand-guide ${reduceMotion ? "still" : ""}`} role="status">
      <div className="guide-head">
        <span>
          <span aria-hidden="true">⌁</span> Home anchors F / J ·{" "}
          <strong>
            {info ? `${info.hand} ${info.finger}` : "assigned finger"}
          </strong>{" "}
          for <strong>{label}</strong>
          {info && info.home !== key
            ? ` · ${info.home.toUpperCase()} → ${label} → ${info.home.toUpperCase()}`
            : ""}
        </span>
        <button type="button" className="quiet" aria-label="Hide hands" aria-keyshortcuts="Space+Shift+{" title="Hide hands · Space + Shift + {" onClick={onHide}>
          Hide hands <kbd aria-hidden="true">Space + Shift + {"{"}</kbd>
        </button>
      </div>
    </div>
  );
}
