import "./BaseButton.css";

export function BaseButton(props) {
  return (
    <button className="base-button-next" {...props}>
      {props.children ? props.children : "Next"}
    </button>
  );
}
