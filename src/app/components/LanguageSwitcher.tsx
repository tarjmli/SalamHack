type ButtonProps = {
  text: string;
  onClick: () => void;
};

const Button = ({ text, onClick }: ButtonProps) => {
  return (
    <button onClick={onClick} className="p-2 bg-blue-500 text-white rounded">
      {text}
    </button>
  );
};

export default Button;
